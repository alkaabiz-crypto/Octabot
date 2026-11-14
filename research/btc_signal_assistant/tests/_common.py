"""Shared test helpers: fixture loading and path setup."""
import gzip
import json
import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(TESTS_DIR)
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from signal_assistant import data

FIXTURE_DIR = os.path.join(TESTS_DIR, "fixtures")


def fixture_rows(tf):
    with gzip.open(os.path.join(FIXTURE_DIR, f"btc_{tf}.json.gz"), "rb") as f:
        return json.load(f)


def fixture_candles(tf):
    return data.Candles.from_rows(tf, fixture_rows(tf))


def write_fixture_dir(target_dir):
    """Write the fixtures as plain JSON files usable by ``run.py --offline``."""
    os.makedirs(target_dir, exist_ok=True)
    for tf in ("1h", "4h"):
        with open(os.path.join(target_dir, f"btc_{tf}.json"), "w") as f:
            json.dump(fixture_rows(tf), f)
    return target_dir


def synthetic_candles(tf, n, start_price=100.0, drift=0.0, amplitude=1.0, seed=7, start_t=1_700_000_000):
    """Deterministic pseudo-random candles (no numpy dependency)."""
    import random
    rnd = random.Random(seed)
    step = data.constants.STEP_SECONDS[tf]
    rows, price = [], start_price
    for i in range(n):
        o = price
        c = max(1.0, o + drift + rnd.gauss(0, amplitude))
        h = max(o, c) + abs(rnd.gauss(0, amplitude / 2))
        l = max(0.5, min(o, c) - abs(rnd.gauss(0, amplitude / 2)))
        rows.append([start_t + i * step, o, h, l, c, 10.0 + rnd.random()])
        price = c
    return data.Candles.from_rows(tf, rows)
