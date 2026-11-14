"""Decision rules: each branch is exercised with hand-built indicator states, and invariants hold on real data."""
import unittest

import _common
from signal_assistant import analysis, constants, data, enums


def _quality(q=enums.DataQuality.OK, issues=()):
    return data.DataQualityReport(quality=q.value, issues=list(issues), last_closed_1h_utc="", last_closed_4h_utc="",
                                  age_seconds_1h=0, bars_1h=1000, bars_4h=300)


def _series(tf, n, close, prev_close, ema50, ema200, rsi, macd, sig, hist, prev_hist, adx, pdi, mdi, up, lo, prev_up=None, prev_lo=None):
    """Build a Series whose last two bars have the given indicator state."""
    c = _common.synthetic_candles(tf, n)
    cl = list(c.c)
    cl[-1], cl[-2] = close, prev_close
    cand = data.Candles(tf, c.t, c.o, [max(x, close, prev_close) + 1 for x in c.h], [1.0] * n, cl, c.v)
    def full(v, prev=None):
        arr = [v] * n
        if prev is not None:
            arr[-2] = prev
        return arr
    return analysis.Series(cand, full(ema50), full(ema200), full(rsi), full(macd), full(sig), full(hist, prev_hist), full(adx), full(pdi), full(mdi),
                           full(up, prev_up), full(lo, prev_lo), full((up + lo) / 2), full(1.0))


def bullish_4h(**over):
    kw = {"tf": "4h", "n": 250, "close": 110, "prev_close": 109, "ema50": 105, "ema200": 100, "rsi": 60, "macd": 2, "sig": 1, "hist": 1, "prev_hist": 0.5,
              "adx": 30, "pdi": 30, "mdi": 10, "up": 120, "lo": 90}
    kw.update(over)
    return _series(**kw)


def bearish_4h(**over):
    kw = {"tf": "4h", "n": 250, "close": 90, "prev_close": 91, "ema50": 95, "ema200": 100, "rsi": 40, "macd": -2, "sig": -1, "hist": -1, "prev_hist": -0.5,
              "adx": 30, "pdi": 10, "mdi": 30, "up": 110, "lo": 80}
    kw.update(over)
    return _series(**kw)


def breakout_1h(**over):
    """Fresh breakout: close above the previous-20 high, previous close was not."""
    kw = {"tf": "1h", "n": 1000, "close": 112, "prev_close": 108, "ema50": 105, "ema200": 100, "rsi": 62, "macd": 1.5, "sig": 1.0, "hist": 0.5, "prev_hist": 0.2,
              "adx": 25, "pdi": 28, "mdi": 12, "up": 110, "lo": 95, "prev_up": 110, "prev_lo": 95}
    kw.update(over)
    return _series(**kw)


def breakdown_1h(**over):
    kw = {"tf": "1h", "n": 1000, "close": 93, "prev_close": 97, "ema50": 96, "ema200": 100, "rsi": 38, "macd": -1.5, "sig": -1.0, "hist": -0.5, "prev_hist": -0.2,
              "adx": 25, "pdi": 12, "mdi": 28, "up": 105, "lo": 95, "prev_up": 105, "prev_lo": 95}
    kw.update(over)
    return _series(**kw)


def run(s1h, s4h, quality=None):
    # 1000 1H bars and 250 4H bars start together, so the last 4H bar closes exactly when the last 1H bar closes
    return analysis.assess(s1h, s4h, len(s1h.candles) - 1, quality or _quality())


