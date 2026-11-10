"""Download the source of every TradingView built-in indicator and strategy (pine-facade "standard" list).

Usage: python src/fetch_builtins.py OUT_DIR
Writes OUT_DIR/<safe id>.pine and OUT_DIR/manifest.json. The code is TradingView's, so it is kept out of the
repository; the manifest (name, id, kind, sha256) is committed.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    items = json.loads(get("https://pine-facade.tradingview.com/pine-facade/list?filter=standard"))
    manifest = {}
    for it in items:
        sid = it["scriptIdPart"]
        url = "https://pine-facade.tradingview.com/pine-facade/get/" + urllib.parse.quote(sid, safe="") + "/last"
        try:
            src = json.loads(get(url)).get("source", "")
        except (OSError, ValueError) as e:
            print("FAIL", it["scriptName"], e)
            continue
        safe = re.sub(r"[^A-Za-z0-9_]+", "_", sid)
        with open(os.path.join(out, safe + ".pine"), "w") as f:
            f.write(src)
        kind = "strategy" if re.search(r"^\s*strategy\(", src, re.M) else "indicator"
        manifest[sid] = {"name": it["scriptName"].replace("&#039;", "'"), "file": safe + ".pine", "kind": kind,
                         "chars": len(src), "sha256": hashlib.sha256(src.encode()).hexdigest()}
        time.sleep(0.3)
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(len(manifest), "sources;", sum(v["kind"] == "strategy" for v in manifest.values()), "strategies")


if __name__ == "__main__":
    main()
