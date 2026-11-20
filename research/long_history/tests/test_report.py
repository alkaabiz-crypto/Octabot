import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import report  # noqa: E402


class Rules(unittest.TestCase):
    def test_bh_rejects_only_small_p(self):
        p = [0.0001, 0.0004, 0.03, 0.2, 0.5] + [0.6] * 95
        self.assertEqual(report.benjamini_hochberg(p), {0, 1})

    def test_bh_none(self):
        self.assertEqual(report.benjamini_hochberg([0.04] + [0.5] * 49), set())

    def test_consistency(self):
        good = {"years": {"2020": [50, 0.1], "2021": [50, -0.1], "2022": [50, 0.2]}, "halves": [0.1, 0.05]}
        bad = {"years": {"2020": [50, 0.1], "2021": [50, -0.1], "2022": [50, -0.2]}, "halves": [0.1, 0.05]}
        self.assertTrue(report.consistent(good))
        self.assertFalse(report.consistent(bad))


if __name__ == "__main__":
    unittest.main()
