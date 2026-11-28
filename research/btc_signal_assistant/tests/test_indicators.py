"""Indicator correctness: textbook properties, independent vectorised references and no look-ahead."""
import unittest

import _common
from signal_assistant import errors
from signal_assistant import indicators as I

try:
    import numpy as np
    import pandas as pd
    HAVE_PANDAS = True
except ImportError:  # pragma: no cover
    HAVE_PANDAS = False


def _candles():
    return _common.synthetic_candles("1h", 600, drift=0.05, amplitude=1.5, seed=3)


class TestDefinedRanges(unittest.TestCase):
    def test_first_defined_index(self):
        c = _candles()
        self.assertEqual(next(i for i, v in enumerate(I.ema(c.c, 50)) if v is not None), 49)
        self.assertEqual(next(i for i, v in enumerate(I.rsi(c.c, 14)) if v is not None), 14)
        line, sig, _hist = I.macd(c.c, 12, 26, 9)
        self.assertEqual(next(i for i, v in enumerate(line) if v is not None), 25)
        self.assertEqual(next(i for i, v in enumerate(sig) if v is not None), 25 + 8)
        a, p, _m = I.adx(c.h, c.l, c.c, 14)
        self.assertEqual(next(i for i, v in enumerate(p) if v is not None), 14)
        self.assertEqual(next(i for i, v in enumerate(a) if v is not None), 27)
        up, _lo, _mid = I.donchian(c.h, c.l, 20)
        self.assertEqual(next(i for i, v in enumerate(up) if v is not None), 20)

    def test_short_series_all_none(self):
        self.assertEqual(I.ema([1.0, 2.0], 5), [None, None])
        self.assertEqual(I.rsi([1.0] * 10, 14), [None] * 10)
        a, _p, _m = I.adx([1.0] * 10, [1.0] * 10, [1.0] * 10, 14)
        self.assertEqual(a, [None] * 10)

    def test_bad_period(self):
        with self.assertRaises(errors.IndicatorError):
            I.ema([1.0, 2.0], 0)
        with self.assertRaises(errors.IndicatorError):
            I.macd([1.0] * 50, 26, 12, 9)


class TestTextbookProperties(unittest.TestCase):
    def test_constant_series(self):
        c = [100.0] * 80
        self.assertTrue(all(v == 100.0 for v in I.ema(c, 10)[9:]))
        self.assertTrue(all(v == 50.0 for v in I.rsi(c, 14)[14:]))   # no gains, no losses
        _line, _sig, hist = I.macd(c, 12, 26, 9)
        self.assertTrue(all(abs(v) < 1e-9 for v in hist[33:]))
        a, _p, _m = I.adx(c, c, c, 14)
        self.assertTrue(all(v == 0.0 for v in a[27:]))

    def test_monotonic_up(self):
        c = [float(i) for i in range(1, 120)]
        self.assertTrue(all(v == 100.0 for v in I.rsi(c, 14)[14:]))
        a, p, m = I.adx([x + 0.5 for x in c], [x - 0.5 for x in c], c, 14)
        self.assertGreater(p[-1], m[-1])
        self.assertEqual(m[-1], 0.0)
        self.assertAlmostEqual(a[-1], 100.0)
        up, _lo, _mid = I.donchian(c, c, 20)
        # the current bar is excluded: a rising close is always above the previous 20-bar high
        self.assertTrue(all(c[i] > up[i] for i in range(20, len(c))))
        self.assertEqual(up[25], c[24])

    def test_monotonic_down_rsi_zero(self):
        c = [float(200 - i) for i in range(120)]
        self.assertTrue(all(v == 0.0 for v in I.rsi(c, 14)[14:]))

    def test_ema_seed_is_sma(self):
        c = _candles().c
        self.assertAlmostEqual(I.ema(c, 20)[19], sum(c[:20]) / 20)
        self.assertAlmostEqual(I.sma(c, 20)[19], sum(c[:20]) / 20)
        self.assertAlmostEqual(I.sma(c, 20)[100], sum(c[81:101]) / 20)

    def test_macd_identity(self):
        c = _candles().c
        line, sig, hist = I.macd(c, 12, 26, 9)
        e12, e26 = I.ema(c, 12), I.ema(c, 26)
        for i in range(40, len(c)):
            self.assertAlmostEqual(line[i], e12[i] - e26[i])
            self.assertAlmostEqual(hist[i], line[i] - sig[i])

    def test_rsi_bounds_and_wilder_example(self):
        c = _candles().c
        self.assertTrue(all(0.0 <= v <= 100.0 for v in I.rsi(c, 14) if v is not None))
        # Hand-computed 3-period example: closes 10, 11, 10.5, 11.5 -> changes +1, -0.5, +1
        # avg gain = 2/3, avg loss = 0.5/3 -> RS = 4 -> RSI = 80
        self.assertAlmostEqual(I.rsi([10.0, 11.0, 10.5, 11.5], 3)[3], 80.0)
        # next close 11.0 (change -0.5): avg gain = (2/3*2 + 0)/3 = 4/9, avg loss = (0.5/3*2 + 0.5)/3 = 5/18
        # RS = 1.6 -> RSI = 61.538...
        self.assertAlmostEqual(I.rsi([10.0, 11.0, 10.5, 11.5, 11.0], 3)[4], 100 - 100 / 2.6, places=6)

    def test_donchian_hand_example(self):
        highs = [5.0, 7.0, 6.0, 9.0, 8.0, 4.0]
        lows = [4.0, 6.0, 5.0, 8.0, 7.0, 3.0]
        up, lo, mid = I.donchian(highs, lows, 3)
        self.assertEqual(up[3], 7.0)   # max of highs[0:3]
        self.assertEqual(lo[3], 4.0)
        self.assertEqual(up[5], 9.0)   # max of highs[2:5]
        self.assertEqual(lo[5], 5.0)
        self.assertEqual(mid[5], 7.0)


