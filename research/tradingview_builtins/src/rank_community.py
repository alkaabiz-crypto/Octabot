"""Rank TradingView community scripts by likes, via the public search endpoint (pubscripts-suggest-json).

Usage: python src/rank_community.py OUT_JSON
Runs generic queries (several pages each), keeps one entry per script, and records likes (agreeCount), access level,
type and whether the source contains buy/sell signal outputs. Sources are saved next to OUT_JSON but not committed.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

QUERIES = ["trend", "signal", "buy sell", "rsi", "macd", "volume", "momentum", "oscillator", "moving average", "breakout",
           "scalping", "gold", "bitcoin", "strategy", "supertrend", "vwap", "support resistance", "reversal", "atr",
           "bollinger", "stochastic", "ema", "smart money", "order block", "liquidity", "divergence", "channel", "squeeze",
           "machine learning", "indicator", "alerts", "trailing stop", "range filter", "heikin ashi", "fibonacci"]
PAGES = 4
UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return json.loads(r.read())


def main():
    out = sys.argv[1]
    src_dir = os.path.join(os.path.dirname(out), "community_sources")
    os.makedirs(src_dir, exist_ok=True)
    scripts = {}
    for q in QUERIES:
        for p in range(PAGES):
            url = "https://www.tradingview.com/pubscripts-suggest-json/?search=" + urllib.parse.quote(q) + (f"&offset={p * 50}" if p else "")
            try:
                d = get(url)
            except (OSError, ValueError) as e:
                print("FAIL", q, p, e)
                break
            for x in d.get("results", []):
                sid = x["scriptIdPart"]
                src = x.get("scriptSource") or ""
                if sid not in scripts:
                    signals = bool(re.search(r"(plotshape|alertcondition|label\.new|strategy\.entry)", src)) and bool(re.search(r"(?i)\b(buy|sell|long|short)\b", src))
                    repaint_risk = bool(re.search(r"(lookahead\s*=\s*barmerge\.lookahead_on|offset\s*=\s*-|ta\.pivothigh|pivothigh|zigzag|request\.security)", src))
                    scripts[sid] = {"name": x["scriptName"], "author": (x.get("author") or {}).get("username"), "likes": x.get("agreeCount") or 0,
                                    "access": x.get("access"), "kind": "strategy" if re.search(r"^\s*strategy\(", src, re.M) else "indicator",
                                    "has_source": bool(src), "has_signals": signals, "repaint_risk_flags": repaint_risk, "url_id": x.get("imageUrl")}
                    if src:
                        with open(os.path.join(src_dir, re.sub(r"[^A-Za-z0-9]+", "_", sid) + ".pine"), "w") as f:
                            f.write(src)
            if not d.get("next"):
                break
            time.sleep(0.5)
        print(q, len(scripts), flush=True)
    ranked = sorted(scripts.items(), key=lambda kv: -kv[1]["likes"])
    with open(out, "w") as f:
        json.dump([{"id": k, **v} for k, v in ranked], f, indent=1)
    print("unique scripts:", len(ranked))


if __name__ == "__main__":
    main()
