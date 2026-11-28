"""Frozen configuration of the gold KST + session VWAP BUY paper test. Never edit after the first commit."""
SYMBOL = "XAUUSDm"
START_UTC = 1794441600               # 2026-11-12 00:00 UTC: only legs entered at or after this count
WARMUP_FIRST_MONTH = "2026-09"       # data used to warm up KST, ATR and VWAP; no legs counted from it
# (stop_atr, trail_atr, breakeven, time_h, lose_h, news) -- see research/gold_kst_news/PROTOCOL.md
PRIMARY = ("CHOSEN_48H_TIME_STOP", (0.0, 0.0, 0, 48, 0, "NONE"))   # pre-registered choice of the exit grid
# recorded for comparison only: (name, exit params, entry filter from gold_kst_news/src/ideas.py or None)
SHADOWS = (("ORIGINAL", (0.0, 0.0, 0, 0, 0, "NONE"), None),
           ("DOLLAR_FALLING", (0.0, 0.0, 0, 0, 0, "NONE"), "DOLLAR_FALLING"),   # nearest misses of round 2 (IDEAS.md)
           ("VOL_LOW", (0.0, 0.0, 0, 0, 0, "NONE"), "VOL_LOW"))
CHECKPOINTS = (50, 100, 150, 200)
FUTILITY_AT = 100                    # stop as failed if PRIMARY expectancy <= 0 after this many legs
FINAL_AT = 200                       # the only decision point (about 1.7 years at ~120 legs a year)
FROZEN_SHA256 = {
    "gold_kst_news/src/engine.py": "82685413ceb030e69ee331564e85f893e1c7f856d536ae3d530eefb7671a7c70",
    "gold_kst_news/src/ideas.py": "d60f30f444b5b4d53ed8cc705e07189431ca3c69192d058a98ddc00135f7c0a4",
    "gold_kst_news/src/optimize.py": "8fcbc231f0db439a9f2389384c5652161d5c326b96b72f1a1e1be02a50f38e5e",
    "oil_rsi_vwap/src/oil.py": "7ac14110df94b3853ae0f9ccf20c8f14668865627569877128014684eb7f6d87",
    "rsi_vwap_study/src/study.py": "77926cedff1d3f60625e026affa90edd973af42a886386ff25e16db6e2ec1c9d",
    "oil_rsi_vwap/src/build_bars.py": "42031276acaf912b42c6ec23374554ea31d79b9ce3e9ad4b360e4c9eb79291a0",
}
