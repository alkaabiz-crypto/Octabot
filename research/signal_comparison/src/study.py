"""Shared machinery for the two stages: context building, candidate trades, selection and evaluation."""
import csv
import os
import statistics
import time
import zlib

import engine
import marketdata as md
import protocol as P
import signals as sg
import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
REPORTS_DIR = os.path.join(ROOT, "reports")
LOGS_DIR = os.path.join(ROOT, "logs")
REGIMES = ("bull", "bear", "sideways")


def fmt(t):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))


def cand_key(cand):
    return f"s{cand['scale']:g}" + (f"_k{cand['k']}" if "k" in cand else "")


def strategy_key(approach, direction_name, exit_rule):
    return f"{approach}|{direction_name}|{exit_rule}"


class Context:
    """Everything derived from one asset's candles. ``end_before`` hard-limits what is loaded."""

    def __init__(self, asset, end_before):
        cfg = P.ASSETS[asset]
        self.asset, self.cfg, self.end_before = asset, cfg, end_before
        self.market = md.load_market(asset, os.path.join(DATA_DIR, cfg["file"]), end_before=end_before)
        self.lab = sg.SignalLab(self.market)
        self.regimes = engine.Regimes(self.market.h1)
        self.outcomes = {(d, x): engine.Outcomes(self.market, d, x) for d in P.DIRECTIONS.values() for x in P.EXITS}
        self.dev_index = engine.index_at_or_after(self.market.h1, cfg["dev_start"])
        self.today_spread = engine.today_spread_fraction(self.market, cfg["final_start"])
        self._trades = {}

    def trades(self, approach, direction_name, exit_rule, cand):
        """All trades of one candidate from development start to the end of the loaded data."""
        key = (approach, direction_name, exit_rule, cand_key(cand))
        if key not in self._trades:
            d = P.DIRECTIONS[direction_name]
            sig = self.lab.signals(approach, d, cand)
            self._trades[key] = engine.trades_from_signals(self.outcomes[(d, exit_rule)], sig, self.regimes, self.dev_index)
        return self._trades[key]

    def r(self, trade, cost=P.PRIMARY_COST):
        return trade.r_net(cost, self.today_spread)


def between(trades, t0, t1):
    return [t for t in trades if t0 <= t.entry_time < t1]


def select_candidate(ctx, approach, direction_name, exit_rule, before_time):
    """Pre-registered rule: highest primary-cost t-statistic among candidates with enough prior trades."""
    best, best_t = P.textbook_candidate(approach), None
    table = {}
    for cand in P.candidates(approach):
        prior = between(ctx.trades(approach, direction_name, exit_rule, cand), ctx.cfg["dev_start"], before_time)
        # only trades already CLOSED before the decision time are known
        prior = [t for t in prior if t.exit_time <= before_time]
        s = stats.summarize([ctx.r(t) for t in prior], with_ci=False)
        table[cand_key(cand)] = dict(trades=s["trades"], t_stat=s.get("t_stat"), expectancy_r=s.get("expectancy_r"))
        if s["trades"] >= P.SELECTION_MIN_TRADES and s.get("t_stat") is not None:
            is_textbook = cand == P.textbook_candidate(approach)
            if best_t is None or s["t_stat"] > best_t or (s["t_stat"] == best_t and is_textbook):
                best, best_t = cand, s["t_stat"]
    return best, table


def evaluate(ctx, trades, direction_name, exit_rule, t0, t1, label):
    """Full metric set for a list of trades entered in [t0, t1)."""
    rs = [ctx.r(t) for t in trades]
    m = stats.summarize(rs)
    m["period"] = [fmt(t0), fmt(t1)]
    if not trades:
        return m
    for cost in ("spread", "stress", P.TODAY_COST):
        m[f"expectancy_{cost}"] = statistics.mean(ctx.r(t, cost) for t in trades)
    m["avg_hold_hours"] = statistics.mean(t.hold_hours for t in trades)
    m["avg_cost_r_primary"] = statistics.mean((t.entry_spread + P.COSTS[P.PRIMARY_COST]["slippage"] * t.entry) / t.risk for t in trades)
    reasons = {}
    for t in trades:
        reasons[t.reason] = reasons.get(t.reason, 0) + 1
    m["exit_reasons"] = reasons
    m["regimes"] = {}
    for reg in REGIMES:
        rr = [ctx.r(t) for t in trades if t.regime == reg]
        s = stats.summarize(rr, with_ci=False)
        m["regimes"][reg] = {k: s.get(k) for k in ("trades", "win_rate_pct", "profit_factor", "expectancy_r", "t_stat", "p_one_sided", "max_drawdown_r")}
    d = P.DIRECTIONS[direction_name]
    o = ctx.outcomes[(d, exit_rule)]
    b = ctx.market.h1
    i0, i1 = engine.index_at_or_after(b, t0), engine.index_at_or_after(b, t1)
    seed = zlib.crc32(f"{ctx.asset}|{label}|{direction_name}|{exit_rule}|{P.SEED}".encode())
    rnd = engine.random_expectancies(o, i0, i1, len(trades), P.PRIMARY_COST, P.RANDOM_RUNS, seed)
    m["random_entry_mean_r"] = statistics.mean(rnd) if rnd else None
    m["p_random"] = stats.p_random(m["expectancy_r"], rnd)
    return m


def period_context(ctx, t0, t1):
    """Buy-and-hold change and regime mix of a period (context for the tables, not a strategy)."""
    b = ctx.market.h1
    i0, i1 = engine.index_at_or_after(b, t0), engine.index_at_or_after(b, t1) - 1
    mix = {r: 0 for r in (*REGIMES, "undefined")}
    for i in range(i0, i1 + 1, 24):
        mix[ctx.regimes.at(b.t[i])] += 1
    total = sum(mix.values()) or 1
    return dict(first_bar=fmt(b.t[i0]), last_bar=fmt(b.t[i1]), bars=i1 - i0 + 1, buy_and_hold_pct=(b.c[i1] / b.o[i0] - 1) * 100,
                regime_share_pct={k: round(v / total * 100, 1) for k, v in mix.items()})


def write_trades(path, ctx, trades, extra=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entry_utc", "exit_utc", "direction", "entry", "risk_1R", "r_spread", "r_primary", "r_stress", "exit_reason",
                    "regime", "hold_hours", "entry_spread", "candidate"])
        for i, t in enumerate(trades):
            w.writerow([fmt(t.entry_time), fmt(t.exit_time), "BUY" if t.direction > 0 else "SELL", round(t.entry, 4), round(t.risk, 4),
                        round(t.r_spread, 4), round(ctx.r(t), 4), round(ctx.r(t, "stress"), 4), t.reason, t.regime,
                        round(t.hold_hours, 1), round(t.entry_spread, 4), extra[i] if extra else ""])
