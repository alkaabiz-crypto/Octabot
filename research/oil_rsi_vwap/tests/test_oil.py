"""Tests for the oil engine. Run from research/oil_rsi_vwap: python -m unittest discover -s tests -p "test_*.py"."""
import csv
import gzip
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import oil

T0 = 1735689600  # 2025-01-01 00:00 UTC


def make(rows, spread=0.1, t0=T0, skip_hours=()):
    """rows: (bid o, h, l, c, ticks) per 15m bar. Bars inside ``skip_hours`` (hour index from t0) are left out."""
    path = os.path.join(tempfile.mkdtemp(), "q.csv.gz")
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        for k, (o, h, l, c, n) in enumerate(rows):
            if k // 4 in skip_hours:
                continue
            w.writerow([t0 + k * 900, o, h, l, c, o + spread, h + spread, l + spread, c + spread, n])
    return oil.OilAsset(path)


def flat(n, p=100.0, rng=2.0):
    return [(p, p + rng / 2, p - rng / 2, p, 10)] * n


class TestSessionVwap(unittest.TestCase):
    def test_new_session_after_missing_hour(self):
        a = make(flat(4 * 6), skip_hours=(3,))      # hours 0,1,2 then 4,5
        self.assertEqual(a.session[:3], [1, 1, 1])
        self.assertEqual(a.session[3:], [2, 2])
        self.assertAlmostEqual(a.vwap[3], 100.0)

    def test_weights_are_tick_counts(self):
        rows = [(100, 101, 99, 100, 1)] * 4 + [(110, 111, 109, 110, 3)] * 4
        a = make(rows)
        self.assertAlmostEqual(a.vwap[1], (100 * 4 + 110 * 12) / 16)


class TestExecution(unittest.TestCase):
    """ATR14 = 2 after 20 flat hours, so 1R = 4; spread 0.1."""

    def test_long_pays_ask_and_stops_on_bid(self):
        a = make(flat(80) + [(100, 100.5, 99.5, 100, 10), (100, 100, 96.0, 96.5, 10)] + flat(20, 96.5))
        tr = a.simulate(19, 1, "TRAIL")
        self.assertAlmostEqual(tr.entry, 100.1)
        self.assertEqual(tr.reason, "stop")
        self.assertAlmostEqual(tr.r_gross, -1.0)          # stop at 96.1 on the bid

    def test_short_receives_bid_and_stops_on_ask(self):
        a = make(flat(80) + [(100, 100.5, 99.5, 100, 10), (100, 103.95, 100, 103, 10)] + flat(20, 103))
        tr = a.simulate(19, -1, "SYM")
        self.assertAlmostEqual(tr.entry, 100.0)
        self.assertEqual(tr.reason, "stop")                 # ask high 104.05 >= stop 104
        self.assertAlmostEqual(tr.r_gross, -1.0)

    def test_flat_market_loses_the_spread(self):
        a = make(flat(80 + 4 * 60, 100, 1.0))
        tr = a.simulate(19, 1, "SYM")
        self.assertEqual(tr.reason, "time")
        self.assertLess(tr.r_gross, 0)

    def test_no_trade_when_no_quote_at_signal_close(self):
        a = make(flat(4 * 30), skip_hours=(20,))
        self.assertIsNone(a.simulate(19, 1, "TRAIL"))

    def test_costs(self):
        tr = oil.Trade(0, 0, 2 * 86400, 1, 100.0, 4.0, 1.0, "stop", "bull")
        self.assertAlmostEqual(tr.r("primary"), 1 - 0.0002 * 25)
        self.assertAlmostEqual(tr.r("stress"), 1 - (0.0005 + 0.0004) * 25)


class TestNoLookAhead(unittest.TestCase):
    def test_truncation(self):
        rnd = random.Random(3)
        rows, p = [], 70.0
        for _ in range(4 * 24 * 40):
            c = p * (1 + rnd.gauss(0, 0.003))
            rows.append((p, max(p, c) * 1.001, min(p, c) * 0.999, c, rnd.randint(1, 50)))
            p = c
        full, cut = make(rows), make(rows[: 4 * 24 * 25])
        n = len(cut.e.t)
        self.assertEqual(full.vwap[:n], cut.vwap)
        for rule in ("V1_VWAP_MOMENTUM", "V2_RSI_REVERSION"):
            for d in (1, -1):
                self.assertEqual(full.signals(rule, d)[:n], cut.signals(rule, d))


if __name__ == "__main__":
    unittest.main()
