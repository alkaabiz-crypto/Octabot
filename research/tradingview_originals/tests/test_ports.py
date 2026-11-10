"""Tests for the original-script ports. Run from research/tradingview_originals:
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

import ports as P

T0 = 1735689600


def make(rows, crypto=False):
    path = os.path.join(tempfile.mkdtemp(), "q.csv.gz")
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        for k, (o, h, l, c, n) in enumerate(rows):
            w.writerow([T0 + k * 900, o, h, l, c, o + 0.05, h + 0.05, l + 0.05, c + 0.05, n])
    return P.OriginalAsset(path, crypto=crypto)


def walk(n, seed=21):
    rnd = random.Random(seed)
    rows, p = [], 100.0
    for k in range(n):
        drift = 0.0003 if (k // 3000) % 2 == 0 else -0.0003
        c = p * (1 + rnd.gauss(drift, 0.004))
        rows.append((p, max(p, c) * 1.001, min(p, c) * 0.999, c, rnd.randint(1, 40)))
        p = c
    return rows


class TestPorts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = walk(4 * 24 * 260)          # long enough for the Lorentzian loop (needs > 4,000 hourly bars)
        cls.a = make(cls.rows)

    def test_every_script_fires_without_look_ahead(self):
        cut = make(self.rows[: 4 * 24 * 200])
        n = len(cut.e.t)
        for name, (b, s) in self.a.sig.items():
            if name == "WADDAH_ATTAR_ORIGINAL":
                continue                        # fixed dead zone of 20 never triggers at this synthetic price scale
            self.assertGreater(sum(b) + sum(s), 0, name)
            cb, cs = cut.sig[name]
            self.assertEqual(b[:n], cb, name)
            self.assertEqual(s[:n], cs, name)

    def test_lorentzian_gives_both_directions_once_the_history_block_is_used(self):
        # From bar 4,000 the original searches the fixed block from t-2000 down to bar 1,999 (see PROTOCOL.md)
        ls, ss = self.a.sig["LORENTZIAN_V6"]
        self.assertGreater(sum(ls[4000:]), 0)
        self.assertGreater(sum(ss[4000:]), 0)

    def test_flip_legs_run_signal_to_opposite_signal(self):
        buy, sell = self.a.sig["SUPERTREND_KIVANC"]
        legs = self.a.flip_trades("SUPERTREND_KIVANC", 1, 0, 10 ** 11)
        self.assertGreater(len(legs), 5)
        for tr in legs[:20]:
            i = tr.signal_index
            self.assertTrue(buy[i])
            j = next(k for k in range(i + 1, len(sell)) if sell[k])
            self.assertEqual(tr.exit_time, self.a.e.t[j] + 3600)

    def test_bigbeluga_signals_respect_the_ten_bar_gap(self):
        b, s = self.a.sig["BIGBELUGA_SESSION_VWAP"]
        idx = [i for i in range(len(b)) if b[i] or s[i]]
        self.assertTrue(all(y - x >= 10 for x, y in itertools.pairwise(idx)))


if __name__ == "__main__":
    unittest.main()
