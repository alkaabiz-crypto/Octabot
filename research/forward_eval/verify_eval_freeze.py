"""Check the SHA-256 fingerprints of the frozen forward-evaluation files (EVAL_MANIFEST.sha256). Prints 'evaluation freeze intact'
or 'EVALUATION FREEZE VIOLATION' with every changed or missing file. Usage: python3 -I verify_eval_freeze.py"""
import hashlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
bad = []
for line in open(os.path.join(HERE, "EVAL_MANIFEST.sha256")):
    h, f = line.split(None, 1); f = f.strip(); p = os.path.join(ROOT, f)
    if not os.path.exists(p): bad.append(f"MISSING {f}")
    elif hashlib.sha256(open(p, "rb").read()).hexdigest() != h: bad.append(f"CHANGED {f}")
print("EVALUATION FREEZE VIOLATION:\n" + "\n".join(bad) if bad else f"evaluation freeze intact: {sum(1 for _ in open(os.path.join(HERE, 'EVAL_MANIFEST.sha256')))} files match")
sys.exit(1 if bad else 0)
