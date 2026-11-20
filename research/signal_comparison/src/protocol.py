"""PRE-REGISTERED PROTOCOL - comparison of three signal-generation approaches on BTCUSDm and UKOILm.

Written on 2026-11-09 BEFORE any strategy result of this project existed. Paper research only; no orders.
The human-readable version is ../PROTOCOL.md; this file is what the code actually uses.

QUESTION   Which approach gives the most RELIABLE BUY and SELL recommendations (consistent, statistically
           supported, robust to costs and market regime), not which has the highest historical return.

DATA       Exness public tick archive (ticks.ex2archive.com), symbols BTCUSDm and UKOILm (Standard account
           quotes), every bid/ask quote aggregated to UTC hourly bid and ask candles. Indicators are computed
           on BID candles (what a chart shows). 4H and daily candles are aggregated from the hourly candles on
           UTC boundaries. Hours without quotes stay missing; nothing is interpolated.

APPROACHES (each has a BUY rule and a mirror-image SELL rule; all use closed candles only; the higher
           timeframe value is always the last 4H candle that had closed when the 1H candle closed)
  A1 DONCHIAN_TREND   1H close crosses above the highest high of the previous N bars, and the last closed 4H
                      close is above its EMA(S).                        Textbook: N=20, S=200.
  A2 COMBINED         The existing signal assistant's BUY rule: 4H close above EMA(S) and 4H EMA(F) above EMA(S);
                      a fresh 1H Donchian-N breakout; at least 3 of the four 1H confirmers bullish and none
                      bearish (EMA F/S structure, RSI vs 50, MACD line vs signal, ADX>=20 with +DI vs -DI);
                      1H RSI not above 80 (not below 20 for SELL).
  A3 VOTING           No breakout required. Five votes per timeframe: EMA F/S structure, RSI vs 50, MACD line vs
                      signal, ADX>=20 with +DI vs -DI, close vs the middle of the previous-N-bar Donchian channel.
                      BUY when at least K of the five 1H votes are bullish AND at least 3 of the five 4H votes
                      are bullish AND that combined condition was false on the previous 1H bar (a fresh
                      alignment) AND 1H RSI is not above 80. K is 4 or 5.

PARAMETERS BTC settings are not assumed to suit oil, and textbook settings are not assumed to suit either.
           The only free dimension is a TIME SCALE s applied to every look-back at once:
               s = 0.5 (fast), 1 (textbook), 2 (slow).
           A1 and A2 therefore have 3 candidates each, A3 has 6 (3 scales x K in {4, 5}), per asset and direction.
           Thresholds (RSI 50/80/20, ADX 20) and the exit rule are never tuned.

EXECUTION  Signal on a closed 1H candle -> enter at the first quote of the next available hour:
           BUY at the ASK, SELL at the BID. One position at a time per strategy. Risk unit R = 2 x ATR14 (1H bid).
           Long stops trigger on the BID low, short stops on the ASK high; a gap through the stop fills at the
           hour's opening quote. Two exits are reported for every strategy:
  TRAIL    initial stop 2 x ATR14; after every 1H close, stop = max(stop, best close since entry - 3 x ATR14).
           No target. (The exit of the validated Donchian study.) Shows the trend-following payoff.
  SYM      stop 2 x ATR14 and target 2 x ATR14 (+1R / -1R), exit at the close after 48 hourly bars if neither
           is hit; if both are touched in one bar the stop is assumed first. Without an edge the win rate of
           this exit is about 50% before costs, so it measures directional reliability.

COSTS      The bid/ask spread is REAL: it is inside the fills above (buy at ask, sell at bid).
  spread   measured spread only.
  primary  measured spread + 0.02% of price per round trip for slippage (HYPOTHETICAL).
  stress   measured spread + 0.05% slippage per round trip + 0.02% of price per calendar day held as
           financing/swap (HYPOTHETICAL; Exness swaps and any commission are unverified).
           Standard ("m") accounts are assumed commission-free.
  today    DIAGNOSTIC ONLY, never used by the selection or pass rules. Measured spreads shrank a lot over the
           years (BTCUSDm from about 0.21% in 2019 to about 0.02% in 2026), so historical results carry
           historical costs. This scenario replaces each trade's actual entry spread with the median opening
           spread of the 12 months before the final test, plus the primary slippage. It is an approximation
           (stop trigger levels are not recomputed) added before any result was seen.

REGIMES    Causal label at entry from the last completed UTC day: bull = daily close above daily EMA200 and
           EMA200 higher than 20 days earlier; bear = below and lower; otherwise sideways.

TESTING    Chronological. Three zones per asset:
  warm-up      indicators and the daily EMA200 settle; no trades counted.
  development  walk-forward: at the start of every half-year fold each strategy picks its parameter candidate
               using ONLY trades entered before the fold (from development start), then trades the fold.
               The stitched fold results are out-of-sample.
  final test   2025-07-01 onward. Never read by stage 1 (the loader truncates the data). The candidate is
               picked once from the whole development zone, locked with a SHA-256, and evaluated ONCE.
  Selection rule (reliability, not return): highest t-statistic of primary-cost R among candidates with at
               least 30 prior trades; if none qualifies, the textbook candidate. Ties go to the textbook one.
  Every strategy is ALSO reported with the textbook candidate and no selection at all.

STATISTICS per strategy and period: trades, win rate, profit factor, expectancy in R, t-statistic and one-sided
           p-value (mean R > 0), bootstrap 95% CI of the expectancy, maximum drawdown (R and % at 0.5% risk),
           longest losing streak, share of positive folds, and a RANDOM-ENTRY benchmark: the same exit and
           direction entered at random hours of the same period (1,000 runs); p_random is the share of random
           runs whose expectancy is at least the strategy's. Holm correction across the 24 selected strategies.

RELIABLE   (pre-registered pass rule, per asset x approach x direction x exit, primary cost)
  walk-forward: >= 50 trades, expectancy > 0 with t >= 2.0, profit factor >= 1.2, positive expectancy in
                >= 60% of folds that have trades, expectancy > 0 at stress cost, p_random <= 0.05;
  final test:   >= 10 trades, expectancy > 0, profit factor >= 1.1.
  Passers are ranked by walk-forward t-statistic, then fold consistency - never by return.
  If nothing passes for an asset and direction, the finding is: NO RELIABLE RECOMMENDATION.

DISCLOSURE BTC history has been examined before: the earlier breakout study evaluated A1 (long and short) on
           Binance data including a 2025-07 -> 2026-11 holdout, and the signal assistant's replay described
           forward returns after A2 signals over 2018-2026. No parameter was fitted in either. A3, the Exness
           BTCUSDm series, and all UKOILm data are new to this project.
"""
import calendar


