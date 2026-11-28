"""No-look-ahead and fill tests. Run from research/tradingview_builtins:
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
import builtin_strategies as B  # noqa: E402
import builtin_indicators as I  # noqa: E402
import run_everything as R  # noqa: E402

T0 = 1735689600


def make(rows):
    path = os.path.join(tempfile.mkdtemp(), "q.csv.gz")
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        for k, (o, h, l, c, n) in enumerate(rows):
            w.writerow([T0 + k * 900, o, h, l, c, o + 0.05, h + 0.05, l + 0.05, c + 0.05, n])
    return B.BuiltinAsset(path)


def walk(n, seed=5):
    rnd = random.Random(seed)
    rows, p = [], 100.0
    for k in range(n):
        drift = 0.0004 if (k // 2500) % 2 == 0 else -0.0004
        c = p * (1 + rnd.gauss(drift, 0.004))
        rows.append((p, max(p, c) * 1.001, min(p, c) * 0.999, c, rnd.randint(1, 40)))
        p = c
    return rows


class NoLookAhead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = walk(16000)
        cls.full = make(cls.rows)
        cls.cut = make(cls.rows[:12000])

    def test_indicator_signals_use_past_only(self):
        a, b = I.signals(self.full.e), I.signals(self.cut.e)
        m = len(self.cut.e.t) - 1
        for name in a:
            for side in (0, 1):
                self.assertEqual(a[name][side][:m], b[name][side][:m], name)

    def test_filters_use_past_only(self):
        a, b = R.filters(self.full), R.filters(self.cut)
        m = len(self.cut.e.t) - 1
        for name in a:
            self.assertEqual(a[name][0][:m], b[name][0][:m], name)
            self.assertEqual(a[name][1][:m], b[name][1][:m], name)

    def test_strategy_orders_use_past_only(self):
        m = len(self.cut.e.t) - 1
        for name in B.NAMES[:-2] + B.CHARTART:
            a = B.strategy_orders(name, self.full.e, self.full.atr)[:m]
            b = B.strategy_orders(name, self.cut.e, self.cut.atr)[:m]
            self.assertEqual(a, b, name)

    def test_strategy_trades_identical_before_cut(self):
        tc = self.cut.e.t[-1] - 30 * 86400
        for name in ("MACD", "CA_GOLDEN_CROSS_SMA200", "TECHNICAL_RATINGS"):
            a = [t for t in self.full.simulate_strategy(name) if t.exit_time < tc]
            b = [t for t in self.cut.simulate_strategy(name) if t.exit_time < tc]
            self.assertEqual(a, b, name)

    def test_buys_pay_the_ask(self):
        for t in self.full.simulate_strategy("MACD"):
            j = self.full.p_idx[t.entry_time]
            q = self.full.q
            if t.direction > 0:
                self.assertGreaterEqual(t.entry, q["bo"][j] + 0.05 - 1e-9)

    def test_golden_cross_is_long_only(self):
        tr = self.full.simulate_strategy("CA_GOLDEN_CROSS_SMA200")
        self.assertTrue(tr)
        self.assertTrue(all(t.direction > 0 for t in tr))


if __name__ == "__main__":
    unittest.main()
