"""BTCUSDT indicator signal assistant - command line entry point.

Examples
  python run.py                      analyse the latest closed candles (downloads from Binance)
  python run.py --json               same, machine-readable
  python run.py --offline cache      use cache/btc_1h.json and cache/btc_4h.json instead of downloading
  python run.py --save cache         download, then save the candles for later offline runs
  python run.py --watch              re-analyse after every 1H close and notify on confirmed BUY signals
  python run.py --quiet              only print the recommendation line (and alerts)

Exit code: 0 normal, 1 data problem (nothing analysed), 10 when the recommendation is BUY (handy for shell automation).
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from signal_assistant import analysis, constants, data, enums, errors, notify, report

EXIT_BUY = 10


def load_market(args):
    if args.offline:
        c1h = data.load_candles_file("1h", os.path.join(args.offline, "btc_1h.json"))
        c4h = data.load_candles_file("4h", os.path.join(args.offline, "btc_4h.json"))
        return c1h, c4h
    c1h, c4h = data.fetch_market(days=args.days)
    if args.save:
        os.makedirs(args.save, exist_ok=True)
        data.save_candles_file(c1h, os.path.join(args.save, "btc_1h.json"))
        data.save_candles_file(c4h, os.path.join(args.save, "btc_4h.json"))
    return c1h, c4h


def analyse_once(args, notifier):
    try:
        c1h, c4h = load_market(args)
    except errors.DataError as e:
        print(f"DATA PROBLEM: {e}. No recommendation produced.", file=sys.stderr)
        return 1
    now_s = None if not args.offline else c1h.close_time(len(c1h) - 1)  # offline files are judged as of their last candle
    a = analysis.assess_latest(c1h, c4h, now_s=now_s)
    if args.json:
        print(report.render_json(a))
    elif args.quiet:
        print(f"{a.as_of_utc} UTC  {a.recommendation.value}  confidence {a.confidence.value}  close {a.price:,.2f}")
    else:
        print(report.render_text(a))
    res = notifier.notify_if_buy(a)
    if res["sent"]:
        print(f"Notification sent via {', '.join(res['channels'])}" + (f"; failures: {res['failures']}" if res["failures"] else ""), file=sys.stderr)
    elif a.recommendation == enums.Recommendation.BUY:
        print(f"BUY already notified ({res['reason']})", file=sys.stderr)
    return EXIT_BUY if a.recommendation == enums.Recommendation.BUY else 0


def seconds_to_next_1h_close(now=None, delay=45):
    now = time.time() if now is None else now
    step = constants.STEP_SECONDS["1h"]
    return (step - int(now) % step) + delay


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", action="store_true", help="print the assessment as JSON")
    p.add_argument("--quiet", action="store_true", help="print only the recommendation line")
    p.add_argument("--offline", metavar="DIR", help="read btc_1h.json / btc_4h.json from DIR instead of downloading")
    p.add_argument("--save", metavar="DIR", help="save downloaded candles to DIR")
    p.add_argument("--days", type=int, default=constants.DEFAULT_HISTORY_DAYS, help="history to download (default %(default)s)")
    p.add_argument("--watch", action="store_true", help="loop: re-run shortly after every 1H candle close")
    args = p.parse_args(argv)
    if args.watch and args.offline:
        p.error("--watch cannot be combined with --offline")
    notifier = notify.Notifier(HERE)
    if not args.watch:
        return analyse_once(args, notifier)
    print("Watching BTCUSDT. Re-analysing after every 1H close. Ctrl-C to stop.", file=sys.stderr)
    while True:
        analyse_once(args, notifier)
        wait = seconds_to_next_1h_close()
        print(f"next check in {wait // 60} min", file=sys.stderr)
        try:
            time.sleep(wait)
        except KeyboardInterrupt:
            print("stopped", file=sys.stderr)
            return 0


if __name__ == "__main__":
    sys.exit(main())
