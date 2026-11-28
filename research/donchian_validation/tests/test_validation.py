"""Tests for the validation code. Run from research/donchian_validation:
    FROZEN_BTC_BREAKOUT=<frozen research/btc_breakout> python -m unittest discover -s tests -p "test_*.py"
Tests that need the frozen checkout are skipped when FROZEN_BTC_BREAKOUT is not set.
"""
import collections
import os
import random
import statistics
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import itertools

import config
import replica
import run_validation as rv
import vstats

HAVE_FROZEN = bool(config.FROZEN_DIR) and os.path.isdir(config.FROZEN_DIR)


class FakeTrade:
    def __init__(self, entry, exit_, r):
        self.entry_time, self.exit_time, self._r = entry, exit_, r
        self.regime, self.reason = "bull", "stop"

    def r_net(self, cost):
        return self._r

    @property
    def hold_hours(self):
        return (self.exit_time - self.entry_time) / 3600


class TestRandomSampler(unittest.TestCase):
    """Long trades are the winners. A sampler must not under-sample them."""

    def setUp(self):
        rnd = random.Random(3)
        self.outcomes = []
        t0 = config.ts(2021, 1)
        for h in range(24 * 360):
            long_trade = rnd.random() < 0.1
            dur = (100 if long_trade else 5) * 3600
            r = 5.0 if long_trade else -0.5          # pool mean = 0.1*5 - 0.9*0.5 = 0.05
            self.outcomes.append(FakeTrade(t0 + h * 3600, t0 + h * 3600 + dur, r))
        self.pool_mean = statistics.mean(t._r for t in self.outcomes)

    def test_sequential_sampler_is_unbiased(self):
        p = collections.defaultdict(lambda: 0.05)
        rnd = random.Random(1)
        means = []
        for _ in range(300):
            ch = rv.sequential_random(self.outcomes, p, rnd)
            means.append(statistics.mean(t._r for t in ch))
        self.assertAlmostEqual(statistics.mean(means), self.pool_mean, delta=0.08)

    def test_shuffle_then_reject_overlaps_is_biased_against_long_trades(self):
        rnd = random.Random(2)
        means = []
        for _ in range(100):
            cand = self.outcomes[:]
            rnd.shuffle(cand)
            chosen, spans = [], []
            for t in cand:
                if len(chosen) >= 300:
                    break
                if any(a < t.exit_time and t.entry_time < b for a, b in spans):
                    continue
                spans.append((t.entry_time, t.exit_time))
                chosen.append(t)
            means.append(statistics.mean(t._r for t in chosen))
        self.assertLess(statistics.mean(means), self.pool_mean - 0.15)


class TestRollovers(unittest.TestCase):
    def test_counts_and_friday_triple(self):
        # Wed 2026-01-07 12:00 UTC -> Sat 2026-01-10 12:00 UTC (winter: rollover 22:00): Wed, Thu, Fri
        n, days = rv.rollovers(config.ts(2026, 1, 7, 12), config.ts(2026, 1, 10, 12))
        self.assertEqual(n, 3)
        self.assertEqual(days, 5)          # Friday counts 3
        # summer: rollover at 21:00; a trade 20:30 -> 21:30 crosses it, 21:30 -> 23:00 does not
        self.assertEqual(rv.rollovers(config.ts(2026, 7, 1, 20) + 1800, config.ts(2026, 7, 1, 21) + 1800)[0], 1)
        self.assertEqual(rv.rollovers(config.ts(2026, 7, 1, 21) + 1800, config.ts(2026, 7, 1, 23))[0], 0)
        self.assertEqual(rv.rollovers(config.ts(2026, 1, 7, 10), config.ts(2026, 1, 7, 20))[0], 0)

    def test_dst(self):
        self.assertTrue(rv.eu_dst(config.ts(2026, 7, 1)))
        self.assertFalse(rv.eu_dst(config.ts(2026, 1, 1)))
        self.assertFalse(rv.eu_dst(config.ts(2026, 3, 29, 0)))   # last Sunday of March 2026 is the 29th, switch 01:00 UTC
        self.assertTrue(rv.eu_dst(config.ts(2026, 3, 29, 2)))


class TestStats(unittest.TestCase):
    def test_distributions(self):
        self.assertAlmostEqual(vstats.chi2_sf(18.307, 10), 0.05, places=4)
        self.assertAlmostEqual(vstats.t_sf(2.0, 10), 0.036694, places=5)
        self.assertAlmostEqual(vstats.norm_sf(1.96), 0.025, places=3)

    def test_ljung_box_white_noise_and_ar(self):
        rnd = random.Random(4)
        x = [rnd.gauss(0, 1) for _ in range(2000)]
        self.assertGreater(vstats.ljung_box(x, 10)["p_value"], 0.01)
        y = [0.0]
        for _ in range(1999):
            y.append(0.5 * y[-1] + rnd.gauss(0, 1))
        self.assertLess(vstats.ljung_box(y, 10)["p_value"], 1e-6)

    def test_runs_test(self):
        self.assertLess(vstats.runs_test([True] * 50 + [False] * 50)["p_two_sided"], 1e-6)
        self.assertLess(vstats.runs_test([i % 2 == 0 for i in range(100)])["p_two_sided"], 1e-6)

    def test_summary_drawdown(self):
        s = vstats.summary([1, -1, -1, 3, -1])
        self.assertEqual(s["max_drawdown_r"], 2)
        self.assertEqual(s["longest_losing_streak"], 2)
        self.assertAlmostEqual(s["profit_factor"], 4 / 3)

    def test_stationary_bootstrap(self):
        rnd = random.Random(5)
        idx = vstats.stationary_bootstrap_indices(100, 5, rnd)
        self.assertEqual(len(idx), 100)
        runs = sum(1 for a, b in itertools.pairwise(idx) if b != (a + 1) % 100)
        self.assertTrue(8 < runs < 35)    # about n / mean_block block starts


@unittest.skipUnless(HAVE_FROZEN, "FROZEN_BTC_BREAKOUT not set")
class TestAgainstFrozenEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import frozen
        cls.lab = frozen.lab()
        cls.m = replica.Market(cls.lab)

    def test_replica_matches_engine_on_holdout(self):
        e = self.lab.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", config.ts(2025, 7), 10 ** 11)
        r = self.m.run(config.ts(2025, 7), 10 ** 11)
        self.assertEqual(len(e), len(r))
        for a, b in zip(e, r):
            self.assertEqual((a["entry_time"], a["exit_time"], a["exit"]), (b.entry_time, b.exit_time, b.reason))
            self.assertAlmostEqual(a["R_gross"], b.r_gross, places=6)

    def test_delay_and_slippage_only_make_fills_worse_on_average(self):
        base = [t for t in self.m.run(config.ts(2024, 1), config.ts(2025, 1))]
        slip = [t for t in self.m.run(config.ts(2024, 1), config.ts(2025, 1), stop_slip=0.001)]
        self.assertEqual(len(base), len(slip))
        self.assertTrue(all(b.r_gross <= a.r_gross + 1e-12 for a, b in zip(base, slip)))

    def test_frozen_files_unchanged(self):
        import frozen
        self.assertTrue(frozen.check_integrity())


if __name__ == "__main__":
    unittest.main()