class TestBuy(unittest.TestCase):
    def test_confirmed_buy(self):
        a = run(breakout_1h(), bullish_4h())
        self.assertEqual(a.recommendation, enums.Recommendation.BUY)
        self.assertTrue(a.confirmed_buy)
        self.assertEqual(a.trend_4h, enums.Bias.BULLISH)
        self.assertEqual(a.missing_for_buy, [])
        self.assertEqual(a.agreement["bullish"], 9)   # 4H Donchian is neutral (inside channel)
        self.assertEqual(a.confidence, enums.Confidence.HIGH)
        self.assertTrue(any("fresh breakout" in r for r in a.reasons))
        self.assertIn("not a probability", a.evidence_note)

    def test_buy_medium_confidence_with_neutral_adx(self):
        a = run(breakout_1h(adx=15), bullish_4h())    # 1H ADX neutral -> still 3 confirmers
        self.assertEqual(a.recommendation, enums.Recommendation.BUY)
        self.assertEqual(a.confidence, enums.Confidence.MEDIUM)

    def test_buy_downgraded_when_rsi_stretched(self):
        a = run(breakout_1h(rsi=85), bullish_4h())
        self.assertEqual(a.recommendation, enums.Recommendation.WAIT)
        self.assertTrue(any("stretched" in r for r in a.reasons))

    def test_not_fresh_breakout_is_wait(self):
        a = run(breakout_1h(prev_close=111), bullish_4h())   # previous close already above the band
        self.assertEqual(a.recommendation, enums.Recommendation.WAIT)
        self.assertTrue(any("fresh close above" in m for m in a.missing_for_buy))

    def test_one_bearish_confirmer_blocks_buy(self):
        a = run(breakout_1h(macd=-1, sig=1, hist=-2), bullish_4h())
        self.assertEqual(a.recommendation, enums.Recommendation.WAIT)
        self.assertTrue(any("MACD" in m and "bearish" in m for m in a.missing_for_buy))

    def test_too_few_confirmers_blocks_buy(self):
        a = run(breakout_1h(adx=10, rsi=50), bullish_4h())  # ADX neutral, RSI neutral -> 2 confirmers
        self.assertEqual(a.recommendation, enums.Recommendation.WAIT)

    def test_buy_with_weak_4h_adx_warns(self):
        a = run(breakout_1h(), bullish_4h(adx=15))
        self.assertEqual(a.recommendation, enums.Recommendation.BUY)
        self.assertTrue(any("4H ADX" in w for w in a.warnings))

    def test_buy_with_degraded_data_warns(self):
        a = run(breakout_1h(), bullish_4h(), _quality(enums.DataQuality.DEGRADED, ["historical gap"]))
        self.assertEqual(a.recommendation, enums.Recommendation.BUY)
        self.assertTrue(any("degraded" in w for w in a.warnings))


class TestSell(unittest.TestCase):
    def test_confirmed_sell(self):
        a = run(breakdown_1h(), bearish_4h())
        self.assertEqual(a.recommendation, enums.Recommendation.SELL)
        self.assertTrue(any("not a validated short" in w for w in a.warnings))

    def test_sell_downgraded_when_rsi_extreme(self):
        a = run(breakdown_1h(rsi=15), bearish_4h())
        self.assertEqual(a.recommendation, enums.Recommendation.WAIT)


class TestAvoid(unittest.TestCase):
    def test_counter_trend_breakout(self):
        a = run(breakout_1h(), bearish_4h())
        self.assertEqual(a.recommendation, enums.Recommendation.AVOID)
        self.assertEqual(a.confidence, enums.Confidence.NONE)
        self.assertTrue(any("counter-trend" in r for r in a.reasons))

    def test_counter_trend_breakdown(self):
        a = run(breakdown_1h(), bullish_4h())
        self.assertEqual(a.recommendation, enums.Recommendation.AVOID)

    def test_no_trend_anywhere(self):
        # mixed 4H EMA structure (close above EMA200, EMA50 below), ADX < 20 on both timeframes, no breakout
        s4 = bullish_4h(ema50=98, adx=12)
        s1 = breakout_1h(close=100, prev_close=99, adx=12)   # inside channel
        a = run(s1, s4)
        self.assertEqual(a.trend_4h, enums.Bias.NEUTRAL)
        self.assertEqual(a.recommendation, enums.Recommendation.AVOID)
        self.assertTrue(any("no trend" in r for r in a.reasons))

    def test_unusable_data(self):
        a = run(breakout_1h(), bullish_4h(), _quality(enums.DataQuality.UNUSABLE, ["stale data"]))
        self.assertEqual(a.recommendation, enums.Recommendation.AVOID)
        self.assertIn("usable, fresh, gap-free data", a.missing_for_buy)
        self.assertTrue(any("stale" in r for r in a.reasons))

    def test_indicators_not_ready(self):
        c1h = _common.synthetic_candles("1h", 50)
        c4h = _common.synthetic_candles("4h", 50)
        a = analysis.assess(analysis.compute_series(c1h), analysis.compute_series(c4h), 49, _quality())
        self.assertEqual(a.recommendation, enums.Recommendation.AVOID)
        self.assertEqual(a.readings_1h, [])


