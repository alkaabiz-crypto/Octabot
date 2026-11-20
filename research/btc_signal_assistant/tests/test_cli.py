"""run.py and replay.py end to end on the offline fixture."""
import contextlib
import io
import json
import os
import tempfile
import unittest

import _common
import replay
import run
from signal_assistant import enums


class TestRun(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = _common.write_fixture_dir(os.path.join(self.tmp.name, "data"))
        # point notifier state at the temp dir so tests never touch the real module directory
        self._orig_here = run.HERE
        run.HERE = self.tmp.name

    def tearDown(self):
        run.HERE = self._orig_here
        self.tmp.cleanup()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = run.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_text_output(self):
        code, out, _err = self._run("--offline", self.data_dir)
        self.assertIn(code, (0, run.EXIT_BUY))
        self.assertIn("RECOMMENDATION :", out)
        self.assertIn("4H trend confirmation", out)
        self.assertIn("1H entry timeframe", out)
        self.assertIn("Evidence note", out)
        table_rows = [l for l in out.splitlines() if l.startswith("  [")]
        self.assertEqual(len(table_rows), 10)
        for name in ("Donchian 20", "EMA 50/200", "RSI 14", "MACD 12/26/9", "ADX 14"):
            self.assertEqual(sum(name in l for l in table_rows), 2, name)   # once per timeframe

    def test_json_output_and_exit_code(self):
        code, out, _ = self._run("--offline", self.data_dir, "--json")
        d = json.loads(out)
        self.assertIn(d["recommendation"], [r.value for r in enums.Recommendation])
        self.assertEqual(code, run.EXIT_BUY if d["recommendation"] == "BUY" else 0)
        self.assertEqual(len(d["readings_1h"]), 5)
        self.assertEqual(len(d["readings_4h"]), 5)

    def test_quiet(self):
        _code, out, _ = self._run("--offline", self.data_dir, "--quiet")
        self.assertEqual(len(out.strip().splitlines()), 1)

    def test_missing_offline_file_is_data_problem(self):
        code, _out, err = self._run("--offline", os.path.join(self.tmp.name, "nowhere"))
        self.assertEqual(code, 1)
        self.assertIn("DATA PROBLEM", err)

    def test_watch_rejects_offline(self):
        with self.assertRaises(SystemExit):
            self._run("--offline", self.data_dir, "--watch")

    def test_seconds_to_next_close(self):
        self.assertEqual(run.seconds_to_next_1h_close(now=3600 * 10 + 100, delay=45), 3500 + 45)


class TestReplay(unittest.TestCase):
    def test_replay_runs_and_is_descriptive(self):
        tmp = tempfile.TemporaryDirectory()
        data_dir = _common.write_fixture_dir(os.path.join(tmp.name, "data"))
        csv_path = os.path.join(tmp.name, "signals.csv")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = replay.main(["--offline", data_dir, "--csv", csv_path])
        text = out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Descriptive only", text)
        self.assertIn("Verdict on profitability: NONE", text)
        self.assertIn("BUY signals:", text)
        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path) as f:
            header = f.readline().strip().split(",")
        self.assertEqual(header[:3], ["signal_close_utc", "recommendation", "confidence"])
        tmp.cleanup()

    def test_replay_matches_live_path_for_last_bar(self):
        c1h, c4h = _common.fixture_candles("1h"), _common.fixture_candles("4h")
        from signal_assistant import analysis
        results = replay.replay(c1h, c4h, start_index=len(c1h) - 3)
        live = analysis.assess_latest(c1h, c4h, now_s=c1h.close_time(len(c1h) - 1))
        self.assertEqual(results[-1][1].recommendation, live.recommendation)
        self.assertEqual(results[-1][1].reasons, live.reasons)


if __name__ == "__main__":
    unittest.main()
