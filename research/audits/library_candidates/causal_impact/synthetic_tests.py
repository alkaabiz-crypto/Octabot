"""Deterministic synthetic tests of the three execution engines (scratch only; no repository file is touched).
  FROZEN : verify_minute.b9 / d4 imported UNCHANGED from the read-only extract of the frozen library
  FWD    : library_forward/forward.py imported UNCHANGED (hash-checked copy); only its network fetch is replaced
  SIM    : the independent simulator in sim.py (wall clock = forward model, candle clock = backtest counting)
usage: python3 -I synthetic_tests.py <extract_dir> <forward_copy_dir> <out_json>
"""
import hashlib, json, os, sys, tempfile, time
import numpy as np

EXT, FWDDIR, OUT = sys.argv[1:4]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sim as S  # noqa: E402
os.environ.setdefault("BARS_DIR", "/nonexistent"); os.environ.setdefault("BIN_DIR", "/nonexistent")
sys.path.insert(0, os.path.join(EXT, "research", "theory_library")); import verify_minute as V  # noqa: E402
sys.path.insert(0, FWDDIR); import forward as F  # noqa: E402
FROZEN_FWD_SHA = hashlib.sha256(open(os.path.join(EXT, "research", "library_forward", "forward.py"), "rb").read()).hexdigest()
assert hashlib.sha256(open(os.path.join(FWDDIR, "forward.py"), "rb").read()).hexdigest() == FROZEN_FWD_SHA
T0 = 1736121600 // 60          # 2025-01-06 00:00 UTC in minutes (a Monday, hour aligned)
RES = {"frozen_forward_sha256": FROZEN_FWD_SHA, "tests": []}


def record(name, ok, detail):
    RES["tests"].append(dict(test=name, passed=bool(ok), detail=detail)); print(("PASS " if ok else "FAIL ") + name, json.dumps(detail, default=str)[:400], flush=True)


