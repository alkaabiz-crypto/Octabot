"""High-power look-ahead scan of the event-driven (Book-based) frozen theories: 3 seeds x 20 cuts. A difference before the cut is
classified as TRUNCATION if the only change is a final trade that is still open at the end of the data in one version."""
import json, sys, numpy as np
sys.path.insert(0, "."); EXT, OUT = sys.argv[1:3]; sys.argv = [None, EXT, "/dev/null"]
import causality_scan as CS
E, T, TF, TG = CS.E, CS.T, CS.TF, CS.TG
EVENT = {"A13", "B7", "B8", "B9", "B10", "C1", "C2", "C3", "C4", "C5", "C6", "D1", "D2", "D3", "D4", "D5", "D6", "E1", "E2", "E3", "E4",
         "F6", "F7", "F8", "F9", "F10", "F11", "F12", "G1", "G2", "G13", "G14"}
REG = [r for r in T.REGISTRY + TF.REGISTRY_F + TG.REGISTRY_G if r[0] in EVENT]; mkts = ("XAUUSDm", "US500m", "BTCUSDT"); rep = {}


def runreg(data):
    E.base = lambda mk: data[mk]; E.candles.cache_clear(); out = {}
    for tid, fam, tfs, ms, fn in REG:
        for mk in mkts:
            if mk not in ms: continue
            for tf in tfs:
                if E.candles(mk, tf) is None: continue
                res = fn(mk, tf)
                if res: out[f"{tid}|{mk}|{tf}"] = (res[0].m.values.copy(), list(res[1].rows))
    return out


for seed in (21, 22, 23):
    A = runreg({k: CS.frame(k, seed) for k in mkts})
    for j in range(20):
        cut = CS.START + int(CS.DAYS * 1440 * (0.2 + 0.03 * j)) + 7 * 60 + 23 + 37 * j
        B = runreg({k: CS.frame(k, seed, cut, seed + 900 + j) for k in mkts})
        for key, (cm, ra) in A.items():
            rb = B[key][1]; kc = int(np.searchsorted(cm, cut, side="right")) - 1
            ent = lambda rows: [(r[0], r[2], round(r[3], 9)) for r in rows if r[0] < kc]
            ext = lambda rows: [(r[1], round(r[4], 9)) for r in rows if r[1] < kc]
            r = rep.setdefault(key, dict(cuts=0, decision_changed=0, examples=[])); r["cuts"] += 1
            if ent(ra) != ent(rb) or ext(ra) != ext(rb):
                r["decision_changed"] += 1
                if len(r["examples"]) < 2:
                    ea, eb = ent(ra), ent(rb); k0 = next((i for i in range(min(len(ea), len(eb))) if ea[i] != eb[i]), min(len(ea), len(eb)))
                    r["examples"].append(dict(seed=seed, cut_candle=kc, original=ea[k0:k0 + 2], changed_future=eb[k0:k0 + 2]))
byt = {}
for k, v in rep.items():
    t = k.split("|")[0]; b = byt.setdefault(t, [0, 0]); b[0] += v["decision_changed"]; b[1] += v["cuts"]
json.dump(dict(by_theory=byt, detail=rep), open(OUT, "w"), indent=1)
for t, (a, b) in sorted(byt.items(), key=lambda x: -x[1][0]): print(t, f"{a}/{b} cuts changed pre-cut decisions")