class TestWait(unittest.TestCase):
    def test_wait_lists_missing_conditions(self):
        a = run(breakout_1h(close=100, prev_close=99), bullish_4h())   # gate ok, no trigger
        self.assertEqual(a.recommendation, enums.Recommendation.WAIT)
        self.assertTrue(any("4H trend gate passed" in r for r in a.reasons))
        self.assertTrue(any("1H trigger" in m for m in a.missing_for_buy))

    def test_to_dict_is_json_friendly(self):
        import json
        a = run(breakout_1h(), bullish_4h())
        d = json.loads(json.dumps(a.to_dict()))
        self.assertEqual(d["recommendation"], "BUY")
        self.assertEqual(d["readings_1h"][0]["bias"], "BULLISH")


class TestReadings(unittest.TestCase):
    def test_rsi_bands(self):
        s = breakout_1h(rsi=75)
        self.assertIn("overbought", analysis.read_rsi(s, -1).summary)
        s = breakout_1h(rsi=25)
        r = analysis.read_rsi(s, -1)
        self.assertEqual(r.bias, enums.Bias.BEARISH)
        self.assertIn("oversold", r.summary)

    def test_adx_neutral_below_20(self):
        r = analysis.read_adx(breakout_1h(adx=19.9, pdi=40, mdi=5), -1)
        self.assertEqual(r.bias, enums.Bias.NEUTRAL)

    def test_ema_mixed(self):
        r = analysis.read_ema(breakout_1h(close=101, ema50=99, ema200=100), -1)
        self.assertEqual(r.bias, enums.Bias.NEUTRAL)

    def test_donchian_position(self):
        r = analysis.read_donchian(breakout_1h(close=102.5, prev_close=102, up=110, lo=95), -1)
        self.assertEqual(r.bias, enums.Bias.NEUTRAL)
        self.assertEqual(r.values["position_pct"], 50.0)


class TestAlignment(unittest.TestCase):
    def test_aligned_4h_index_uses_only_closed_candles(self):
        c4h = _common.synthetic_candles("4h", 10, start_t=0)   # opens at 0, 14400, ...; closes at 14400, 28800, ...
        self.assertEqual(analysis.aligned_4h_index(c4h, 3600), -1)       # no 4H candle closed yet
        self.assertEqual(analysis.aligned_4h_index(c4h, 14400), 0)       # closes exactly now -> usable
        self.assertEqual(analysis.aligned_4h_index(c4h, 14400 + 3600), 0)
        self.assertEqual(analysis.aligned_4h_index(c4h, 28800 - 1), 0)
        self.assertEqual(analysis.aligned_4h_index(c4h, 28800), 1)
        self.assertEqual(analysis.aligned_4h_index(c4h, 10 ** 9), 9)


