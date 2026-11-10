"""Raw Exness tick evidence for the one-year study: file path, size, SHA256 vs manifest, coverage, duplicates, bid/ask checks."""
import csv, hashlib, io, json, os, sys, zipfile
import pandas as pd
tick_dir, manifest, out = sys.argv[1], sys.argv[2], sys.argv[3]
man = {r["month"]: r for r in csv.DictReader(open(manifest))}
rows = []
for f in sorted(os.listdir(tick_dir)):
    if not f.endswith(".zip"): continue
    p = os.path.join(tick_dir, f); data = open(p, "rb").read(); sha = hashlib.sha256(data).hexdigest()
    month = f.split("_")[2] + "-" + f.split("_")[3][:2]; m = man[month]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        name = z.namelist()[0]; df = pd.read_csv(z.open(name))
    t = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d %H:%M:%S.%fZ", utc=True)
    rows.append(dict(month=month, file=p, bytes=len(data), sha256=sha, manifest_sha256=m["zip_sha256"], sha_match=sha == m["zip_sha256"],
                     source_url=m["url"], csv_inside=name, symbols=";".join(sorted(df["Symbol"].unique())), ticks=len(df), manifest_ticks=int(m["ticks"]),
                     first_tick=str(t.iloc[0]), last_tick=str(t.iloc[-1]), exact_duplicate_rows=int(df.duplicated().sum()),
                     same_timestamp_rows=int(t.duplicated().sum()), ask_below_bid=int((df["Ask"] < df["Bid"]).sum()),
                     zero_or_negative=int(((df["Bid"] <= 0) | (df["Ask"] <= 0)).sum()), non_monotonic=int((t.diff().dt.total_seconds() < 0).sum()),
                     median_spread=round(float((df["Ask"] - df["Bid"]).median()), 2), max_spread=round(float((df["Ask"] - df["Bid"]).max()), 2),
                     max_gap_minutes=round(float(t.diff().dt.total_seconds().max() / 60), 1)))
    print(rows[-1]["month"], rows[-1]["sha_match"], rows[-1]["ticks"], rows[-1]["exact_duplicate_rows"], rows[-1]["max_gap_minutes"], flush=True)
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
