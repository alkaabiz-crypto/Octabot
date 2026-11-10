"""Tests for the RSI + VWAP study engine. Run from research/rsi_vwap_study:
    python -m unittest discover -s tests -p "test_*.py"
The cross-check against the frozen Donchian engine runs only if FROZEN_BTC_BREAKOUT is set.
"""
import json
import os
import random
import statistics
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import study as S

T0 = S.ts(2024, 1, 1)


def write_asset(rows_15m, extra_days=0):
    """rows_15m: list of (o, h, l, c, v). 1H and 1D candles are aggregated from them."""
    tmp = tempfile.mkdtemp()
    p = [[T0 + k * 900, *r] for k, r in enumerate(rows_15m)]

    def agg(step):
        out = []
        for r in p:
            b = r[0] // step * step
            if out and out[-1][0] == b:
                x = out[-1]
                x[2], x[3], x[4], x[5] = max(x[2], r[2]), min(x[3], r[3]), r[4], x[5] + r[5]
            else:
                out.append([b, r[1], r[2], r[3], r[4], r[5]])
        return out
    paths = []
    for name, data in (("15m", p), ("1h", agg(3600)), ("1d", agg(86400))):
        path = os.path.join(tmp, f"x_{name}.json")
        with open(path, "w") as f:
            json.dump(data, f)
        paths.append(path)
    return S.Asset("TEST", *paths)


def flat(n, price=100.0, rng=2.0, v=1.0):
    return [(price, price + rng / 2, price - rng / 2, price, v)] * n


class TestIndicators(unittest.TestCase):
    def test_rsi_wilder(self):
        self.assertAlmostEqual(S.rsi([10.0, 11.0, 10.5, 11.5], 3)[3], 80.0)
        self.assertAlmostEqual(S.rsi([10.0, 11.0, 10.5, 11.5, 11.0], 3)[4], 100 - 100 / 2.6)

    def test_session_vwap_resets_daily(self):
        t = [0, 3600, 86400, 90000]
        h, l, c, v = [3.0, 6.0, 9.0, 12.0], [1.0, 2.0, 7.0, 8.0], [2.0, 4.0, 8.0, 10.0], [1.0, 3.0, 2.0, 2.0]
        w = S.session_vwap(t, h, l, c, v)
        tp = [(h[i] + l[i] + c[i]) / 3 for i in range(4)]
        self.assertAlmostEqual(w[1], (tp[0] * 1 + tp[1] * 3) / 4)
        self.assertAlmostEqual(w[2], tp[2])                       # new session
        self.assertAlmostEqual(w[3], (tp[2] * 2 + tp[3] * 2) / 4)

    def test_vwap_and_signals_have_no_look_ahead(self):
        rnd = random.Random(1)
        rows, p = [], 100.0
        for _ in range(4 * 24 * 40):
            c = p * (1 + rnd.gauss(0, 0.003))
            rows.append((p, max(p, c) * 1.001, min(p, c) * 0.999, c, 1 + rnd.random()))
            p = c
        full = write_asset(rows)
        cut = write_asset(rows[: 4 * 24 * 25])
        n = len(cut.e.t)
        self.assertEqual(full.vwap[:n], cut.vwap)
        for rule in S.RULES:
            for d in (1, -1):
                self.assertEqual(full.signals(rule, d)[:n], cut.signals(rule, d), (rule, d))
                self.assertGreater(sum(full.signals(rule, d)), 0, (rule, d))


