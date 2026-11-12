"""Check that no frozen file changed since the freeze (FREEZE.md). Exit code 1 and a FREEZE VIOLATION list on any mismatch.

Usage (repository root): python3 -I research/theory_library/verify_freeze.py
"""
import hashlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bad = []
for line in open(os.path.join(ROOT, "research", "theory_library", "FREEZE_MANIFEST.sha256")):
    h, f = line.rstrip("\n").split("  ", 1); p = os.path.join(ROOT, f)
    if not os.path.exists(p): bad.append(f"MISSING {f}")
    elif hashlib.sha256(open(p, "rb").read()).hexdigest() != h: bad.append(f"CHANGED {f}")
if bad: print("FREEZE VIOLATION:"); print("\n".join(bad)); sys.exit(1)
print("freeze intact:", sum(1 for _ in open(os.path.join(ROOT, "research", "theory_library", "FREEZE_MANIFEST.sha256"))), "files match")
