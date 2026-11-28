# Batch 2 pre-registration: new information families on BTC and ETH

**Committed before any Batch 2 signal data was downloaded or computed.**
- **T0** is this commit's timestamp.
- The user approved the review recommendations in `../batch2_review/REVIEW.md` §9 on 2026-11-12:
  - keep the 2025-01-01 data rule;
  - use this branch;
  - test H1–H4 on BTC/ETH, with FX carry deferred;
  - assume no Binance-futures access, so signals are traded on the CFD;
  - keep the repository private, with no new restricted data committed;
  - accept a 12–24 month forward wait.
- **Paper only.** No orders and no accounts.

## Common rules

**Markets and instruments**
- **Markets:** BTC and ETH only. The other 9 instruments are ineligible: no perpetual funding, futures basis, aggressor-side flow or options IV exists for them in any available source (`../batch2_review/REVIEW.md` §5).
- **Traded instrument:** Exness BTCUSDm / ETHUSDm CFDs.
- **Price used for evaluation, development and forward alike:** Binance spot BTCUSDT / ETHUSDT 1-minute klines from `data-api.binance.vision`, as a **proxy** for the CFD. It is the same source in both periods, so the comparison is consistent. Exness CFD prices are not live-accessible (the archive is monthly).

**Execution**
- At each decision time D, enter at the **open of the first 1-minute candle starting at or after D + 1 minute**.
- Exit at the open of the first 1-minute candle starting at or after the scheduled exit time.
- **Exits are time-based only.** No stops or targets, so no intrabar path is assumed.
- **One open position per hypothesis × coin.** Signals that arrive while a position is open are ignored.

**Costs** (in bp of price; spreads are the Exness Oct 2026 medians, `../batch2_review/REVIEW.md` §1: BTCUSDm 0.79 bp, ETHUSDm 4.13 bp)

| | Round-trip cost | Financing (the Exness swap is unknown) |
|---|---|---|
| **Primary** | 1.5 × spread (spread + 0.5 × spread slippage): **BTC 1.19 bp, ETH 6.20 bp** | 0.03% of notional per day held |
| **Stress** | 3 × spread: **BTC 2.37 bp, ETH 12.39 bp** | 0.08% per day |

**Information timing:** each input is used only after its real availability time.
- **Hyperliquid funding:** the hourly rate stamped at t is used only at or after t.
- **Binance and Deribit candles:** a candle is used only after its close.
- **DVOL:** the close of the hourly bar ending at D.

**Periods**
- **DEVELOPMENT:** 2025-01-01 00:00 UTC → T0.
  - **Label:** *previously inspected target series. BTC/ETH prices in this window were examined by earlier studies. Exploratory only. It can never produce a PASS.*
  - **Use:** sanity checks and the power calculation only.
- **FORWARD (confirmatory):** starts at **E = the first 00:00 UTC at least 24 hours after T0**. No market data after T0 is examined before E, apart from the unchanged hourly reports of the existing paper tests.
- **Data rule:** all inputs start at 2025-01-01. Warm-up windows use 2025 data only, so the first signals appear later in 2025.

## Hypotheses (one setting each; no variants)

| ID | Mechanism | Data (and why) | Decision time D | Signal | Trade |
|---|---|---|---|---|---|
| **H1** Funding extremes reverse | Crowded leveraged positions unwind against the crowd | **Hyperliquid** BTC/ETH perpetual hourly funding (`fundingHistory`). Binance funding is not live-accessible from this server (HTTP 451), and its archive files are monthly. | daily 00:00 UTC | F = sum of the 24 hourly rates in (D − 24h, D]; z = (F − mean)/sd over the previous 90 daily values | z ≥ +2 → **SHORT**; z ≤ −2 → **LONG**; hold **72 h** |
| **H2** High basis precedes weak returns | Demand for leveraged longs, and crash risk (crypto carry) | **Deribit** quarterly future (expiring in Mar/Jun/Sep/Dec), using the nearest one with ≥ 30 days left, hourly close; spot = Binance close of the same hour | Monday 00:00 UTC | b = (F/S − 1) × 365 / days to expiry; p = percentile rank of b among the previous 26 weekly values | p ≥ 0.80 → **SHORT**; p ≤ 0.20 → **LONG**; hold **7 days** |
| **H3** Taker-flow momentum | Aggressive order flow carries information that the price absorbs slowly | **Binance spot** 1h klines (taker-buy base volume = aggressor-side buys) | every hour | I = (2 × taker-buy − volume)/volume of the hour ending at D; z over the previous 720 hourly values | z ≥ +2 → **LONG**; z ≤ −2 → **SHORT**; hold **4 h** |
| **H4** Volatility risk premium | Investors pay for crash insurance, and a high premium is earned later | **Deribit DVOL** (BTC, ETH), hourly close at D; RV30 = √365 × sd of the last 30 daily log returns of Binance closes at 00:00, in % | daily 00:00 UTC | VRP = DVOL − RV30; z over the previous 180 daily values | z ≥ +1 → **LONG**; z ≤ −1 → **SHORT**; hold **7 days** |

