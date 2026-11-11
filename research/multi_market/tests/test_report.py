import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import report  # noqa: E402


class Rules(unittest.TestCase):
    def test_bh_loaded(self):
        self.assertEqual(report.benjamini_hochberg([0.0001, 0.6, 0.7]), {0})

    def test_eligibility(self):
        ok = {"discovery": {"trades": 150, "expectancy_r": 0.1, "expectancy_stress_r": 0.02, "z": 2.0}}
        bad = {"discovery": {"trades": 150, "expectancy_r": 0.1, "expectancy_stress_r": -0.01, "z": 2.5}}
        self.assertTrue(report.eligible_disc(ok))
        self.assertFalse(report.eligible_disc(bad))

    def test_p(self):
        self.assertAlmostEqual(report.p_of(1.6448536), 0.05, places=4)


if __name__ == "__main__":
    unittest.main()
