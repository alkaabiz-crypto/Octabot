"""Tests for round-2 community indicators. Run from research/community_indicators_2:
    python -m unittest discover -s tests -p "test_*.py"
"""
import csv
import gzip
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import community2 as C

T0 = 1735689600


def make(rows):
    path = os.path.join(tempfile.mkdtemp(), "q.csv.gz")
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        for k, (o, h, l, c, n) in enumerate(rows):
            w.writerow([T0 + k * 900, o, h, l, c, o + 0.05, h + 0.05, l + 0.05, c + 0.05, n])
    return C.Community2Asset(path)


def walk(n, seed=9):
    rnd = random.Random(seed)
    rows, p = [], 100.0
    for k in range(n):
        drift = 0.0007 if (k // 2500) % 2 == 0 else -0.0007
        c = p * (1 + rnd.gauss(drift, 0.003))
        rows.append((p, max(p, c) * 1.0008, min(p, c) * 0.9992, c, rnd.randint(1, 30)))
        p = c
    return rows


class TestPieces(unittest.TestCase):
    def test_psar_and_halftrend_follow_a_clean_trend(self):
        up = [100 + 0.5 * i for i in range(80)]
        down = [up[-1] - 0.5 * i for i in range(80)]
        c = up + down
        h, l = [x + 0.3 for x in c], [x - 0.3 for x in c]
        sar = C.psar(h, l)
        self.assertEqual(sar[70], 1)
        self.assertEqual(sar[-1], -1)
        ht = C.halftrend(h, l, c)
        self.assertEqual(ht[70], 1)
        self.assertEqual(ht[-1], -1)

    def test_heikin_ashi_and_coral(self):
        c = [100 + i for i in range(50)]
        self.assertTrue(all(C.heikin_ashi(c, [x + 1 for x in c], [x - 1 for x in c], [x + 0.5 for x in c])[5:]))
        cr = C.coral(c)
        self.assertGreater(cr[-1], cr[-2])

    def test_smc_break_needs_a_confirmed_swing(self):
        # As in the LuxAlgo original, the swing state starts at "high", so a swing high registers only after a swing
        # low: swing low at bar 5 (confirmed at 10), swing high at bar 12 (confirmed at 17), break above it at bar 25.
        h, low = [100.0] * 30, [98.0] * 30
        low[5], h[12] = 90.0, 110.0
        c = [99.0] * 30
        c[25] = 111.0
        sig = C.smc_breaks(h, low, c)
        self.assertEqual(sig[25], 1)
        self.assertEqual(sum(1 for s in sig if s == 1), 1)


class TestSignals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = walk(4 * 24 * 75)
        cls.a = make(cls.rows)

    def test_every_signal_fires_without_look_ahead(self):
        cut = make(self.rows[: 4 * 24 * 50])
        n = len(cut.e.t)
        for name, dirs in C.SIGNALS:
            for d in dirs:
                full = self.a.c2_signals(name, d)
                self.assertGreater(sum(full), 0, (name, d))
                self.assertEqual(full[:n], cut.c2_signals(name, d), (name, d))


if __name__ == "__main__":
    unittest.main()
