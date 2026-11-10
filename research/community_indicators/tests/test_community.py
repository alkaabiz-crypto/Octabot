"""Tests for the community indicators. Run from research/community_indicators:
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
import itertools

import community as C

T0 = 1735689600


def make(rows):
    path = os.path.join(tempfile.mkdtemp(), "q.csv.gz")
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        for k, (o, h, l, c, n) in enumerate(rows):
            w.writerow([T0 + k * 900, o, h, l, c, o + 0.05, h + 0.05, l + 0.05, c + 0.05, n])
    return C.CommunityAsset(path)


def walk(n, seed=4):
    rnd = random.Random(seed)
    rows, p = [], 100.0
    for k in range(n):
        drift = 0.0006 if (k // 2000) % 2 == 0 else -0.0006
        c = p * (1 + rnd.gauss(drift, 0.003))
        rows.append((p, max(p, c) * 1.0008, min(p, c) * 0.9992, c, rnd.randint(1, 30)))
        p = c
    return rows


class TestPieces(unittest.TestCase):
    def test_wma_and_linreg(self):
        self.assertAlmostEqual(C.wma([1.0, 2.0, 3.0], 3)[2], (1 + 4 + 9) / 6)
        self.assertAlmostEqual(C.linreg_last([1.0, 2.0, 3.0, 4.0]), 4.0)
        self.assertAlmostEqual(C.linreg_last([5.0, 5.0, 5.0]), 5.0)

    def test_ut_bot_stop_trails_below_rising_price(self):
        c = [100 + i for i in range(30)]
        stop = C.ut_bot(c, [2.0] * 30)
        self.assertTrue(all(s < x for s, x in zip(stop[5:], c[5:])))
        self.assertEqual(stop[-1], c[-1] - 2.0)

    def test_hull_follows_trend(self):
        c = [100 + 0.5 * i for i in range(120)]
        h = C.hull(c)
        self.assertGreater(h[-1], h[-3])


class TestSignals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = walk(4 * 24 * 70)
        cls.a = make(cls.rows)

    def test_every_indicator_fires_both_ways_without_look_ahead(self):
        cut = make(self.rows[: 4 * 24 * 45])
        n = len(cut.e.t)
        for name in C.INDICATORS:
            for d in (1, -1):
                full = self.a.community_signals(name, d)
                self.assertGreater(sum(full), 0, (name, d))
                self.assertEqual(full[:n], cut.community_signals(name, d), (name, d))

    def test_flip_indicators_alternate(self):
        for name in ("SSL_CHANNEL", "CHANDELIER_EXIT", "HULL_SUITE", "RANGE_FILTER"):
            b, s = self.a.community_signals(name, 1), self.a.community_signals(name, -1)
            seq = [1 if b[i] else -1 for i in range(len(b)) if b[i] or s[i]]
            self.assertTrue(all(x != y for x, y in itertools.pairwise(seq)), name)


if __name__ == "__main__":
    unittest.main()