def ts(y, m, d=1):
    return calendar.timegm((y, m, d, 0, 0, 0))


ASSETS = {
    # warm-up ends / development starts ; first walk-forward fold ; final test start
    "BTCUSDm": {"file": "BTCUSDm_1h.csv.gz", "dev_start": ts(2019, 1), "first_fold": ts(2020, 1), "final_start": ts(2025, 7)},
    "UKOILm": {"file": "UKOILm_1h.csv.gz", "dev_start": ts(2021, 1), "first_fold": ts(2022, 1), "final_start": ts(2025, 7)},
}
DATA_END = ts(2026, 11)          # last full month in the archive when the study was run: 2026-10

APPROACHES = ("A1_DONCHIAN_TREND", "A2_COMBINED", "A3_VOTING")
DIRECTIONS = {"BUY": 1, "SELL": -1}
EXITS = ("TRAIL", "SYM")
SCALES = (0.5, 1.0, 2.0)
TEXTBOOK = {"donchian": 20, "ema_fast": 50, "ema_slow": 200, "rsi": 14, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9, "adx": 14}
VOTE_K = (4, 5)
TEXTBOOK_K = 4

RSI_MID, RSI_HIGH, RSI_LOW, ADX_MIN = 50.0, 80.0, 20.0, 20.0
MIN_CONFIRMERS = 3
HTF_MIN_VOTES = 3

ATR_PERIOD = 14
STOP_ATR, TRAIL_ATR, SYM_TARGET_ATR, SYM_MAX_BARS = 2.0, 3.0, 2.0, 48

COSTS = {
    "spread": {"slippage": 0.0, "swap_per_day": 0.0},
    "primary": {"slippage": 0.0002, "swap_per_day": 0.0},
    "stress": {"slippage": 0.0005, "swap_per_day": 0.0002},
}
PRIMARY_COST = "primary"
TODAY_COST = "today"                      # diagnostic scenario, see docstring
TODAY_SPREAD_WINDOW_DAYS = 365
RISK_PER_TRADE = 0.005

SELECTION_MIN_TRADES = 30
RANDOM_RUNS = 1000
BOOTSTRAP_RUNS = 2000
SEED = 20261109

PASS = {"wf_min_trades": 50, "wf_min_t": 2.0, "wf_min_pf": 1.2, "wf_min_pos_fold_share": 0.6, "wf_max_p_random": 0.05,
            "final_min_trades": 10, "final_min_pf": 1.1}


def scaled(scale):
    """Indicator look-backs for a time scale (rounded, minimum 2)."""
    return {k: max(2, round(v * scale)) for k, v in TEXTBOOK.items()}


def candidates(approach):
    """Parameter candidates for an approach: list of dicts with 'scale' (and 'k' for A3)."""
    if approach == "A3_VOTING":
        return [{"scale": s, "k": k} for s in SCALES for k in VOTE_K]
    return [{"scale": s} for s in SCALES]


def textbook_candidate(approach):
    return {"scale": 1.0, "k": TEXTBOOK_K} if approach == "A3_VOTING" else {"scale": 1.0}


def folds(asset):
    """Half-year walk-forward folds from first_fold up to the final test start: (name, start, end)."""
    a = ASSETS[asset]
    out, y, h = [], None, None
    t = a["first_fold"]
    import time
    while t < a["final_start"]:
        g = time.gmtime(t)
        y, h = g.tm_year, 1 if g.tm_mon == 1 else 2
        end = ts(y, 7) if h == 1 else ts(y + 1, 1)
        out.append((f"{y}H{h}", t, min(end, a["final_start"])))
        t = end
    return out
