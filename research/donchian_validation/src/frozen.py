"""Read-only access to the frozen engine, with integrity checks. Never writes into the frozen checkout."""
import hashlib
import os
import sys

import config


class FrozenIntegrityError(Exception):
    pass


def check_integrity():
    root = config.FROZEN_DIR
    if not root or not os.path.isdir(root):
        raise FrozenIntegrityError("FROZEN_BTC_BREAKOUT is not set to the frozen research/btc_breakout directory")
    for rel, expected in config.EXPECTED_SHA256.items():
        with open(os.path.join(root, rel), "rb") as f:
            got = hashlib.sha256(f.read()).hexdigest()
        if got != expected:
            raise FrozenIntegrityError(f"{rel} differs from the frozen version ({got[:12]} != {expected[:12]})")
    sums = {}
    with open(os.path.join(root, "data", "SHA256SUMS")) as f:
        for line in f:
            h, name = line.split()
            sums[name] = h
    for name, expected in sums.items():
        with open(os.path.join(root, name), "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != expected:
                raise FrozenIntegrityError(f"{name} does not match data/SHA256SUMS")
    return True


def engine_module():
    """Import the frozen engine module (read-only)."""
    src = os.path.join(config.FROZEN_DIR, "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    import engine
    return engine


def lab():
    check_integrity()
    eng = engine_module()
    return eng.Lab(os.path.join(config.FROZEN_DIR, "data"))
