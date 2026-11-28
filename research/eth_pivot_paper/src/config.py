"""Frozen configuration of the Pivot Reversal BUY paper test on ETH (copy of the BTC test, started after the 2026-11-12 audit). Never edit after the first commit."""
SYMBOL = "ETHUSDm"
STRATEGY = "PIVOT_REVERSAL"          # TradingView built-in "Pivot Reversal Strategy", leftBars 4, rightBars 2, 1H
DIRECTION = 1                        # BUY legs only
START_UTC = 1794441600               # 2026-11-12 00:00 UTC: only legs entered at or after this count
WARMUP_FIRST_MONTH = "2026-10"       # data used to warm up pivots and ATR; no trades counted from it
CHECKPOINTS = (50, 100, 200, 300, 400)
FUTILITY_AT = 200                    # stop as failed if expectancy <= 0 after this many legs
FINAL_AT = 400                       # the only decision point
FROZEN_SHA256 = {
    "tradingview_builtins/src/builtin_strategies.py": "e43775aa29d8273c2d09fa66949a9a35f170bf0c6b38537c9759f6d6b3fc131b",
    "tradingview_originals/src/ports.py": "896b45704d0be66ae8a77fe4b4005d6ef72e636333fda37dccceb7e7c2828168",
    "oil_rsi_vwap/src/oil.py": "7ac14110df94b3853ae0f9ccf20c8f14668865627569877128014684eb7f6d87",
    "rsi_vwap_study/src/study.py": "77926cedff1d3f60625e026affa90edd973af42a886386ff25e16db6e2ec1c9d",
    "indicator_scan/src/scan.py": "af2ae6d1c9034cc73943e5b5d32421de0652aae81a1c03777cee289a555eeff7",
    "oil_rsi_vwap/src/build_bars.py": "42031276acaf912b42c6ec23374554ea31d79b9ce3e9ad4b360e4c9eb79291a0",
    "audit/src/seq_held.py": "56cfd1b38a855ee067b9514a742fc8b15bd508b74d1c0d65eaf436090f222740",
    "long_history/src/fast_bench.py": "8feb06e45427731ca436e31d8d46c16546277f96c17422560509a6ba4d5bae5b",
}
