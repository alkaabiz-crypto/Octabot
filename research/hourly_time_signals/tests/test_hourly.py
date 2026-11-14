"""Tests for the hourly-signal code. Run from research/hourly_time_signals:
    python -m unittest discover -s tests -p "test_*.py"
"""
import calendar
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import hourly as HR


class TestTimes(unittest.TestCase):
    def test_us_dst_and_new_york_times(self):
        winter, summer = HR.S.ts(2026, 1, 15), HR.S.ts(2026, 7, 15)
        self.assertEqual(HR.ny_to_utc(winter, 9, 30), winter + 14 * 3600 + 1800)
        self.assertEqual(HR.ny_to_utc(summer, 9, 30), summer + 13 * 3600 + 1800)
        self.assertEqual(HR.rollover(winter), winter + 22 * 3600)
        self.assertEqual(HR.rollover(summer), summer + 21 * 3600)
        # 2026: DST starts Sunday 8 March, ends Sunday 1 November
        self.assertFalse(HR.us_dst(calendar.timegm((2026, 3, 7, 12, 0, 0))))
        self.assertTrue(HR.us_dst(calendar.timegm((2026, 3, 9, 12, 0, 0))))
        self.assertTrue(HR.us_dst(calendar.timegm((2026, 10, 31, 12, 0, 0))))
        self.assertFalse(HR.us_dst(calendar.timegm((2026, 11, 2, 12, 0, 0))))

    def test_fixed_window_skips_weekends(self):
        plan = HR.fixed_window(HR.S.ts(2026, 1, 5), HR.S.ts(2026, 1, 12), 0, 7, 1)
        self.assertEqual(len(plan), 5)
        self.assertEqual(plan[0][3] - plan[0][2], 7 * 3600)


class FakeQuotes(HR.Quotes):
    def __init__(self, rows):
        self.q = {k: [] for k in ("t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "n")}
        for t, bid, ask in rows:
            for k, v in (("t", t), ("bo", bid), ("ao", ask)):
                self.q[k].append(v)
        self.idx = {t: j for j, t in enumerate(self.q["t"])}


class TestTrades(unittest.TestCase):
    def test_bid_ask_fills_and_costs(self):
        qt = FakeQuotes([(0, 100.0, 100.1), (3600, 101.0, 101.1)])
        self.assertAlmostEqual(qt.trade(0, 3600, 1), (101.0 - 100.1) / 100.1 * 1e4 - 2.0)
        self.assertAlmostEqual(qt.trade(0, 3600, -1), (100.0 - 101.1) / 100.0 * 1e4 - 2.0)
        self.assertIsNone(qt.trade(0, 7200, 1))

    def test_stress_charges_swap_only_across_rollover(self):
        day = HR.S.ts(2026, 1, 15)
        qt = FakeQuotes([(day + 21 * 3600, 100.0, 100.0), (day + 23 * 3600, 100.0, 100.0), (day + 3600, 100.0, 100.0)])
        self.assertAlmostEqual(qt.trade(day + 21 * 3600, day + 23 * 3600, 1, "stress"), -5.0 - 2.0)   # crosses 22:00
        self.assertAlmostEqual(qt.trade(day + 3600, day + 21 * 3600, 1, "stress"), -5.0)


if __name__ == "__main__":
    unittest.main()
