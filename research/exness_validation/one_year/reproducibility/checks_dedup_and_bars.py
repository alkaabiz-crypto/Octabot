"""(a) Duplicate-tick effect: original tick_replay with exact-duplicate tick rows removed vs as-run.
(b) Bar rebuild: original build_bars.process() fed the local verified zips (urlopen patched to read the file) into a temp
folder; compare decompressed bytes with the committed bars15m files."""
import glob, gzip, hashlib, io, json, os, sys, zipfile
import numpy as np
REPO = sys.argv[1]; TICKS = os.environ["TICK_DIR"]; TMP = os.environ["STUDY_TMP"]
sys.path.insert(0, os.path.join(REPO, "research/exness_validation/one_year/src")); sys.path.insert(0, os.path.join(REPO, "research/exness_validation/src"))
import study as S
from engine import Lab
out = {}
# ---- (a)
LX = Lab(os.path.join(TMP, "exness_bid"))
cx = S.candidates(LX)
ts, bid, ask = S.load_ticks()
base = S.tick_replay(LX, cx, (ts, bid, ask), 0)
rec = np.rec.fromarrays([ts, bid, ask]); _, keep = np.unique(rec, return_index=True); keep.sort()
dd = S.tick_replay(LX, cx, (ts[keep], bid[keep], ask[keep]), 0)
key = lambda t: (t["signal_close"], round(t["entry_ask"], 2), t["exit_time"], round(t["exit_bid"], 2), round(t["R_net"], 6))
out["duplicate_ticks"] = dict(ticks_as_run=int(len(ts)), ticks_after_dedup=int(len(keep)), removed=int(len(ts) - len(keep)),
                              trades_as_run=len(base), trades_dedup=len(dd), identical_trades=[key(t) for t in base] == [key(t) for t in dd])
# ---- (b)
import build_bars as B
tmp_out = os.path.join(TMP, "rebuild_bars"); os.makedirs(tmp_out, exist_ok=True)
B.OUT = tmp_out; B.MANIFEST = os.path.join(tmp_out, "manifest.csv"); B.TMP = os.path.join(TMP, "rebuild_zip"); os.makedirs(B.TMP, exist_ok=True)
class Local:
    def __init__(self, path): self.f = open(path, "rb")
    def read(self, n=-1): return self.f.read(n)
    def __enter__(self): return self
    def __exit__(self, *a): self.f.close()
def fake_urlopen(url, timeout=None, context=None):
    return Local(os.path.join(TICKS, url.rsplit("/", 1)[1]))
B.urllib.request.urlopen = fake_urlopen
res = []
for z in sorted(glob.glob(os.path.join(TICKS, "Exness_BTCUSDm_*.zip"))):
    bn = os.path.basename(z); y, m = bn.split("_")[2], bn.split("_")[3][:2]
    B.process(int(y), int(m))
    a = gzip.open(os.path.join(tmp_out, f"BTCUSDm_{y}_{m}.csv.gz")).read(); b = gzip.open(os.path.join(REPO, "research/exness_validation/data/bars15m", f"BTCUSDm_{y}_{m}.csv.gz")).read()
    res.append(dict(month=f"{y}-{m}", rebuilt_sha256=hashlib.sha256(a).hexdigest(), committed_sha256=hashlib.sha256(b).hexdigest(), identical=a == b))
out["bar_rebuild_from_raw_ticks"] = res
json.dump(out, open(sys.argv[2], "w"), indent=1); print(json.dumps(out, indent=1))