class TestExecution(unittest.TestCase):
    """ATR14 of the 1H candles is 2.0 in these scenarios, so 1R = 4.0 price units."""

    def asset(self, after):
        # 20 flat hours (80 quarter-hours) with 1H range 2 -> ATR 2; then the scenario bars
        return write_asset(flat(80) + after)

    def test_long_stop(self):
        a = self.asset([(100, 100.5, 99.5, 100, 1)] * 2 + [(100, 100, 95, 96, 1)] + flat(20))
        tr = a.simulate(19, 1, "TRAIL")        # signal on the 20th hour, entry at the next 15m open
        self.assertEqual((tr.entry, tr.risk, tr.reason), (100, 4.0, "stop"))
        self.assertAlmostEqual(tr.r_gross, -1.0)

    def test_short_gap_fills_at_open(self):
        a = self.asset([(100, 100.5, 99.5, 100, 1), (106, 107, 105, 106, 1)] + flat(20, 106))
        tr = a.simulate(19, -1, "SYM")
        self.assertEqual(tr.reason, "stop")
        self.assertAlmostEqual(tr.r_gross, (100 - 106) / 4.0)   # filled at the gap open, worse than -1R

    def test_sym_target_and_time(self):
        a = self.asset([(100, 104, 100, 103, 1)] + flat(20, 103))
        tr = a.simulate(19, 1, "SYM")
        self.assertEqual(tr.reason, "target")
        self.assertAlmostEqual(tr.r_gross, 1.0)
        b = self.asset(flat(4 * 60, 100, 1.0))
        tr = b.simulate(19, 1, "SYM")
        self.assertEqual(tr.reason, "time")
        self.assertEqual(tr.exit_time - tr.entry_time, 48 * 3600)

    def test_sym_stop_first_when_both_touched(self):
        a = self.asset([(100, 105, 95, 100, 1)] + flat(20))
        self.assertEqual(a.simulate(19, 1, "SYM").reason, "stop")

    def test_short_trailing_stop(self):
        down = [(100 - 0.5 * k, 100.25 - 0.5 * k, 99.25 - 0.5 * k, 99.5 - 0.5 * k, 1) for k in range(40)]
        a = self.asset(down + [(80, 95, 80, 94, 1)] + flat(10, 94))
        tr = a.simulate(19, -1, "TRAIL")
        self.assertEqual(tr.reason, "stop")
        self.assertGreater(tr.r_gross, 1.0)

    def test_costs(self):
        tr = S.Trade(0, 0, 3600, 1, 100.0, 4.0, 1.0, "stop", "bull")
        self.assertAlmostEqual(tr.r("primary"), 1.0 - 0.0005 * 25)
        self.assertAlmostEqual(tr.r("stress"), 1.0 - 0.001 * 25)


class TestStats(unittest.TestCase):
    def test_t_and_holm(self):
        self.assertAlmostEqual(S.t_sf(2.0, 10), 0.036694, places=5)
        adj = S.holm({"a": 0.01, "b": 0.04, "c": 0.03})
        self.assertAlmostEqual(adj["a"], 0.03)
        self.assertAlmostEqual(adj["b"], 0.06)

    def test_random_sampler_unbiased(self):
        class T:
            def __init__(self, e, x, r):
                self.entry_time, self.exit_time, self._r = e, x, r
        rnd = random.Random(2)
        outs = []
        for hh in range(24 * 300):
            long_t = rnd.random() < 0.1
            outs.append(T(T0 + hh * 3600, T0 + hh * 3600 + (100 if long_t else 5) * 3600, 5.0 if long_t else -0.5))
        p = {q: 0.05 for q in {S.quarter(o.entry_time) for o in outs}}
        ms = [statistics.mean(o._r for o in S.sequential_random(outs, p, rnd)) for _ in range(200)]
        self.assertAlmostEqual(statistics.mean(ms), statistics.mean(o._r for o in outs), delta=0.08)


FROZEN = os.environ.get("FROZEN_BTC_BREAKOUT", "")


@unittest.skipUnless(FROZEN and os.path.isdir(FROZEN), "FROZEN_BTC_BREAKOUT not set")
class TestAgainstFrozenEngine(unittest.TestCase):
    def test_trailing_long_matches_frozen_donchian_trades(self):
        sys.path.insert(0, os.path.join(FROZEN, "src"))
        import engine  # frozen, read-only
        lab = engine.Lab(os.path.join(FROZEN, "data"))
        frozen_trades = lab.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", S.ts(2025, 7), 10 ** 11)
        d = os.path.join(FROZEN, "data")
        a = S.Asset("BTC", os.path.join(d, "btc_15m.json"), os.path.join(d, "btc_1h.json"), os.path.join(d, "btc_1d.json"))
        checked = 0
        for ft in frozen_trades:
            if ft["exit"] == "data_end":
                continue
            i = a.e_idx[ft["entry_time"] - 3600]
            tr = a.simulate(i, 1, "TRAIL")
            self.assertEqual((tr.entry_time, tr.exit_time, tr.regime), (ft["entry_time"], ft["exit_time"], ft["regime"]))
            self.assertAlmostEqual(tr.r_gross, ft["R_gross"], places=5)
            checked += 1
        self.assertGreater(checked, 90)


if __name__ == "__main__":
    unittest.main()