# ---------------------------------------------------------------- engine wrappers
def run_fwd(m, o, h, l, c, cfg, sigtab=None, chunks=None):
    """Run the frozen forward.py over minute arrays. chunks=None: one call; else a list of 'now' minutes (hourly cron)."""
    ms = m * 60000; M1 = [(int(a), float(b), float(d), float(e), float(f)) for a, b, d, e, f in zip(ms, o, h, l, c)]
    Hc = S.hourly(m, o, h, l, c); H1 = [(int(Hc["hr"][k] * 3600000), float(Hc["o"][k]), float(Hc["h"][k]), float(Hc["l"][k]), float(Hc["c"][k])) for k in range(len(Hc["s"]))]
    now = {"t": 10 ** 18}
    F.candles = lambda coin, iv, start, source="hyperliquid": ([x for x in M1 if start <= x[0] and x[0] + 60000 <= now["t"]] if iv == "1m"
                                                              else [x for x in H1 if x[0] + 3600000 <= now["t"]])
    orig_signal = F.signal
    if sigtab is not None: F.signal = lambda kind, hc: sigtab.get(hc[-1][0] // 60000)
    d = tempfile.mkdtemp(); F.HERE = d; name = "T"
    json.dump(dict(cursor=int(ms[0]) - 60000, pending=[], pos=None, next_check=0, trades=0, net1=0.0, net2=0.0, bp2=0.0, wins2=0, started="test"),
              open(os.path.join(d, f"state_{name}.json"), "w"))
    rows = []
    try:
        for t in (chunks or [10 ** 18 // 60000]):
            now["t"] = t * 60000; r, _ = F.run(name, cfg); rows += r
    finally:
        F.signal = orig_signal
    tomin = lambda s: int(time.mktime(time.strptime(s, "%Y-%m-%d %H:%M")) - time.timezone) // 60
    out = [dict(side=1 if r["side"] == "BUY" else -1, ft=tomin(r["fill_utc"]), xt=tomin(r["exit_utc"]), made=tomin(r["signal_close_utc"]) * 60000,
                entry=r["entry"], exit=r["exit"], reason=r["reason"]) for r in rows]
    st = json.load(open(os.path.join(d, f"state_{name}.json")))
    ledger = open(os.path.join(d, f"ledger_{name}.csv")).read().splitlines() if os.path.exists(os.path.join(d, f"ledger_{name}.csv")) else []
    return out, st, ledger


def run_frozen(m, o, h, l, c, kind):
    M = dict(m=m, o=o, h=h, l=l, c=c, hs=o * V.FEE, pen=o * 1e-4)
    hr = m // 60; st = np.flatnonzero(np.r_[True, hr[1:] != hr[:-1]]); en = np.r_[st[1:], len(m)]
    Hc = dict(o=o[st], h=np.maximum.reduceat(h, st), l=np.minimum.reduceat(l, st), c=c[en - 1], s=st, e=en, hr=hr[st])
    tr = V.b9(M, Hc) if kind == "fib" else V.d4(M, Hc)
    return [dict(side=s, f=f, x=x, ft=int(m[f]), xt=int(m[x]), entry=float(pe), exit=float(px)) for s, f, x, pe, px in tr]


PEN_FEE = lambda px, q: px * 1e-4                       # ETH_FIB forward rule: 1 bp of the limit price
CFG_FEE = lambda kind: dict(coin="X", source="binance", fee=0.0005, pen_bp=1.0, unit=1, unit_name="u", kind=kind)
CFG_SPR = lambda kind, sp: dict(coin="X", spread=sp, unit=1, unit_name="u", kind=kind)
REASON = {"stop (gap)": "stop_gap", "stop": "stop", "target": "target", "time (20 candles)": "time"}


def same_trades(a, b, tol=6e-5):
    if len(a) != len(b): return False, f"count {len(a)} vs {len(b)}"
    for i, (x, y) in enumerate(zip(a, b)):
        if (x["side"], x["ft"], x["xt"]) != (y["side"], y["ft"], y["xt"]) or abs(x["entry"] - y["entry"]) > tol * max(1, abs(x["entry"])) or abs(x["exit"] - y["exit"]) > tol * max(1, abs(x["exit"])):
            return False, f"trade {i}: {x} vs {y}"
        if "reason" in x and "reason" in y and REASON.get(y["reason"], y["reason"]) != x["reason"]: return False, f"reason {i}: {x['reason']} vs {y['reason']}"
    return True, f"{len(a)} trades identical"


# ---------------------------------------------------------------- crafted scenarios (signals injected at chosen hours)
def flat_minutes(hours, px=100.0):
    n = hours * 60; m = T0 + np.arange(n); o = np.full(n, px); return m, o.copy(), o.copy(), o.copy(), o.copy()


def poke(arrs, minute, lo=None, hi=None, op=None, cl=None):
    m, o, h, l, c = arrs; q = minute
    if op is not None: o[q] = op
    if lo is not None: l[q] = min(l[q], lo)
    if hi is not None: h[q] = max(h[q], hi)
    if cl is not None: c[q] = cl
    h[q] = max(h[q], o[q], c[q]); l[q] = min(l[q], o[q], c[q])


def crafted(name, arrs, sigs, expect, note):
    """sigs: {signal_candle_index: (side, lim, stop, tp)} -> order created at the open of the next hour."""
    m, o, h, l, c = arrs
    sim_tr, _ = S.simulate(m, o, h, l, c, "fvg", PEN_FEE, clock="wall", sigfun=lambda Hc, k: sigs.get(k))
    tab = {int(T0 + k * 60): v for k, v in sigs.items()}
    fwd_tr, st, _ = run_fwd(m, o, h, l, c, CFG_FEE("fvg"), sigtab=tab)
    got_sim = [(t["side"], t["ft"] - T0, round(t["entry"], 4), t["reason"]) for t in sim_tr]
    got_fwd = [(t["side"], t["ft"] - T0, round(t["entry"], 4), REASON[t["reason"]]) for t in fwd_tr]
    ok = got_sim == got_fwd == expect
    record(name, ok, dict(note=note, expected=expect, sim=got_sim, forward_py=got_fwd))


def crafted_suite():
    P = 100.0
    # C1: older order (lim 98) still unfilled when a newer signal (lim 99.5) appears; the dip reaches 99.4 first (newer fills),
    #     later reaches 97.9 (where the older one would have filled). Causal: the NEWER order is taken at 99.5.
    a = flat_minutes(30, P); sig = {2: (1, 98.0, 96.0, 102.0), 4: (1, 99.5, 96.0, 103.0)}
    poke(a, 6 * 60 + 10, lo=99.4); poke(a, 8 * 60 + 5, lo=97.9)
    crafted("C1 newer order fills first while an older order is pending -> newer taken, older cancelled", a, sig,
            [(1, 6 * 60 + 10, 99.5, "time")], "the frozen backtest's rule would take the OLDER order at 98.0 (it fills later, within its window)")
    # C2: older order fills first after a newer signal appeared -> older taken, newer cancelled
    a = flat_minutes(30, P); sig = {2: (1, 99.5, 96.0, 102.0), 4: (1, 98.0, 96.0, 103.0)}
    poke(a, 6 * 60 + 10, lo=99.4); poke(a, 8 * 60 + 5, lo=97.9)
    crafted("C2 earlier order fills after a later signal appeared -> earlier taken", a, sig, [(1, 6 * 60 + 10, 99.5, "time")], "newer order cancelled at the fill")
    # C3: two pending orders both fill on the same minute -> the OLDEST is taken (even though the newer has the better price)
    a = flat_minutes(30, P); sig = {2: (1, 99.0, 96.0, 102.0), 3: (1, 99.6, 96.0, 103.0)}
    poke(a, 6 * 60 + 1, lo=98.9)
    crafted("C3 two orders fill on the same minute -> oldest wins", a, sig, [(1, 6 * 60 + 1, 99.0, "time")], "oldest-first scan of the pending list")
    # C4: older order expires (10 h) before price reaches it; a newer order exists -> no fill after expiry; newer fills later
    a = flat_minutes(40, P); sig = {2: (1, 98.0, 90.0, 120.0), 8: (1, 97.0, 90.0, 120.0)}
    poke(a, 13 * 60 + 0, lo=97.95)          # minute 13:00 = order 1 expiry (made 03:00 + 10 h): t < expires fails -> not filled
    poke(a, 15 * 60 + 30, lo=96.9)
    crafted("C4 order expires while a newer signal is pending -> expired order never fills", a, sig, [(1, 15 * 60 + 30, 97.0, "time")],
            "first touch of 98 is exactly at the expiry minute (excluded); the newer order fills at 97")
    # C5: gap through the limit: the minute opens below a buy limit -> filled at the OPEN (better than the limit)
    a = flat_minutes(30, P); sig = {2: (1, 99.0, 90.0, 120.0)}
    poke(a, 5 * 60 + 7, op=98.2, lo=98.1, cl=98.3)
    crafted("C5 gap through the limit -> fill at the minute open", a, sig, [(1, 5 * 60 + 7, 98.2, "time")], "e = min(open, limit)")
    # C6: the fill minute also touches the stop and the target -> stop exit on the fill minute; the target is ignored on the fill minute
    a = flat_minutes(30, P); sig = {2: (1, 99.0, 98.5, 99.5)}
    poke(a, 5 * 60 + 7, lo=98.4, hi=99.9)
    crafted("C6 simultaneous fill, stop and target on one minute -> stop", a, sig, [(1, 5 * 60 + 7, 99.0, "stop")], "stop checked from the fill minute, target from the next")
    # C7: position limit: a signal while a position is open is ignored; next check = exit hour + 2 h; pending list cleared on fill
    a = flat_minutes(40, P); sig = {2: (1, 99.0, 98.0, 101.0), 3: (1, 98.5, 97.0, 101.0), 5: (1, 99.0, 98.0, 101.0), 6: (1, 99.0, 98.0, 101.0), 7: (1, 99.0, 98.0, 101.0)}
    poke(a, 3 * 60 + 30, lo=98.9)            # order 1 fills 03:30 (order 2 created 04:00? no: made 04:00 only if flat -> ignored)
    poke(a, 5 * 60 + 15, hi=101.2)           # target 05:15 -> next check 07:00 (signals at candles 5,6 -> creation 06:00,07:00)
    poke(a, 7 * 60 + 20, lo=98.8)            # 07:20: the order created at 07:00 (signal candle 6) fills; candle-5 signal (06:00) was never placed
    crafted("C7 one position at a time; no signal while in a position; next check exit hour + 2 h", a, sig,
            [(1, 3 * 60 + 30, 99.0, "target"), (1, 7 * 60 + 20, 99.0, "time")], "signal at candle 3 ignored (in position), candle 5 skipped (before 07:00)")
    # C8: many pending orders at once (no cap) -> the forward state can hold 6+ orders
    a = flat_minutes(30, P); sig = {k: (1, 99.0 - 0.1 * k, 90.0, 120.0) for k in range(2, 9)}
    poke(a, 9 * 60 + 30, lo=98.15)
    crafted("C8 no cap on pending orders: 7 pending, the oldest whose level is reached fills", a, sig, [(1, 9 * 60 + 30, 98.8, "time")],
            "orders 99.0-0.1k for k=2..8 (98.8..98.2, all alive at 09:30); oldest fillable is k=2 at 98.8")


# ---------------------------------------------------------------- the frozen backtest on the C1 pattern with REAL FVG signals
def frozen_vs_causal_fvg():
    """Hourly path with two genuine bullish FVGs (signal candles 2 and 3). The dip in hour 4 fills the newer (higher) order;
    the deeper dip in hour 5 reaches the older order. Frozen backtest = older order; forward/SIM = newer order."""
    HP = [(100, 101, 99, 100.5), (100.5, 103, 100.5, 102.5), (102.5, 104, 101.5, 103.5), (103.5, 106, 103.4, 105.5),
          (105.5, 105.6, 102.9, 103.2), (103.2, 103.3, 100.8, 101.5)] + [(101.5, 101.6, 101.4, 101.5)] * 30
    m, o, h, l, c = [], [], [], [], []
    for k, (O, Hh, Ll, Cc) in enumerate(HP):            # minute path: open -> low (minute 20) -> high (minute 40) -> close
        for j in range(60):
            px = O + (Ll - O) * j / 20 if j <= 20 else (Ll + (Hh - Ll) * (j - 20) / 20 if j <= 40 else Hh + (Cc - Hh) * (j - 40) / 19)
            m.append(T0 + k * 60 + j); o.append(px); h.append(px); l.append(px); c.append(px)
    m, o, h, l, c = (np.array(x, dtype=float if i else np.int64) for i, x in enumerate((m, o, h, l, c)))
    l[5 * 60 + 20] = 100.8; l[4 * 60 + 20] = 102.9
    fz = run_frozen(m, o, h, l, c, "fvg"); sm, _ = S.simulate(m, o, h, l, c, "fvg", PEN_FEE, clock="wall"); fw, _, _ = run_fwd(m, o, h, l, c, CFG_FEE("fvg"))
    la, _ = S.simulate_lookahead(m, o, h, l, c, "fvg", lambda px, q: o[q] * 1e-4)
    f0 = lambda t: (t["side"], t["ft"] - T0, round(t["entry"], 3))
    detail = dict(frozen=[f0(t) for t in fz], sim_lookahead=[(t["side"], int(m[t["f"]]) - T0, round(t["entry"], 3)) for t in la],
                  sim_causal=[f0(t) for t in sm], forward_py=[f0(t) for t in fw])
    # which order: the older one (limit 101) can only fill in hour 5 (minute >= 300), the newer one (limit 103) fills in hour 4
    detail["reading"] = "entries are below the limits because the minute opens gap through them (fill at the open)"
    ok = detail["frozen"] and 300 <= detail["frozen"][0][1] < 360 and detail["frozen"][0][2] <= 101.0 and 240 <= detail["sim_causal"][0][1] < 300 and 102.0 < detail["sim_causal"][0][2] <= 103.0 and detail["forward_py"] == detail["sim_causal"] and detail["sim_lookahead"] == detail["frozen"]
    record("F1 genuine FVG pair: frozen backtest takes the older (deeper, later-filling) order; forward.py and SIM take the newer one", ok, detail)
    # prefix invariance on this exact path: remove the deeper dip of hour 5 (data AFTER the newer fill at 04:20)
    l2 = l.copy(); h2 = h.copy(); o2 = o.copy(); c2 = c.copy()
    for q in range(5 * 60, len(m)): o2[q] = h2[q] = l2[q] = c2[q] = 103.2
    fz2 = run_frozen(m, o2, h2, l2, c2, "fvg"); sm2, _ = S.simulate(m, o2, h2, l2, c2, "fvg", PEN_FEE, clock="wall")
    pos_at = lambda tr, t: [(x["side"], x["ft"] - T0) for x in tr if x["ft"] <= t]
    T = T0 + 4 * 60 + 59
    record("F2 same path, future after 04:59 changed: is the position held at 04:59 the same?",
           pos_at(fz, T) != pos_at(fz2, T) and pos_at(sm, T) == pos_at(sm2, T),
           dict(frozen_original=pos_at(fz, T), frozen_changed_future=pos_at(fz2, T), sim_original=pos_at(sm, T), sim_changed_future=pos_at(sm2, T),
                meaning="the frozen backtest's position at 04:59 depends on prices after 04:59; the causal simulator's does not"))


# ---------------------------------------------------------------- randomized tests
def walk(seed, days=20, vol=6e-4, jump=0.002):
    r = np.random.default_rng(seed); n = days * 1440; ret = r.normal(0, vol, n) + r.normal(0, 3 * vol, n) * (r.random(n) < 0.01)
    trend = np.repeat(r.normal(0, 4e-4, n // 600 + 1), 600)[:n]; lp = np.log(100) + np.cumsum(ret + trend * 0.2)
    c = np.exp(lp); o = np.r_[100.0, c[:-1]] * np.exp(np.where(r.random(n) < 0.003, r.normal(0, jump, n), 0))   # occasional open gaps
    wig = np.abs(r.normal(0, vol, (2, n))); h = np.maximum(o, c) * np.exp(wig[0]); l = np.minimum(o, c) * np.exp(-wig[1])
    return T0 + np.arange(n, dtype=np.int64), o, h, l, c


def randomized():
    seeds = range(1, 41); agree = {"fib": [0, 0], "fvg": [0, 0]}; spr = [0, 0]; la_eq = {"fib": [0, 0], "fvg": [0, 0]}; viol = {"FROZEN": [0, 0], "SIM_wall": [0, 0], "SIM_candle": [0, 0], "FWD": [0, 0]}
    inv = dict(fill_before_creation=0, fill_after_expiry=0, overlapping_positions=0, exit_before_fill=0, signal_before_next_check=0, max_pending=0, trades=0)
    first_fail = {}
    for sd in seeds:
        m, o, h, l, c = walk(sd)
        for kind in ("fib", "fvg"):
            # (a) SIM wall == frozen forward.py, ETH-style costs
            log = []; sw, _ = S.simulate(m, o, h, l, c, kind, PEN_FEE, clock="wall", log=log); fw, _, _ = run_fwd(m, o, h, l, c, CFG_FEE(kind))
            ok, why = same_trades([dict(t, ft=t["ft"], xt=t["xt"]) for t in sw], fw); agree[kind][0] += ok; agree[kind][1] += 1
            if not ok: first_fail.setdefault(f"sim_vs_fwd_{kind}", (sd, why))
            # (b) SIM look-ahead selection == FROZEN verify_minute (pen and cost per minute as verify_minute)
            fz = run_frozen(m, o, h, l, c, kind); la, _ = S.simulate_lookahead(m, o, h, l, c, kind, lambda px, q: o[q] * 1e-4)
            ok2, why2 = same_trades([dict(t, ft=int(m[t["f"]]), xt=int(m[t["x"]])) for t in la], fz); la_eq[kind][0] += ok2; la_eq[kind][1] += 1
            if not ok2: first_fail.setdefault(f"lookahead_vs_frozen_{kind}", (sd, why2))
            # (c) timeline invariants on the causal simulator
            inv["trades"] += len(sw); pend = 0
            for i, t in enumerate(sw):
                if t["ft"] * 60000 < t["made"] * 60000 // 60000 * 1: pass
                if t["ft"] < t["made"]: inv["fill_before_creation"] += 1
                if t["ft"] >= t["made"] + 600: inv["fill_after_expiry"] += 1
                if t["xt"] < t["ft"]: inv["exit_before_fill"] += 1
                if i and t["ft"] <= sw[i - 1]["xt"]: inv["overlapping_positions"] += 1
                if i and t["made"] < sw[i - 1]["xt"] // 60 * 60 + 120: inv["signal_before_next_check"] += 1
            for ev in log:
                if ev[0] == "create": pend += 1
                elif ev[0] in ("fill",): pend = 0
                elif ev[0] == "expire": pend -= 1
                inv["max_pending"] = max(inv["max_pending"], pend)
            # (d) prefix invariance: replace everything after a cut by an unrelated path; decisions up to the cut must not change
            for cut_frac in (0.3, 0.5, 0.7):
                q0 = int(len(m) * cut_frac) + 17            # mid-hour cut
                m2, o2, h2, l2, c2 = walk(sd + 1000)
                sc = o[q0] / o2[q0]; o3, h3, l3, c3 = (np.r_[x[:q0], y[q0:] * sc] for x, y in ((o, o2), (h, h2), (l, l2), (c, c2)))
                T = int(m[q0 - 1])
                def upto(tr): return [(x["side"], x["ft"], round(x["entry"], 6)) for x in tr if x["ft"] <= T] + [(x["xt"], round(x["exit"], 6)) for x in tr if x["xt"] <= T]
                A = {"FROZEN": run_frozen(m, o, h, l, c, kind), "SIM_wall": sw, "SIM_candle": S.simulate(m, o, h, l, c, kind, PEN_FEE, clock="candle", fib_need=51)[0]}
                B = {"FROZEN": run_frozen(m, o3, h3, l3, c3, kind), "SIM_wall": S.simulate(m, o3, h3, l3, c3, kind, PEN_FEE, clock="wall")[0],
                     "SIM_candle": S.simulate(m, o3, h3, l3, c3, kind, PEN_FEE, clock="candle", fib_need=51)[0]}
                if cut_frac == 0.5:
                    A["FWD"] = fw; B["FWD"] = run_fwd(m, o3, h3, l3, c3, CFG_FEE(kind))[0]
                for k in A:
                    viol[k][1] += 1; v = upto(A[k]) != upto(B[k]); viol[k][0] += v
        # (e) gold-style fixed spread: SIM wall == forward.py
        sw, _ = S.simulate(m, o, h, l, c, "fvg", lambda px, q: 0.05, clock="wall"); fw, _, _ = run_fwd(m, o, h, l, c, CFG_SPR("fvg", 0.05))
        ok, why = same_trades(sw, fw); spr[0] += ok; spr[1] += 1
        if not ok: first_fail.setdefault("sim_vs_fwd_spread", (sd, why))
    record("R1 independent SIM (wall clock) reproduces frozen forward.py trade-for-trade (random walks, ETH-style fee rule)",
           all(a == b for a, b in agree.values()), dict(agree={k: f"{a}/{b} seeds" for k, (a, b) in agree.items()}, first_fail=first_fail))
    record("R2 independent SIM reproduces frozen forward.py with a fixed-spread rule (gold/oil style)", spr[0] == spr[1], dict(agree=f"{spr[0]}/{spr[1]} seeds"))
    record("R3 SIM with the frozen look-ahead selection reproduces frozen verify_minute.py trade-for-trade",
           all(a == b for a, b in la_eq.values()), dict(agree={k: f"{a}/{b} seeds" for k, (a, b) in la_eq.items()}))
    record("R4 prefix invariance: replacing the future after a cut never changes causal decisions before the cut; it does change the frozen backtest's",
           viol["SIM_wall"][0] == 0 and viol["SIM_candle"][0] == 0 and viol["FWD"][0] == 0 and viol["FROZEN"][0] > 0,
           {k: f"{a} of {b} cuts changed past decisions" for k, (a, b) in viol.items()})
    record("R5 timeline invariants of the causal simulator", all(inv[k] == 0 for k in ("fill_before_creation", "fill_after_expiry", "overlapping_positions", "exit_before_fill", "signal_before_next_check")), inv)


def chunk_invariance():
    m, o, h, l, c = walk(7, days=10)
    one, st1, led1 = run_fwd(m, o, h, l, c, CFG_FEE("fib"))
    hours = [int(m[0]) + 60 * k + 9 for k in range(1, len(m) // 60 + 2)]          # hourly cron at hh:09
    many, st2, led2 = run_fwd(m, o, h, l, c, CFG_FEE("fib"), chunks=hours + hours[-1:] * 3)   # last run repeated 3x (no new data)
    strip = lambda L: [",".join(x.split(",")[:-1]) for x in L]                     # drop processed_utc column
    record("D1 forward.py: hourly incremental runs (+3 repeated runs with no new data) == one run; no duplicate ledger rows",
           strip(led1) == strip(led2) and len(set(strip(led2))) == len(led2) and st1["trades"] == st2["trades"],
           dict(single_run_trades=st1["trades"], hourly_runs_trades=st2["trades"], ledger_rows=len(led2) - 1))


if __name__ == "__main__":
    crafted_suite(); frozen_vs_causal_fvg(); randomized(); chunk_invariance()
    RES["summary"] = f"{sum(t['passed'] for t in RES['tests'])}/{len(RES['tests'])} passed"; print(RES["summary"])
    json.dump(RES, open(OUT, "w"), indent=1, default=str)