That gives **8 primary tests**: H1 to H4, each on BTC and ETH.

## Metrics and benchmarks

**Primary metric:** mean net return per trade, in bp of price, at primary cost.

**Also reported:**
- stress-cost mean;
- trade count, median, 95% CI, win rate and profit factor;
- simple sum and compounded return;
- max drawdown;
- buy and hold (B3), for information only.

**Benchmarks (1,000 draws each, seed 20261113 + CRC32 of the test ID)**

| | Benchmark | How a draw is built |
|---|---|---|
| **B1** | Random entry | The same sides and holding times, with each start placed at a random eligible decision time (hourly for H3, daily 00:00 for H1/H4, Monday 00:00 for H2) within the same period |
| **B2** | Placebo | The signal series is shifted in time by a random offset of at least 30 days, wrapping around, and the rules are re-applied |

**p-values (one-sided):** p = (1 + #draws with mean ≥ the observed mean) / 1,001.

## Forward decision rules (confirmatory)

**Horizon:**
- The power target is n_req = ((z₀.₉₉₃₇₅ + z₀.₈₀) × sd / δ)².
  - sd is the per-trade standard deviation of net returns in DEVELOPMENT.
  - δ = max(10 bp, 2 × the primary round-trip cost).
  - z₀.₉₉₃₇₅ is the one-sided α of 0.05/8 used for planning.
- **The evaluation date is the later of:**
  - the date the test has n_req closed trades;
  - 6 months after E.
- It is **capped at 24 months after E.**
- No decision is made before the evaluation date. Running numbers are monitoring only.

**Outcomes:**
- **PASS** needs all of:
  - forward mean > 0 at primary **and** stress cost;
  - B1 p survives **Holm–Bonferroni across the 8 tests at α = 0.05**;
  - B2 p ≤ 0.05;
  - n ≥ 30.
- **FAIL:** forward mean ≤ 0 at primary cost at the evaluation date, or B1 p > 0.5.
- **INCONCLUSIVE:** anything else, including n_req not reached by the 24-month cap.

**A PASS only justifies further paper testing at real Exness costs, not live money.**

## Programme-level multiple testing

- **Confirmatory error control:** Holm across the 8 forward tests. The forward data is new, and the hypotheses are fixed at T0.
- **Development results:** reported with Benjamini–Hochberg using the **cumulative programme count** in `../RESEARCH_REGISTRY.md`, which is about 110,000 tests. In practice none can be significant.

## Data handling and licences

- **Storage:** raw inputs live **only in session scratch storage**. They are never committed. Only SHA-256 hashes of the files used and derived per-trade results are committed.
- **Licences:**
  - Binance (Binance Vision / data-api terms): non-commercial, no hosting or redistribution.
  - Deribit: "personal use only".
  - Hyperliquid: no licence found, so treated as personal research use.

## What would invalidate this batch

The weaknesses accepted in advance are those listed in `../batch2_review/REVIEW.md` §8:
- the target series was seen;
- low power for rare events;
- signal venue ≠ execution venue;
- the Exness swap is unknown (proxied by the financing cost);
- timestamp conventions;
- data revisions.

**Any change to these rules after T0 needs a dated amendment, and a changed test restarts its forward clock.**
