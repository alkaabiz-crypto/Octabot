# G6: which evidence may become a new strategy (written 2026-11-14 01:20 UTC, before any new backtest)

[`PLAN.md`](../PLAN.md) G6: only an INFORMATIVE indicator or a SUPPORTED / PARTLY SUPPORTED theory may become a new strategy candidate. **At most 3**, each pre-registered, never from a parameter search.

## Step 1: what qualifies

| Evidence | Category verdict | Qualifies? |
|---|---|---|
| IND-018 HAR volatility forecast | INFORMATIVE (volatility, not direction) | Yes, for **sizing only** |
| THE-001 previous-day zones + signal candle, S&P 500 | PARTLY SUPPORTED (S&P only) | Yes |
| THE-014 Coinbase premium = USD vs offshore USDT demand (BTC) | PARTLY SUPPORTED: positive against Binance and OKX USDT in every period; not against Bitstamp USD; not on ETH | Yes |
| IND-001 Coinbase premium z | WEAK | No: covered by THE-014 |
| THE-008 pre-holiday, THE-013 HAR long memory, STR-016 HMM USD/JPY | WATCH | No: WATCH does not qualify |
| THE-002, THE-006, THE-009, THE-015a, THE-016 | DECAYED | No: an effect that has gone is not a basis for a new strategy |
| Everything else | NONE / NOT SUPPORTED | No |

## Step 2: can each become a tradable rule after costs? (decided now)

| Evidence | Decision | Reason |
|---|---|---|
| IND-018 (sizing) | **No new strategy.** Already tested as STR-025 (MIXED); continues only as a read-only shadow on STR-023. | A second sizing candidate would be a variant search |
| THE-001 (S&P 500) | **No strategy.** | The effect is about +1.3 bp per signal over 4 h, below the S&P CFD's round-trip cost (about 1.7 bp). The full Theory #2 trading rule already lost on the S&P. Any rule that "makes it work" would require tuning holds or filters after seeing the data. |
| THE-014 (Coinbase premium) | **Yes: one new candidate, STR-026.** | The theory says the signal is **USD demand against offshore USDT demand**, so the most direct test of it is the premium against the **average of the two USDT venues** (Binance and OKX). Averaging two venues removes venue-specific noise. **Disclosed:** this choice was made after seeing checks B and C. That is why it must earn a forward test, and why its backtest is labelled reused data. |

**Result: one new candidate (STR-026), well within the limit of 3.** No other evidence qualifies. It is not padded to 3.

## Step 3: STR-026 pre-registration

**Rule.** Identical to STR-008 / H4 except for the reference price.
- *prem* = ln(Coinbase BTC-USD close / **mean(Binance BTCUSDT close, OKX BTC-USDT close)**), hourly. An hour is used only if all three venues have it.
- *z* over the previous 720 hours, excluding the current one; |*z*| ≥ 2 → follow for 24 h; one position at a time.

**Backtest.**
- Exness BTCUSDm bid/ask execution, protocol costs (primary 0.5× median spread; stress 1.5× plus 0.02% per day).
- Periods EARLY 2020–22, TRAIN, VALIDATION, TEST.
- Random-entry benchmark (1,000 sets). **All of it is reused data:** the component series were seen in H4 and checks B and C.

**Screen pass (needed to start a forward test):**
- mean > 0 in all 4 periods;
- TEST stress mean > 0;
- TEST p ≤ 0.05 against random entries;
- ≥ 30 TEST trades.

**If the screen fails:** STR-026 is REJECTED, and STR-008's forward test alone carries THE-014.

**If the screen passes, a forward paper test** like STR-008's:
- Coinbase plus Binance plus OKX public data, execution at the Binance 1-minute open, primary cost 0.10% per side;
- from the first hourly close ≥ **2026-11-14 03:00 UTC**;
- rule V2 with critical NW t = **2.24** (one test, 4 looks), mean ≥ +2 bp; futility stop if mean + 1.645·se < +2 bp.

**Relation to STR-008.** Both run, and they share most signals. They are reported side by side. It is **not** counted as independent confirmation of STR-008.

## Step 4: STR-026 backtest result (2026-11-14). **REJECTED at the screen**

Script `str_026/backtest.py`, output `str_026/backtest_results.json`.

| Period | Trades | Mean (bp) | Stress (bp) | p vs random |
|---|---|---|---|---|
| EARLY 2020–22 | 317 | +35.50 | +26.28 | 0.007 |
| TRAIN | 153 | +13.57 | +4.36 | 0.106 |
| VALIDATION | 80 | +57.75 | +48.53 | 0.015 |
| TEST | 132 | +20.52 | +11.29 | **0.090** |

- Positive in every period, but the TEST p is above the pre-registered 0.05, so **no forward test**.
- THE-014 continues to be judged by STR-008's forward test alone.
- The averaged reference did **not** improve on Binance alone (H4's TEST p was 0.011), so there is no reason to prefer it.

## G6 outcome

| Qualifying evidence | Outcome |
|---|---|
| IND-018 | Sizing only (STR-025, MIXED, shadow) |
| THE-001 | Not tradable after costs |
| THE-014 | STR-026 rejected at the screen; STR-008 forward test continues |

**No new strategy reached a forward test.** G6 is complete on 2026-11-14 (deadline 2027-02-28).
- The candidates alive for the overall goal are the forward tests already running: STR-023 and STR-008, plus the daily paper tests.
- New G6 candidates can be added only if new evidence qualifies, for example from the quarterly re-checks of THE-001 and THE-014.