@unittest.skipUnless(HAVE_PANDAS, "pandas/numpy not installed")
class TestAgainstVectorisedReference(unittest.TestCase):
    """Independent, vectorised pandas implementations of the same textbook definitions."""

    def setUp(self):
        c = _candles()
        self.h, self.l, self.c = pd.Series(c.h), pd.Series(c.l), pd.Series(c.c)
        self.candles = c

    @staticmethod
    def ref_ema(s, n):
        out = pd.Series(np.nan, index=s.index)
        seed = s.iloc[:n].mean()
        tail = s.iloc[n - 1:].copy()
        tail.iloc[0] = seed
        out.iloc[n - 1:] = tail.ewm(span=n, adjust=False).mean().values
        return out

    @staticmethod
    def ref_wilder(s, n):
        out = pd.Series(np.nan, index=s.index)
        seed = s.iloc[:n].mean()
        tail = s.iloc[n - 1:].copy()
        tail.iloc[0] = seed
        out.iloc[n - 1:] = tail.ewm(alpha=1.0 / n, adjust=False).mean().values
        return out

    def assert_series_close(self, ours, ref, start):
        for i in range(start, len(ours)):
            self.assertIsNotNone(ours[i], i)
            self.assertAlmostEqual(ours[i], float(ref.iloc[i]), places=7, msg=f"index {i}")

    def test_ema(self):
        for n in (12, 26, 50, 200):
            self.assert_series_close(I.ema(self.candles.c, n), self.ref_ema(self.c, n), n - 1)

    def test_rsi(self):
        d = self.c.diff()
        gain, loss = d.clip(lower=0).iloc[1:], (-d.clip(upper=0)).iloc[1:]
        ag, al = self.ref_wilder(gain.reset_index(drop=True), 14), self.ref_wilder(loss.reset_index(drop=True), 14)
        ref = (100 - 100 / (1 + ag / al))
        ours = I.rsi(self.candles.c, 14)
        for i in range(14, len(ours)):
            self.assertAlmostEqual(ours[i], float(ref.iloc[i - 1]), places=7)

    def test_macd(self):
        line, sig, _hist = I.macd(self.candles.c, 12, 26, 9)
        ref_line = self.ref_ema(self.c, 12) - self.ref_ema(self.c, 26)
        ref_sig = self.ref_ema(ref_line.iloc[25:].reset_index(drop=True), 9)
        for i in range(25 + 8, len(line)):
            self.assertAlmostEqual(line[i], float(ref_line.iloc[i]), places=7)
            self.assertAlmostEqual(sig[i], float(ref_sig.iloc[i - 25]), places=7)

    def test_adx(self):
        n = 14
        up, down = self.h.diff(), -self.l.diff()
        pdm = ((up > down) & (up > 0)) * up
        mdm = ((down > up) & (down > 0)) * down
        tr = pd.concat([self.h - self.l, (self.h - self.c.shift()).abs(), (self.l - self.c.shift()).abs()], axis=1).max(axis=1)
        s_tr = self.ref_wilder(tr.iloc[1:].reset_index(drop=True), n)
        s_p = self.ref_wilder(pdm.iloc[1:].reset_index(drop=True), n)
        s_m = self.ref_wilder(mdm.iloc[1:].reset_index(drop=True), n)
        pdi, mdi = 100 * s_p / s_tr, 100 * s_m / s_tr
        dx = (100 * (pdi - mdi).abs() / (pdi + mdi)).iloc[n - 1:].reset_index(drop=True)
        ref_adx = self.ref_wilder(dx, n)
        a, p, m = I.adx(self.candles.h, self.candles.l, self.candles.c, n)
        for i in range(n, len(a)):
            self.assertAlmostEqual(p[i], float(pdi.iloc[i - 1]), places=7)
            self.assertAlmostEqual(m[i], float(mdi.iloc[i - 1]), places=7)
        for i in range(2 * n - 1, len(a)):
            self.assertAlmostEqual(a[i], float(ref_adx.iloc[i - n]), places=7)

    def test_atr(self):
        tr = pd.concat([self.h - self.l, (self.h - self.c.shift()).abs(), (self.l - self.c.shift()).abs()], axis=1).max(axis=1)
        tr.iloc[0] = self.h.iloc[0] - self.l.iloc[0]
        ref = self.ref_wilder(tr, 14)
        self.assert_series_close(I.atr(self.candles.h, self.candles.l, self.candles.c, 14), ref, 13)


class TestNoLookAhead(unittest.TestCase):
    """Truncating the series must not change any earlier value: each value uses only past and current candles."""

    def test_truncation_reproduces_values(self):
        c = _candles()
        full = {"ema": I.ema(c.c, 50), "rsi": I.rsi(c.c, 14), "macd": I.macd(c.c, 12, 26, 9)[2], "adx": I.adx(c.h, c.l, c.c, 14)[0],
                    "dc": I.donchian(c.h, c.l, 20)[0]}
        for cut in (300, 333, 450, 599):
            t = c.truncated(cut)
            part = {"ema": I.ema(t.c, 50), "rsi": I.rsi(t.c, 14), "macd": I.macd(t.c, 12, 26, 9)[2], "adx": I.adx(t.h, t.l, t.c, 14)[0],
                        "dc": I.donchian(t.h, t.l, 20)[0]}
            for name in full:
                for i in range(cut):
                    if full[name][i] is None:
                        self.assertIsNone(part[name][i])
                    else:
                        self.assertAlmostEqual(full[name][i], part[name][i], places=9, msg=f"{name} differs at {i} with cut {cut}")


if __name__ == "__main__":
    unittest.main()
