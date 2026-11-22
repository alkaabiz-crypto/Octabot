"""PRE-REGISTERED PROTOCOL - BTC volatility-compression / breakout research (paper only, no live orders).

DATA: Binance BTCUSDT spot klines 2018-06-01 .. 2026-11-08 (15m, 1h, 4h, 1d) from data-api.binance.vision
      (official public mirror). Exness BTCUSDm history unavailable. Exchange halts left as gaps.
ENTRY TIMEFRAMES: 1H entries with 4H trend confirmation; 15M entries with 1H trend confirmation.
TREND CONFIRMATION (all models): last CLOSED higher-TF candle close > EMA200 for longs, < EMA200 for shorts.
ENTRY MODELS (textbook parameters, NOT optimized):
  M1 BB_SQUEEZE   Bollinger(20, 2) bandwidth in its lowest 20% of the last 120 bars on any of the previous 5 bars,
                  then close crosses above the upper band (long) / below the lower band (short).
  M2 DONCHIAN20   close crosses above the highest high of the previous 20 bars (long) / below lowest low (short).
  M3 ATR_CONTRACT ATR14/ATR100 < 0.75 on any of the previous 5 bars (contraction), then true range > 1.5 x ATR14 of the
                  previous bar (expansion) and close beyond the previous 10-bar high (long) / low (short).
  M4 DONCHIAN_VOL M2 + volume > 1.5 x average volume of the previous 20 bars (participation confirms breakout).
  M5 TREND_DC55   close crosses the previous 55-bar high/low AND higher-TF EMA200 rising (long) / falling (short)
                  over the last 10 higher-TF candles (trend-following breakout).
  M6 SQUEEZE_VOL  M1 + volume > 1.5 x average volume of the previous 20 bars (compression then participation).
EXECUTION: signal evaluated on a CLOSED candle; entry at the OPEN of the next 15m candle. One position at a time per variant.
STOPS (risk R = entry - initial stop):
  FIXED  stop 2 x ATR14 (entry TF, signal candle), target 2R.
  TRAIL  initial stop 2 x ATR14; at every entry-TF close stop = max(stop, highest close since entry - 3 x ATR14); no target.
  Intrabar: if stop and target are touched in the same 15m candle, the stop is assumed first.
DIRECTIONS: long and short tested as separate variants. 6 models x 2 TFs x 2 directions x 2 stops = 48 variants.
COSTS (round trip, % of price; HYPOTHETICAL, Exness costs unverified): low 0.02%, mid 0.05%, high 0.10%. Swaps excluded.
SIZING for returns: 0.5% of equity risked per trade, compounding. Metrics also reported in R.
WALK-FORWARD: 11 half-year windows 2020H1 .. 2025H1. Nothing is fitted, so every window is out-of-sample.
              Positions are force-closed at window end. 2018-06 .. 2019-12 used only for indicator warm-up.
FINAL HOLDOUT: 2025-07-01 .. data end. Untouched until the walk-forward pass list is locked (written + SHA256).
PASS (walk-forward, mid cost): >= 60 trades, expectancy > 0 with t-stat >= 2.0, PF >= 1.2, positive expectancy in
      >= 7 of 11 windows, expectancy > 0 at high cost. HOLDOUT: expectancy > 0 and PF >= 1.1 at mid cost, >= 10 trades.
      Variants are never ranked or chosen by training/in-sample return. If nothing passes both: NO EDGE FOUND.
BASELINES: buy-and-hold BTC and no-trade (0%) over the same windows.
REGIMES (causal, at entry): daily close vs EMA200 and 20-day EMA200 slope -> bull / bear / sideways.
"""
import calendar
STEP = {"15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}
HIGHER = {"1h": "4h", "15m": "1h"}
MODELS = ["M1_BB_SQUEEZE", "M2_DONCHIAN20", "M3_ATR_CONTRACT", "M4_DONCHIAN_VOL", "M5_TREND_DC55", "M6_SQUEEZE_VOL"]
STOPS = ["FIXED", "TRAIL"]
DIRS = [1, -1]
COSTS = {"low": 0.0002, "mid": 0.0005, "high": 0.0010}
RISK = 0.005
def ts(y, m, d=1): return calendar.timegm((y, m, d, 0, 0, 0))
WINDOWS = [(f"{y}H{h}", ts(y, 1 if h == 1 else 7), ts(y if h == 1 else y + 1, 7 if h == 1 else 1)) for y in range(2020, 2026) for h in (1, 2)][:11]
HOLDOUT = ("HOLDOUT", ts(2025, 7), 10 ** 11)
PASS = dict(min_trades=60, min_t=2.0, min_pf=1.2, min_pos_windows=7, holdout_min_trades=10, holdout_min_pf=1.1)
