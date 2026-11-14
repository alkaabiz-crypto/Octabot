"""Notifications for confirmed BUY signals.

Channels, in order:
  1. console banner (always);
  2. a Markdown alert file in ``alerts/`` plus a row in ``alerts/alerts.csv`` (always);
  3. optional generic JSON webhook (``SIGNAL_ASSISTANT_WEBHOOK_URL``; Discord-compatible payload ``{"content": ...}``);
  4. optional Telegram bot message (``SIGNAL_ASSISTANT_TELEGRAM_BOT_TOKEN`` + ``SIGNAL_ASSISTANT_TELEGRAM_CHAT_ID``).

De-duplication: an alert is sent once per signal candle. The last notified candle close is stored in
``state/last_notified.json``, so re-running within the same hour (or a watch loop) does not spam.
"""
import csv
import json
import os
import time
import typing
import urllib.error
import urllib.parse
import urllib.request

from signal_assistant import constants, enums, errors, report


class NotifyResult(typing.TypedDict):
    sent: bool
    reason: str
    channels: list[str]
    failures: list[str]


class Notifier:
    def __init__(self, base_dir, env=None, urlopen=urllib.request.urlopen, out=print):
        self.base_dir = base_dir
        self.env = os.environ if env is None else env
        self.urlopen = urlopen
        self.out = out
        self.state_dir = os.path.join(base_dir, constants.STATE_DIR)
        self.alerts_dir = os.path.join(base_dir, constants.ALERTS_DIR)
        self.state_path = os.path.join(self.state_dir, constants.LAST_NOTIFIED_FILE)

    # ---- state
    def _load_state(self):
        if not os.path.exists(self.state_path):
            return {}
        with open(self.state_path) as f:
            return json.load(f)

    def _save_state(self, state):
        os.makedirs(self.state_dir, exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=1)

    def already_notified(self, assessment):
        return self._load_state().get("last_buy_candle_ts") == assessment.as_of_ts

    # ---- channels
    def _console(self, text):
        bar = "#" * 78
        self.out("\n" + bar + "\n" + text + "\n" + bar + "\n")

    def _files(self, assessment, text):
        os.makedirs(self.alerts_dir, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%MZ", time.gmtime(assessment.as_of_ts))
        path = os.path.join(self.alerts_dir, f"BUY_{stamp}.md")
        with open(path, "w") as f:
            f.write(f"# {text.splitlines()[0]}\n\n" + "\n".join(text.splitlines()[1:]) + "\n\n```\n" + report.render_text(assessment) + "\n```\n")
        csv_path = os.path.join(self.alerts_dir, constants.ALERTS_CSV)
        row = {"signal_close_utc": assessment.as_of_utc, "recommendation": assessment.recommendation.value,
                   "confidence": assessment.confidence.value, "price": assessment.price,
                   "bullish": assessment.agreement["bullish"], "total": assessment.agreement["total"],
                   "notified_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime())}
        new = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(row))
            if new:
                w.writeheader()
            w.writerow(row)
        return path

    def _post(self, url, payload, headers):
        data = json.dumps(payload).encode() if headers.get("Content-Type") == "application/json" else urllib.parse.urlencode(payload).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with self.urlopen(req, timeout=20) as resp:
                if resp.status >= 300:
                    raise errors.NotificationError(f"HTTP {resp.status} from {url.split('?')[0]}")
        except (urllib.error.URLError, OSError) as e:
            raise errors.NotificationError(f"{url.split('/bot')[0]}: {e}") from e

    def _webhook(self, text):
        url = self.env.get(constants.ENV_WEBHOOK_URL)
        if not url:
            return False
        self._post(url, {"content": text, "text": text}, {"Content-Type": "application/json"})
        return True

    def _telegram(self, text):
        token, chat = self.env.get(constants.ENV_TELEGRAM_TOKEN), self.env.get(constants.ENV_TELEGRAM_CHAT_ID)
        if not (token and chat):
            return False
        self._post(f"https://api.telegram.org/bot{token}/sendMessage", {"chat_id": chat, "text": text},
                   {"Content-Type": "application/x-www-form-urlencoded"})
        return True

    # ---- entry point
    def notify_if_buy(self, assessment, force=False):
        """Send a notification when ``assessment`` is a confirmed BUY not yet notified. Never raises."""
        if assessment.recommendation != enums.Recommendation.BUY:
            return NotifyResult(sent=False, reason="not a BUY", channels=[], failures=[])
        if not force and self.already_notified(assessment):
            return NotifyResult(sent=False, reason=f"already notified for candle {assessment.as_of_utc}", channels=[], failures=[])
        text = report.render_alert(assessment)
        channels, failures = [], []
        self._console(text)
        channels.append("console")
        try:
            channels.append("file:" + self._files(assessment, text))
        except OSError as e:
            failures.append(f"file: {e}")
        for name, fn in (("webhook", self._webhook), ("telegram", self._telegram)):
            try:
                if fn(text):
                    channels.append(name)
            except errors.NotificationError as e:
                failures.append(f"{name}: {e}")
        state = self._load_state()
        state.update(last_buy_candle_ts=assessment.as_of_ts, last_buy_candle_utc=assessment.as_of_utc,
                     notified_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()))
        self._save_state(state)
        return NotifyResult(sent=True, reason="confirmed BUY", channels=channels, failures=failures)
