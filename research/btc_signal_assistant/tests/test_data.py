"""Data loading, sanity checks, quality assessment and closed-candle fetching."""
import io
import json
import unittest

import _common
from signal_assistant import data, errors


class TestCandles(unittest.TestCase):
    def test_rejects_corrupt_candle(self):
        with self.assertRaises(errors.CorruptCandleError):
            data.Candles.from_rows("1h", [[0, 10, 9, 8, 9.5, 1]])      # high below open
        with self.assertRaises(errors.CorruptCandleError):
            data.Candles.from_rows("1h", [[0, 10, 11, 8, 9.5, -1]])    # negative volume

    def test_sorts_and_round_trips(self):
        c = data.Candles.from_rows("1h", [[3600, 1, 2, 0.5, 1.5, 1], [0, 1, 2, 0.5, 1.5, 1]])
        self.assertEqual(c.t, [0, 3600])
        self.assertEqual(c.close_time(1), 7200)
        self.assertEqual(len(c.truncated(1)), 1)
        self.assertEqual(data.Candles.from_rows("1h", c.to_rows()).t, c.t)


class TestQuality(unittest.TestCase):
    def setUp(self):
        self.c1h, self.c4h = _common.fixture_candles("1h"), _common.fixture_candles("4h")
        self.now = self.c1h.close_time(len(self.c1h) - 1) + 60

    def test_ok(self):
        q = data.assess_quality(self.c1h, self.c4h, now_s=self.now)
        self.assertEqual(q["quality"], "OK")
        self.assertEqual(q["issues"], [])

    def test_stale(self):
        q = data.assess_quality(self.c1h, self.c4h, now_s=self.now + 3 * 3600)
        self.assertEqual(q["quality"], "UNUSABLE")
        self.assertTrue(any("stale" in s for s in q["issues"]))

    def test_insufficient(self):
        q = data.assess_quality(self.c1h.truncated(100), self.c4h.truncated(100), now_s=self.c1h.close_time(99))
        self.assertEqual(q["quality"], "UNUSABLE")

    def test_recent_gap_unusable_and_old_gap_degraded(self):
        rows = self.c1h.to_rows()
        recent = rows[:-10] + rows[-9:]           # drop one of the last 10 candles
        q = data.assess_quality(data.Candles.from_rows("1h", recent), self.c4h, now_s=self.now)
        self.assertEqual(q["quality"], "UNUSABLE")
        old = rows[:500] + rows[501:]             # drop a candle far in the past
        q = data.assess_quality(data.Candles.from_rows("1h", old), self.c4h, now_s=self.now)
        self.assertEqual(q["quality"], "DEGRADED")

    def test_4h_ahead_of_1h(self):
        q = data.assess_quality(self.c1h.truncated(len(self.c1h) - 5), self.c4h, now_s=self.c1h.close_time(len(self.c1h) - 6))
        self.assertEqual(q["quality"], "UNUSABLE")
        self.assertTrue(any("runs ahead" in s for s in q["issues"]))


class _FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestFetch(unittest.TestCase):
    def test_closed_candles_only_and_paging(self):
        now_s = 1_800_000_000
        step = 3600
        # 1200 hourly candles ending with one that is still open at now_s
        all_rows = []
        t0 = now_s - 1199 * step
        for i in range(1200):
            ot = t0 + i * step
            all_rows.append([ot * 1000, "1", "2", "0.5", "1.5", "3", ot * 1000 + step * 1000 - 1])
        calls = []

        def fake_urlopen(url, timeout=0, context=None):
            start = int(url.split("startTime=")[1]) // 1000
            page = [r for r in all_rows if r[0] // 1000 >= start][:1000]
            calls.append(start)
            return _FakeResponse(json.dumps(page).encode())

        import urllib.request
        orig = urllib.request.urlopen
        urllib.request.urlopen = fake_urlopen
        try:
            c = data.fetch_closed_candles("1h", t0, now_s=now_s)
        finally:
            urllib.request.urlopen = orig
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(c), 1199)                           # the open candle is excluded
        self.assertEqual(c.close_time(len(c) - 1), now_s - step + step)  # last close == now_s - 0? last included closes at now_s
        self.assertTrue(all(c.close_time(i) <= now_s for i in range(len(c))))

    def test_download_failure_raises_typed_error(self):
        import urllib.error
        import urllib.request

        def failing(url, timeout=0, context=None):
            raise urllib.error.URLError("offline")
        orig = urllib.request.urlopen
        urllib.request.urlopen = failing
        try:
            with self.assertRaises(errors.DataUnavailableError):
                data.fetch_closed_candles("1h", 0, now_s=1, retries=2, sleep=lambda s: None)
        finally:
            urllib.request.urlopen = orig


if __name__ == "__main__":
    unittest.main()
