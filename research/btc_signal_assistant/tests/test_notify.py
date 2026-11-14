"""Notification channels, de-duplication and failure handling."""
import io
import json
import os
import tempfile
import unittest
import urllib.error

from signal_assistant import constants, notify
from test_analysis import breakout_1h, bullish_4h, run


class _Resp(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestNotifier(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = []
        self.requests = []

        def urlopen(req, timeout=0):
            self.requests.append(req)
            return _Resp(b"{}")
        self.urlopen = urlopen
        self.buy = run(breakout_1h(), bullish_4h())
        self.wait = run(breakout_1h(close=100, prev_close=99), bullish_4h())

    def tearDown(self):
        self.tmp.cleanup()

    def notifier(self, env=None):
        return notify.Notifier(self.tmp.name, env=env or {}, urlopen=self.urlopen, out=self.out.append)

    def test_buy_notifies_console_and_files_once(self):
        n = self.notifier()
        res = n.notify_if_buy(self.buy)
        self.assertTrue(res["sent"])
        self.assertIn("console", res["channels"])
        self.assertTrue(any(ch.startswith("file:") for ch in res["channels"]))
        self.assertEqual(res["failures"], [])
        self.assertIn("CONFIRMED BUY", self.out[0])
        alerts = os.listdir(os.path.join(self.tmp.name, constants.ALERTS_DIR))
        self.assertIn(constants.ALERTS_CSV, alerts)
        self.assertTrue(any(a.startswith("BUY_") and a.endswith(".md") for a in alerts))
        with open(os.path.join(self.tmp.name, constants.STATE_DIR, constants.LAST_NOTIFIED_FILE)) as f:
            state = json.load(f)
        self.assertEqual(state["last_buy_candle_ts"], self.buy.as_of_ts)
        # same candle again -> de-duplicated
        res2 = n.notify_if_buy(self.buy)
        self.assertFalse(res2["sent"])
        self.assertIn("already notified", res2["reason"])
        self.assertEqual(len(self.out), 1)
        # force overrides
        self.assertTrue(n.notify_if_buy(self.buy, force=True)["sent"])

    def test_non_buy_is_silent(self):
        res = self.notifier().notify_if_buy(self.wait)
        self.assertFalse(res["sent"])
        self.assertEqual(self.out, [])
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, constants.ALERTS_DIR)))

    def test_webhook_and_telegram(self):
        env = {constants.ENV_WEBHOOK_URL: "https://hooks.example/abc",
               constants.ENV_TELEGRAM_TOKEN: "123:abc", constants.ENV_TELEGRAM_CHAT_ID: "42"}
        res = self.notifier(env).notify_if_buy(self.buy)
        self.assertIn("webhook", res["channels"])
        self.assertIn("telegram", res["channels"])
        self.assertEqual(len(self.requests), 2)
        hook, tg = self.requests
        self.assertEqual(hook.full_url, "https://hooks.example/abc")
        self.assertIn("CONFIRMED BUY", json.loads(hook.data.decode())["content"])
        self.assertTrue(tg.full_url.startswith("https://api.telegram.org/bot123:abc/sendMessage"))
        self.assertIn(b"chat_id=42", tg.data)

    def test_webhook_failure_is_reported_not_raised(self):
        def failing(req, timeout=0):
            raise urllib.error.URLError("down")
        n = notify.Notifier(self.tmp.name, env={constants.ENV_WEBHOOK_URL: "https://hooks.example/x"}, urlopen=failing, out=self.out.append)
        res = n.notify_if_buy(self.buy)
        self.assertTrue(res["sent"])
        self.assertTrue(any(f.startswith("webhook") for f in res["failures"]))
        self.assertNotIn("webhook", res["channels"])

    def test_alert_text_has_no_probability_claims(self):
        from signal_assistant import report
        text = report.render_alert(self.buy).lower()
        self.assertIn("not a probability", text)
        self.assertNotIn("guaranteed", text)
        self.assertNotIn("% chance", text)


if __name__ == "__main__":
    unittest.main()
