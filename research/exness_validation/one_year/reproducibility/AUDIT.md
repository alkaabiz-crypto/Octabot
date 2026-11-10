# Reproducibility and evidence audit: one-year Exness BTCUSDm backtest

Audit date: 2026-11-10. Study audited: commit **`e88fc432`**.

The audit changed nothing in the frozen strategy, the study outputs or the forward test. Every file in this folder is new.

## 1. Data source

| Item | Evidence |
|---|---|
| Source | Public Exness tick-history archive. URL pattern: `https://ticks.ex2archive.com/ticks/BTCUSDm/YYYY/MM/Exness_BTCUSDm_YYYY_MM.zip`. Per-month URLs are in `../../data/manifest.csv`. |
| Raw files | 12 zips covering 2025-11 to 2026-10, stored in the session scratch folder `/tmp/claude-0/-home-user-Octabot/5b2bd987-32bf-569e-9423-8a60d237f685/scratchpad/exness_ticks/`. They are NOT committed (415 MB) but can be re-downloaded from the URLs. |
| Sizes and SHA-256 | Per file in `raw_tick_files_evidence.csv`. **12/12 SHA-256 match** the values recorded when the bars were first built (`manifest.csv`). **12/12 tick counts match.** Exness publishes no checksums, so this proves the files are reproducible, not that they are authentic. |
| Content | CSV columns `Exness, Symbol, Timestamp (UTC, ms), Bid, Ask`. Symbol is **BTCUSDm** only. **Real bid and ask ticks** were used: 36,683,952 ticks, 0 with ask < bid, 0 zero or negative prices, 0 out of order. |
| Coverage | 2025-11-01 00:00:01 to 2026-10-31 23:59:59 UTC. |
| Missing periods | 2025-11-30 18:29 to 2025-12-01 00:00 (about 5.5 h). **2026-03-30 to 2026-03-31, two full days.** Smaller gaps are listed in `../results/one_year_results.json` under `data_quality`. No trade was open across any gap. |
| Duplicate ticks | **73,122 exact duplicate rows** (0 to 27,586 per month; June 2026 has the most). Removing them gives **identical 64 trades** (`dedup_and_bar_rebuild.json`). |
| Spread finding | **The spread is constant within each month** (median = max): 18 USD Nov–Mar, 14 Apr–May, 10 Jun–Sep, 6.4–10 Oct. This archive therefore carries a fixed quoted spread per period, not a live variable spread. Real spreads during volatility may be wider, and **the backtest cannot show that.** |
| Non-Exness data | **Binance BTCUSDT** candles (`research/btc_breakout/data`) were used **only** for the separate Exness-vs-Binance comparison columns. They were never used for Exness signals, fills or results. Indicator warm-up used Exness bars from 2019-01 (`../../data/bars15m`). |

## 2. Trades (`trade_ledger_64_trades.csv`, SHA-256 `1b696566…f9a8`; `trade_analysis.json`)

- **Trade #38 produced most of the profit:**
  - signal close 2026-08-19 14:00 UTC;
  - entry ask 64,967.98 (spread 10.00); initial stop 64,535.71 (risk 432.27 per BTC);
  - exit 2026-08-21 11:34:44 at bid 76,400.80 (final trailing stop 76,412.94); held **45.6 h**;
  - **+26.448 R = 107.8% of the year's total R**; 2 assumed swap-days, cost unknown.
- **Reconciliation:**
  - all 64 trades: **24.5277 / 64 = +0.3832 R**;
  - excluding #38: **(24.5277 − 26.4481) / 63 = −0.0305 R**.
- **After measured spread and tick slippage** (commission 0, unverified; swaps unknown and not deducted):

  | Metric | Value |
  |---|---|
  | Win rate | 35.9% (23 wins / 41 losses) |
  | Profit factor | **1.738** (**0.942 without #38**) |
  | Average win / average loss | +2.512 R / −0.811 R (ratio 3.10) |
  | Median trade | **−0.574 R** |
  | Max drawdown at 0.5% risk | 4.58% |

## 3. Reproducibility

The check reran the study in a clean worktree of `e88fc432` (zero local modifications). The checker scripts called below live in this folder, `research/exness_validation/one_year/reproducibility/`.

```
git worktree add --detach <dir> e88fc432
cd <dir> && STUDY_TMP=<tmp> TICK_DIR=<raw zip dir> python3 -I research/exness_validation/one_year/src/study.py
#   exit 0, runtime 1m45s; logs: rerun_stdout.log, rerun_stderr.log; git status afterwards: clean
python3 -I data_evidence.py <raw zip dir> research/exness_validation/data/manifest.csv raw_tick_files_evidence.csv
STUDY_TMP=<tmp> TICK_DIR=<raw zip dir> python3 -I checks_dedup_and_bars.py <repo> dedup_and_bar_rebuild.json
python3 -I trade_analysis.py research/exness_validation/one_year/trades/tick_replay_trades.csv trade_analysis.json
```

| Check | Result |
|---|---|
| All 5 study outputs (results JSON and 4 trade ledgers) | **Byte-identical** to `e88fc432` (`output_hashes.csv`) |
| Code hashes | `engine.py` `1cd38027…`, `protocol.py` `ed709512…`, `study.py` `b90f2491…` (`code_hashes.csv`) |
| 15m bid/ask bars rebuilt from raw ticks with the original `build_bars.py` | **12/12 months byte-identical** to the committed bars |
| Frozen engine vs independent candle replay | 64/64 trades identical (recorded in the study) |

## 4. Forward test (Binance proxy), untouched

- The frozen files are unchanged since `ce2e8c57`.
- 10 hourly runs have processed 23 one-hour candles (2026-11-09 07:00 to 2026-11-10 06:00 UTC), with a contiguous watermark chain and every data check passed.
- 0 signals and 0 trades, because the 4H trend filter is down.
- `signals.csv` and `trades.csv` are created only when the first row exists. Candles and data checks are logged in `run_log.csv`, `DAILY_LOG.md` and `candles_*_forward.csv.gz`.
- Zero trades so far is neither failure nor success. It only shows that conditions have not met the frozen entry rule.

## 5. Decision

| Question | Answer |
|---|---|
| Is the backtest independently reproducible? | **Yes.** A clean checkout of `e88fc432` with the verified raw data reproduces every output byte-for-byte, and the bars rebuild identically from the raw ticks. Reproducibility proves the computation is correct and deterministic. It does not prove the strategy is right. |
| Is the data source verified? | **Partly.** The files come from the public Exness tick archive at recorded URLs, are internally consistent, and re-download identically. However, Exness publishes no checksums to verify authenticity. The archive spread is a fixed per-period value, not the live spread. There are two full missing days and 73k duplicate ticks; the duplicates do not affect results. |
| Is there enough evidence to proceed to Exness demo testing? | **Yes, as a controlled demo test only. Not to live trading.** The study does not show the strategy is profitable: t = 0.86, both 95% confidence intervals include zero, and the result without one trade is −0.03 R. A demo test is the right next step because it measures what the backtest cannot: real variable spreads, actual fills, swaps, commission and broker volume limits. It still needs the MT5 demo connection, which is unavailable from this cloud environment (see `../../forward_demo/CONNECTION_REQUIREMENTS.md`). |