class TestInvariantsOnRealData(unittest.TestCase):
    """Every recommendation on the fixture must satisfy the documented rule set."""

    @classmethod
    def setUpClass(cls):
        cls.c1h, cls.c4h = _common.fixture_candles("1h"), _common.fixture_candles("4h")
        cls.s1h, cls.s4h = analysis.compute_series(cls.c1h), analysis.compute_series(cls.c4h)
        cls.quality = data.assess_quality(cls.c1h, cls.c4h, now_s=cls.c1h.close_time(len(cls.c1h) - 1))
        cls.results = [analysis.assess(cls.s1h, cls.s4h, i, cls.quality) for i in range(constants.MIN_BARS_1H, len(cls.c1h))]

    def test_fixture_quality_ok(self):
        self.assertEqual(self.quality["quality"], "OK", self.quality["issues"])

    def test_all_classes_occur(self):
        seen = {a.recommendation for a in self.results}
        self.assertEqual(seen, set(enums.Recommendation))

    def test_rules(self):
        for a in self.results:
            if not a.readings_1h:   # 4H indicators not yet defined this early in the fixture
                self.assertEqual(a.recommendation, enums.Recommendation.AVOID)
                continue
            r1 = {r.name.split()[0]: r for r in a.readings_1h}
            confirmers = [r1["EMA"], r1["RSI"], r1["MACD"], r1["ADX"]]
            bull = sum(r.bias == enums.Bias.BULLISH for r in confirmers)
            bear = sum(r.bias == enums.Bias.BEARISH for r in confirmers)
            dc = r1["Donchian"]
            if a.recommendation == enums.Recommendation.BUY:
                self.assertEqual(a.trend_4h, enums.Bias.BULLISH, a.as_of_utc)
                self.assertEqual(dc.values.get("fresh_breakout"), 1.0, a.as_of_utc)
                self.assertGreaterEqual(bull, 3, a.as_of_utc)
                self.assertEqual(bear, 0, a.as_of_utc)
                self.assertLessEqual(r1["RSI"].values["rsi"], constants.RSI_EXTREME_HIGH, a.as_of_utc)
                self.assertEqual(a.missing_for_buy, [])
                self.assertNotEqual(a.confidence, enums.Confidence.NONE)
            elif a.recommendation == enums.Recommendation.SELL:
                self.assertEqual(a.trend_4h, enums.Bias.BEARISH)
                self.assertEqual(dc.values.get("fresh_breakdown"), 1.0)
                self.assertGreaterEqual(bear, 3)
                self.assertEqual(bull, 0)
            elif a.recommendation == enums.Recommendation.AVOID:
                self.assertEqual(a.confidence, enums.Confidence.NONE)
                counter = (a.trend_4h == enums.Bias.BULLISH and dc.bias == enums.Bias.BEARISH) or \
                          (a.trend_4h == enums.Bias.BEARISH and dc.bias == enums.Bias.BULLISH)
                adx4 = next(r for r in a.readings_4h if r.name.startswith("ADX")).values["adx"]
                chop = a.trend_4h == enums.Bias.NEUTRAL and r1["ADX"].values["adx"] < 20 and adx4 < 20
                self.assertTrue(counter or chop, a.as_of_utc)
            else:
                buy_possible = (a.trend_4h == enums.Bias.BULLISH and dc.values.get("fresh_breakout") == 1.0 and bull >= 3 and bear == 0
                                and r1["RSI"].values["rsi"] <= constants.RSI_EXTREME_HIGH)
                self.assertFalse(buy_possible, a.as_of_utc)

    def test_assess_latest_matches_replay_path(self):
        latest = analysis.assess_latest(self.c1h, self.c4h, now_s=self.c1h.close_time(len(self.c1h) - 1))
        self.assertEqual(latest.to_dict(), self.results[-1].to_dict())

    def test_no_look_ahead_on_real_data(self):
        """Assessing with the series truncated right after bar i gives the same answer as on the full history."""
        for i in (constants.MIN_BARS_1H + 10, len(self.c1h) // 2, len(self.c1h) - 100, len(self.c1h) - 1):
            tc = self.c1h.close_time(i)
            k = analysis.aligned_4h_index(self.c4h, tc)
            t1h, t4h = self.c1h.truncated(i + 1), self.c4h.truncated(k + 1)
            a_trunc = analysis.assess(analysis.compute_series(t1h), analysis.compute_series(t4h), i, self.quality)
            self.assertEqual(a_trunc.to_dict(), self.results[i - constants.MIN_BARS_1H].to_dict(), f"bar {i}")


if __name__ == "__main__":
    unittest.main()
