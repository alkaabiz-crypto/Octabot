"""Engine, signal, alignment and statistics tests. Run: python -m unittest discover -s tests -p "test_*.py"."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

import engine  # noqa: E402
import indicators as ind  # noqa: E402
import marketdata as md  # noqa: E402
import protocol as P  # noqa: E402
import signals as sg  # noqa: E402
import stats  # noqa: E402


def market(rows, spread=1.0, symbol="TEST", t0=0):
    """rows: list of (o, h, l, c) BID bars, one per hour. Ask = bid + spread."""
    t = [t0 + i * 3600 for i in range(len(rows))]
    o, h, l, c = ([r[k] for r in rows] for k in range(4))
    bars = md.Bars(md.H1, t, o, h, l, c)
    return md.Market(symbol, bars, [x + spread for x in o], [x + spread for x in h], [x + spread for x in l],
                     [x + spread for x in c], [spread] * len(rows), [100] * len(rows))


def flat(n, price=100.0, rng=2.0):
    """n bars with a constant true range so that ATR14 == rng."""
    return [(price, price + rng / 2, price - rng / 2, price) for _ in range(n)]


class FakeRegimes:
    def at(self, t):
        return "bull"


class TestOutcomes(unittest.TestCase):
    """ATR14 is 2.0 in every scenario, so 1R = 4.0 price units; the spread is 1.0 (= 0.25R per round trip)."""

    def setUp(self):
        self.base = flat(20)

    def run_one(self, extra, direction, exit_rule, e=20):
        m = market(self.base + extra)
        return engine.Outcomes(m, direction, exit_rule).table[e]

    def test_long_enters_at_ask_and_stops_at_bid(self):
        # entry bar: bid open 100 -> buy at ask 101; stop = 101 - 4 = 97; next bar bid low 96 -> stopped at 97
        r, x, t_exit, reason, entry, risk = self.run_one([(100, 101, 99, 100), (100, 100, 96, 97)], 1, "TRAIL")
        self.assertEqual((entry, risk, reason, x), (101.0, 4.0, "stop", 21))
        self.assertAlmostEqual(r, -1.0)

    def test_long_gap_through_stop_fills_at_open(self):
        r, x, _, reason, _, _ = self.run_one([(100, 101, 99, 100), (95, 96, 94, 95)], 1, "TRAIL")
        self.assertEqual(reason, "stop")
        self.assertAlmostEqual(r, (95 - 101) / 4.0)       # worse than -1R

    def test_short_enters_at_bid_and_stops_at_ask(self):
        # sell at bid 100; stop = 104; ask high = bid high + 1; bid high 103 -> ask 104 -> stopped at 104
        r, x, _, reason, entry, _ = self.run_one([(100, 101, 99, 100), (100, 103, 100, 102)], -1, "TRAIL")
        self.assertEqual((entry, reason), (100.0, "stop"))
        self.assertAlmostEqual(r, -1.0)

    def test_short_not_stopped_when_only_bid_would_not_reach(self):
        # bid high 102.5 -> ask high 103.5 < 104: still open at data end; closed at the ask close
        r, x, _, reason, _, _ = self.run_one([(100, 101, 99, 100), (100, 102.5, 100, 102)], -1, "TRAIL")
        self.assertEqual(reason, "data_end")
        self.assertAlmostEqual(r, (100 - 103) / 4.0)

    def test_sym_target_long(self):
        # target = 101 + 4 = 105 on the bid
        r, x, _, reason, _, _ = self.run_one([(100, 101, 99, 100), (100, 105, 100, 104)], 1, "SYM")
        self.assertEqual(reason, "target")
        self.assertAlmostEqual(r, 1.0)

    def test_sym_stop_first_when_both_touched(self):
        r, _, _, reason, _, _ = self.run_one([(100, 101, 99, 100), (100, 106, 96, 100)], 1, "SYM")
        self.assertEqual(reason, "stop")
        self.assertAlmostEqual(r, -1.0)

    def test_sym_time_exit(self):
        quiet = [(100, 101, 99, 100)] * 60
        r, x, _, reason, _, _ = self.run_one(quiet, 1, "SYM")
        self.assertEqual(reason, "time")
        self.assertEqual(x - 20 + 1, P.SYM_MAX_BARS)
        self.assertAlmostEqual(r, (100 - 101) / 4.0)       # flat market loses the spread: -0.25R

    def test_sym_short_target_uses_ask(self):
        # short at 100, target 96 on the ASK: bid low 95 -> ask low 96 -> hit
        r, _, _, reason, _, _ = self.run_one([(100, 101, 99, 100), (100, 100, 95, 96)], -1, "SYM")
        self.assertEqual(reason, "target")
        self.assertAlmostEqual(r, 1.0)
        # bid low 95.5 -> ask low 96.5: not hit
        r, _, _, reason, _, _ = self.run_one([(100, 101, 99, 100), (100, 100, 95.5, 96)], -1, "SYM")
        self.assertNotEqual(reason, "target")

    def test_trailing_stop_ratchets_on_closes(self):
        # ATR stays near 2 (ranges of 2). Closes climb to 120; trail = best close - 3*ATR
        up = [(100 + 2 * i, 101 + 2 * i, 99 + 2 * i, 100 + 2 * i + 1) for i in range(10)]
        m = market(self.base + up + [(121, 121, 100, 101)])
        o = engine.Outcomes(m, 1, "TRAIL")
        r, x, _, reason, entry, risk = o.table[20]
        self.assertEqual(reason, "stop")
        self.assertEqual(x, 30)
        best_close = 119.0
        expected_stop = best_close - 3 * o.atr[29]
        self.assertAlmostEqual(r, (expected_stop - entry) / risk)
        self.assertGreater(r, 2.0)

    def test_no_outcome_without_atr(self):
        m = market(flat(30))
        o = engine.Outcomes(m, 1, "TRAIL")
        self.assertIsNone(o.table[5])       # ATR14 undefined at bar 4
        self.assertIsNotNone(o.table[14])   # ATR14 first defined at bar 13

    def test_outcome_never_depends_on_bars_before_signal_bar_except_atr(self):
        """Outcome at e computed on truncated data equals the full-data outcome when the trade ended earlier."""
        rows = self.base + [(100, 101, 99, 100), (100, 100, 96, 97)] + flat(30)
        full = engine.Outcomes(market(rows), 1, "TRAIL").table[20]
        cut = engine.Outcomes(market(rows[:25]), 1, "TRAIL").table[20]
        self.assertEqual(full, cut)


class TestTradesFromSignals(unittest.TestCase):
    def test_one_position_at_a_time_and_next_bar_entry(self):
        rows = flat(20) + [(100, 101, 99, 100)] * 5 + [(100, 100, 95, 96)] + flat(20, 96)
        m = market(rows)
        o = engine.Outcomes(m, 1, "TRAIL")
        sig = [False] * len(rows)
        sig[19] = sig[21] = sig[22] = True      # the 2nd and 3rd arrive while the first trade is open
        sig[25] = True                          # on the exit bar's close: allowed
        tr = engine.trades_from_signals(o, sig, FakeRegimes())
        self.assertEqual([t.signal_index for t in tr], [19, 25])
        self.assertEqual(tr[0].entry_index, 20)
        self.assertEqual(tr[0].exit_index, 25)
        self.assertEqual(tr[0].entry_spread, 1.0)
        self.assertTrue(all(t.entry_time > m.h1.t[t.signal_index] for t in tr))

    def test_costs(self):
        t = engine.Trade(0, 1, 2, 0, 86400 * 2, 1, 100.0, 4.0, 1.0, "stop", "bull", 1.0)
        self.assertAlmostEqual(t.r_net("spread"), 1.0)
        self.assertAlmostEqual(t.r_net("primary"), 1.0 - 0.0002 * 100 / 4)
        self.assertAlmostEqual(t.r_net("stress"), 1.0 - (0.0005 + 0.0002 * 2) * 100 / 4)
        # today: actual spread 1.0 (0.25R) replaced by 0.1% of price (0.1 -> 0.025R), plus primary slippage
        self.assertAlmostEqual(t.r_net("today", 0.001), 1.0 + 0.25 - 0.025 - 0.005)

    def test_random_benchmark_is_reproducible_and_bounded(self):
        m = market(flat(300))
        o = engine.Outcomes(m, 1, "SYM")
        a = engine.random_expectancies(o, 20, 250, 10, "primary", 50, seed=1)
        b = engine.random_expectancies(o, 20, 250, 10, "primary", 50, seed=1)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 50)
        # a flat market only ever loses the spread and slippage
        self.assertTrue(all(-0.3 < x < 0 for x in a))


class TestAlignment(unittest.TestCase):
    def test_aggregate_and_last_closed(self):
        m = market([(i, i + 1, i - 1, i + 0.5) for i in range(1, 13)])     # 12 hourly bars from t=0
        h4 = md.aggregate(m.h1, md.H4)
        self.assertEqual(h4.t, [0, 14400, 28800])
        self.assertEqual((h4.o[0], h4.h[0], h4.l[0], h4.c[0]), (1, 5, 0, 4.5))
        k = md.align(m.h1, h4)
        # hours 0,1,2 close before the first 4H bar is final; hour 3 closes exactly when it becomes final
        self.assertEqual(k[:8], [-1, -1, -1, 0, 0, 0, 0, 1])

    def test_aggregate_with_missing_hours(self):
        bars = md.Bars(md.H1, [0, 3600, 5 * 3600], [1, 2, 3], [2, 3, 4], [0, 1, 2], [1.5, 2.5, 3.5])
        h4 = md.aggregate(bars, md.H4)
        self.assertEqual(h4.t, [0, 14400])
        self.assertEqual(h4.c, [2.5, 3.5])
        # bar at 5h closes at 6h: the 4-8h bin is not final yet, so the usable one is still bin 0
        self.assertEqual(md.last_closed_index(h4, 6 * 3600), 0)

    def test_regime_is_causal(self):
        import random
        rnd = random.Random(5)
        rows, p = [], 100.0
        for _ in range(24 * 320):
            c = p * (1 + rnd.gauss(0.0002, 0.004))
            rows.append((p, max(p, c) * 1.001, min(p, c) * 0.999, c))
            p = c
        m = market(rows)
        full = engine.Regimes(m.h1)
        t_probe = m.h1.t[24 * 300]
        cut_rows = rows[:24 * 300 + 1]
        cut = engine.Regimes(market(cut_rows).h1)
        self.assertEqual(full.at(t_probe), cut.at(t_probe))
        self.assertIn(full.at(t_probe), ("bull", "bear", "sideways"))
        self.assertEqual(full.at(m.h1.t[24 * 100]), "undefined")     # fewer than 200 daily bars


class TestSignals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import random
        rnd = random.Random(11)
        rows, p = [], 100.0
        for i in range(6000):
            drift = 0.0006 if (i // 1500) % 2 == 0 else -0.0006
            c = p * (1 + rnd.gauss(drift, 0.006))
            rows.append((p, max(p, c) * (1 + abs(rnd.gauss(0, 0.002))), min(p, c) * (1 - abs(rnd.gauss(0, 0.002))), c))
            p = c
        cls.rows = rows
        cls.lab = sg.SignalLab(market(rows))

    def test_every_approach_produces_both_directions(self):
        for ap in P.APPROACHES:
            for d in (1, -1):
                s = self.lab.signals(ap, d, P.textbook_candidate(ap))
                self.assertGreater(sum(s), 0, (ap, d))

    def test_a2_is_a_subset_of_a1_like_breakouts(self):
        """Every A2 signal is a fresh Donchian break with the 4H close on the right side of EMA slow -> also A1."""
        for d in (1, -1):
            a1 = self.lab.signals("A1_DONCHIAN_TREND", d, dict(scale=1.0))
            a2 = self.lab.signals("A2_COMBINED", d, dict(scale=1.0))
            self.assertTrue(all(a1[i] for i in range(len(a2)) if a2[i]))
            self.assertLess(sum(a2), sum(a1))

    def test_a3_does_not_need_a_breakout(self):
        a1 = self.lab.signals("A1_DONCHIAN_TREND", 1, dict(scale=1.0))
        a3 = self.lab.signals("A3_VOTING", 1, dict(scale=1.0, k=4))
        self.assertTrue(any(a3[i] and not a1[i] for i in range(len(a3))))

    def test_a3_stricter_k_gives_fewer_or_equal_alignment_bars(self):
        f1, f4 = self.lab.feats(1.0)
        c4 = sum(bool(self.lab._a3_condition(f1, f4, 1, 4, i)) for i in range(len(self.lab.h1)))
        c5 = sum(bool(self.lab._a3_condition(f1, f4, 1, 5, i)) for i in range(len(self.lab.h1)))
        self.assertLessEqual(c5, c4)

    def test_signals_have_no_look_ahead(self):
        """Signals up to bar i computed on data truncated at i equal those computed on the full data."""
        for cut in (3000, 4321, 5999):
            lab_cut = sg.SignalLab(market(self.rows[:cut + 1]))
            for ap in P.APPROACHES:
                for cand in P.candidates(ap):
                    for d in (1, -1):
                        self.assertEqual(self.lab.signals(ap, d, cand)[:cut + 1], lab_cut.signals(ap, d, cand), (ap, cand, d, cut))

    def test_scales_change_signals(self):
        s = [sum(self.lab.signals("A1_DONCHIAN_TREND", 1, dict(scale=x))) for x in P.SCALES]
        self.assertGreater(s[0], s[2])     # faster channel -> more breakouts


class TestAgainstSignalAssistant(unittest.TestCase):
    """A2 with textbook settings must reproduce the existing assistant's BUY and SELL decisions exactly.

    The assistant module is only READ here (imported from its own directory); nothing in it is modified.
    """

    def test_a2_matches_assistant_on_its_fixture(self):
        assistant_dir = os.path.join(os.path.dirname(ROOT), "btc_signal_assistant")
        fixture = os.path.join(assistant_dir, "tests", "fixtures", "btc_1h.json.gz")
        if not os.path.exists(fixture):
            self.skipTest("signal assistant module not present")
        import gzip
        import json
        sys.path.insert(0, assistant_dir)
        try:
            from signal_assistant import analysis, data, enums
            with gzip.open(fixture, "rb") as f:
                r1 = json.load(f)
            with gzip.open(fixture.replace("btc_1h", "btc_4h"), "rb") as f:
                r4 = json.load(f)
            c1, c4 = data.Candles.from_rows("1h", r1), data.Candles.from_rows("4h", r4)
            s1, s4 = analysis.compute_series(c1), analysis.compute_series(c4)
            q = data.DataQualityReport(quality="OK", issues=[], last_closed_1h_utc="", last_closed_4h_utc="",
                                       age_seconds_1h=0, bars_1h=len(c1), bars_4h=len(c4))
            expected = {i: analysis.assess(s1, s4, i, q).recommendation for i in range(1200, len(c1))}
        finally:
            sys.path.remove(assistant_dir)
        bars = md.Bars(md.H1, c1.t, c1.o, c1.h, c1.l, c1.c)
        m = md.Market("BINANCE", bars, c1.o, c1.h, c1.l, c1.c, [0.0] * len(c1), [1] * len(c1))
        lab = sg.SignalLab(m)
        # our 4H bars are aggregated from 1H bars and must equal the exchange's own 4H candles
        # (the aggregation may end with one unfinished bin, which the causal alignment never uses)
        self.assertEqual(lab.h4.t[:len(c4)], c4.t)
        self.assertEqual(max(lab.k4), len(c4) - 1)
        for k in range(len(c4)):
            self.assertAlmostEqual(lab.h4.c[k], c4.c[k])
            self.assertAlmostEqual(lab.h4.h[k], c4.h[k])
            self.assertAlmostEqual(lab.h4.l[k], c4.l[k])
        buy, sell = lab.signals("A2_COMBINED", 1, dict(scale=1.0)), lab.signals("A2_COMBINED", -1, dict(scale=1.0))
        n_buy = n_sell = 0
        for i, rec in expected.items():
            self.assertEqual(buy[i], rec == enums.Recommendation.BUY, f"BUY mismatch at bar {i}")
            self.assertEqual(sell[i], rec == enums.Recommendation.SELL, f"SELL mismatch at bar {i}")
            n_buy += buy[i]
            n_sell += sell[i]
        self.assertGreater(n_buy, 20)
        self.assertGreater(n_sell, 20)


class TestStats(unittest.TestCase):
    def test_t_distribution(self):
        self.assertAlmostEqual(stats.t_sf(2.0, 10), 0.036694, places=5)
        self.assertAlmostEqual(stats.t_sf(0.0, 7), 0.5)
        self.assertAlmostEqual(stats.t_sf(-2.0, 10), 1 - 0.036694, places=5)
        self.assertAlmostEqual(stats.t_sf(1.6449, 10 ** 7), 0.05, places=4)

    def test_summary(self):
        rs = [1.0, -1.0, 2.0, -1.0, -1.0, 3.0]
        s = stats.summarize(rs)
        self.assertEqual(s["trades"], 6)
        self.assertAlmostEqual(s["win_rate_pct"], 50.0)
        self.assertAlmostEqual(s["profit_factor"], 2.0)
        self.assertAlmostEqual(s["expectancy_r"], 0.5)
        self.assertAlmostEqual(s["max_drawdown_r"], 2.0)
        self.assertEqual(s["longest_losing_streak"], 2)
        self.assertLess(s["ci95_low"], 0.5)
        self.assertGreater(s["ci95_high"], 0.5)
        self.assertEqual(stats.summarize([])["trades"], 0)

    def test_holm_and_p_random(self):
        adj = stats.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": None})
        self.assertAlmostEqual(adj["a"], 0.03)
        self.assertAlmostEqual(adj["c"], 0.06)
        self.assertAlmostEqual(adj["b"], 0.06)
        self.assertIsNone(adj["d"])
        self.assertAlmostEqual(stats.p_random(0.5, [0.1, 0.2, 0.6]), 2 / 4)

    def test_indicators_basic(self):
        self.assertAlmostEqual(ind.rsi([10.0, 11.0, 10.5, 11.5], 3)[3], 80.0)
        up, lo = ind.donchian([5.0, 7.0, 6.0, 9.0], [4.0, 6.0, 5.0, 8.0], 3)
        self.assertEqual((up[3], lo[3]), (7.0, 4.0))


class TestProtocol(unittest.TestCase):
    def test_folds_are_contiguous_and_stop_before_final_test(self):
        for asset, cfg in P.ASSETS.items():
            f = P.folds(asset)
            self.assertEqual(f[0][1], cfg["first_fold"])
            self.assertEqual(f[-1][2], cfg["final_start"])
            self.assertTrue(all(a[2] == b[1] for a, b in zip(f, f[1:])))

    def test_candidates(self):
        self.assertEqual(len(P.candidates("A1_DONCHIAN_TREND")), 3)
        self.assertEqual(len(P.candidates("A3_VOTING")), 6)
        self.assertEqual(P.scaled(1.0), P.TEXTBOOK)
        self.assertIn(P.textbook_candidate("A3_VOTING"), P.candidates("A3_VOTING"))


if __name__ == "__main__":
    unittest.main()
