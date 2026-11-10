"""Download the original Pine source of TradingView community scripts (open-source ones only).

Usage: python src/fetch_pine.py OUT_DIR URL [URL ...]
For each script page: reads its title and publication id (PUB;...), downloads the latest source from TradingView's
pine-facade service, and writes OUT_DIR/<id>.pine plus OUT_DIR/manifest.json (url, title, version, sha256).
The sources are third-party code under their authors' licences, so they are kept out of the repository; only the
manifest is committed.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    mpath = os.path.join(out, "manifest.json")
    manifest = {}
    if os.path.exists(mpath):
        with open(mpath) as f:
            manifest = json.load(f)
    for url in sys.argv[2:]:
        try:
            page = get(url)
        except OSError as e:
            print("PAGE FAIL", url, e)
            continue
        title = re.search(r"<title>([^<]*)</title>", page)
        pub = sorted(set(re.findall(r"PUB;[A-Za-z0-9]+", page)))
        if not pub:
            print("NO PUB ID (protected or invite-only?)", url, title.group(1) if title else "")
            continue
        try:
            data = json.loads(get("https://pine-facade.tradingview.com/pine-facade/get/" + pub[0].replace(";", "%3B") + "/last"))
        except (OSError, ValueError) as e:
            print("SOURCE FAIL", url, e)
            continue
        src = data.get("source", "")
        if not src:
            print("NO SOURCE (closed-source)", url)
            continue
        key = pub[0].split(";")[1]
        with open(os.path.join(out, key + ".pine"), "w") as f:
            f.write(src)
        ver = re.search(r"@version\s*=\s*(\d+)", src)
        manifest[url] = {"title": title.group(1) if title else "", "pub_id": pub[0], "pine_version": ver.group(1) if ver else "?",
                         "chars": len(src), "sha256": hashlib.sha256(src.encode()).hexdigest(), "fetched_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime())}
        print("OK", manifest[url]["title"][:70], "| v" + manifest[url]["pine_version"], len(src), "chars")
        time.sleep(1)
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=1)


if __name__ == "__main__":
    main()
