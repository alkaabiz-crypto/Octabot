"""Tests for the scan engine. Run from research/indicator_scan: python -m unittest discover -s tests -p "test_*.py"."""
import csv
import gzip
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import scan

T0 = 1735689600


def make(rows, spread=0.1):
    path = os.path.join(tempfile.mkdtemp(), "q.csv.gz")
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        for k, (o, h, l, c, n) in enumerate(rows):
            w.writerow([T0 + k * 900, o, h, l, c, o + spread, h + spread, l + spread, c + spread, n])
    return scan.ScanAsset(path)


def walk(n, seed=1, vol=0.003):
    rnd = random.Random(seed)
    rows, p = [], 100.0
    for _ in range(n):
        c = p * (1 + rnd.gauss(0, vol))
        rows.append((p, max(p, c) * 1.0008, min(p, c) * 0.9992, c, rnd.randint(1, 30)))
        p = c
    return rows


class TestIndicators(unittest.TestCase):
    def test_textbook_values(self):
        self.assertEqual(scan.sma([1, 2, 3, 4], 2), [None, 1.5, 2.5, 3.5])
        up, lo = scan.bollinger([1.0, 1.0, 1.0], 3)
        self.assertEqual((up[2], lo[2]), (1.0, 1.0))
        k, _d = scan.stochastic([2.0] * 20, [0.0] * 20, [2.0] * 20)
        self.assertAlmostEqual(k[-1], 100.0)
        c = [float(i) for i in range(40)]
        self.assertTrue(all(v > 0 for v in scan.cci([x + 1 for x in c], [x - 1 for x in c], c)[19:]))

    def test_supertrend_follows_trend(self):
        up = [100 + i * 0.5 for i in range(60)]
        down = [up[-1] - i * 0.5 for i in range(60)]
        c = up + down
        t = scan.supertrend([x + 0.3 for x in c], [x - 0.3 for x in c], c)
        self.assertEqual(t[55], 1)
        self.assertEqual(t[-1], -1)


class TestSignalsAndExits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = walk(4 * 24 * 60)
        cls.a = make(cls.rows)

    def test_every_indicator_fires_and_has_no_look_ahead(self):
        cut = make(self.rows[: 4 * 24 * 40])
        n = len(cut.e.t)
        for name in scan.INDICATORS:
            for d in (1, -1):
                full = self.a.scan_signals(name, d)
                self.assertGreater(sum(full), 0, (name, d))
                self.assertEqual(full[:n], cut.scan_signals(name, d), (name, d))

    def test_hw_exit_wins_often_at_random_but_loses_after_costs(self):
        outs = [t for t in self.a.table(1, "HW") if t is not None]
        win = sum(t.r_gross > 0 for t in outs) / len(outs)
        mean = sum(t.r("primary") for t in outs) / len(outs)
        self.assertGreater(win, 0.6)       # target is half the stop: random entries win about 2 in 3
        self.assertLess(mean, 0)           # ...and still lose money after spread and slippage

    def test_hw_target_is_half_the_stop(self):
        outs = [t for t in self.a.table(-1, "HW") if t is not None and t.reason == "target"]
        self.assertTrue(all(abs(t.r_gross - 0.5) < 1e-9 for t in outs[:50]))


if __name__ == "__main__":
    unittest.main()
