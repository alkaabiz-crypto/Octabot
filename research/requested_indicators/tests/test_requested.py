"""Tests for the requested indicators. Run from research/requested_indicators:
    python -m unittest discover -s tests -p "test_*.py"
"""
import csv
import gzip
import math
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import requested as R

T0 = 1735689600
NAMES = ("VWAP_BAND_REVERSION", "VWAP_BAND_BREAKOUT", "SESSION_VWAP_CROSS", "EMA_20_50_200_PULLBACK", "RSI14",
         "RSI_DIVERGENCE", "ADX14_20", "ADX14_25", "VP_80_RULE", "VP_BREAKOUT", "SUPERTREND", "MACD", "LORENTZIAN")


def make(rows, utc=False):
    path = os.path.join(tempfile.mkdtemp(), "q.csv.gz")
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        for k, (o, h, l, c, n) in enumerate(rows):
            if (k // 4) % 24 == 22:      # a one-hour daily break, like the CFD sessions
                continue
            w.writerow([T0 + k * 900, o, h, l, c, o + 0.05, h + 0.05, l + 0.05, c + 0.05, n])
    return R.ReqAsset(path, utc_day_sessions=utc)


def walk(n, seed=12):
    rnd = random.Random(seed)
    rows, p = [], 100.0
    for k in range(n):
        drift = 0.0002 if (k // 3000) % 2 == 0 else -0.0002   # mild trends, so ADX crosses its thresholds
        c = p * (1 + rnd.gauss(drift, 0.003))
        rows.append((p, max(p, c) * 1.0008, min(p, c) * 0.9992, c, rnd.randint(1, 40)))
        p = c
    return rows


class TestPieces(unittest.TestCase):
    def test_vwap_bands(self):
        t = [0, 3600, 7200]
        h, l, c, v = [2.0, 4.0, 6.0], [2.0, 4.0, 6.0], [2.0, 4.0, 6.0], [1.0, 1.0, 2.0]
        vw, sd = R.session_vwap_bands(t, h, l, c, v, [1, 1, 1])
        self.assertAlmostEqual(vw[2], (2 + 4 + 12) / 4)
        self.assertAlmostEqual(sd[2], math.sqrt((4 + 16 + 72) / 4 - 4.5 ** 2))
        vw, _ = R.session_vwap_bands(t, h, l, c, v, [1, 1, 2])
        self.assertAlmostEqual(vw[2], 6.0)          # a new session resets

    def test_value_area_contains_poc_and_70pct(self):
        q = {"bl": [100.0, 100.0, 104.0], "bh": [101.0, 101.0, 110.0], "n": [100, 100, 10]}
        poc, vah, val = R.session_value_areas(q, [1, 1, 1])[1]
        self.assertTrue(val <= poc <= vah)
        self.assertLess(vah, 104.0)                 # 200 of 210 ticks sit between 100 and 101

    def test_running_normalize_is_causal(self):
        self.assertEqual(R.running_normalize([1.0, 3.0, 2.0, 5.0])[:3], [0.0, 1.0, 0.5])


class TestSignals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = walk(4 * 24 * 160)
        cls.a = make(cls.rows)

    def test_every_signal_fires_without_look_ahead(self):
        cut = make(self.rows[: 4 * 24 * 120])
        n = len(cut.e.t)
        for name in NAMES:
            for d in (1, -1):
                full = self.a.req_signals(name, d)
                self.assertGreater(sum(full), 0, (name, d))
                self.assertEqual(full[:n], cut.req_signals(name, d)[:n], (name, d))

    def test_native_exit_holds_four_hours(self):
        tab = [t for t in self.a.table(1, "NATIVE") if t is not None]
        self.assertTrue(all(t.exit_time - t.entry_time == 4 * 3600 for t in tab[:200]))


if __name__ == "__main__":
    unittest.main()
