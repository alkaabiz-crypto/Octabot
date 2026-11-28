# Freeze note: retrospective ADP investigation

**Freeze date: 12 November 2026.** Branch `claude/dazzling-albattani-j6uys7`. The closing amendment was committed as `1e7632de`.

## Scope

This freezes the retrospective ADP-to-NFP investigation:
- PROTOCOL.md addendum 5 (the original study);
- the robustness audit (`ROBUSTNESS_ADP.md`);
- the closing amendment in the same file.

## Final conclusions

- **Prediction.**
  - ADP's beat or miss against its consensus matched the sign of the NFP consensus surprise in 58 of 120 releases (addendum 5) and 58 of 122 (audit).
  - Split by ADP's 2022 method change: 2016-01 to 2021-12, 37/71 (52.1%, 95% CI 40.7–63.3%, two-sided p 0.81); 2022-01 to 2026-06, 21/51 (41.2%, CI 28.8–54.8%, p 0.26).
  - Neither period differs significantly from 50%.
- **Trading before the release** in the textbook direction (entry 1–60 minutes before NFP, exit 5–60 minutes after) did not pay in gold, EUR/USD, GBP/USD or USD/JPY.
  - The addendum-5 means were −0.07R to −0.13R per trade.
  - In the audit, 3 of 192 variants had raw p ≤ 0.05, where about 10 are expected by chance. None survived the false-discovery correction.
- **The risk-unit correction** (2016–19, 46.7 to 60 minutes) changes no sign that matters for the verdict, no significance and no conclusion.
- **Exploratory only.** Gold 2020–26 with the reversed direction gave +0.38R to +0.45R per trade in 3 variants. This is not evidence of an edge. It is carried forward as a pre-registered prospective hypothesis (FORWARD_TEST_PLAN.md, section C).

## Limitations

- **Power.** Hit rates below about 62%, and trade edges below about 0.5R per trade, could not be detected.
- **Data.**
  - The consensus forecasts come from third-party copies of the Investing.com calendar (Kaggle, Hugging Face; licences not stated). They have no forecast timestamps.
  - One conflicting ADP record (March 2023) did not affect any sign.
- **Prices.** Exness bid/ask only, with no extra slippage. 2016–19 uses tick data; 2020–26 uses 15-minute candles. The R definition differs slightly between the two (documented).
- **Scope.** Only four Exness markets and one predictor (ADP) were tested. The untested alternatives are listed in `ROBUSTNESS_ADP.md`, section 5.

## Original results unchanged

`git diff 1619591a -- research/news_surprise/reports/adp_preposition.json research/news_surprise/src/adp_preposition.py` is empty (checked on 2026-11-12). The robustness results (`reports/adp_robustness.json`, commit `24d32f8c`) were not modified by the closing amendment, which wrote separate files.

## Frozen files in the repository (paths relative to `research/`)

| Kind | Path | SHA-256 | Bytes |
|---|---|---|---|
| source | `news_surprise/src/adp_preposition.py` | `60547a5c96df578598e6ab3bad06d56adb66ee69765ab9b273323144847fbe4c` | 6095 |
| source | `news_surprise/src/adp_robustness.py` | `8983775774b46df2c64b797acf71b5ca4580e22274cddc2619ccb42319207cf3` | 12222 |
| source | `news_surprise/src/adp_closing.py` | `ab068908088d74e33f55473420755c0869643b38346dc6618f6e373c966f630a` | 6689 |
| source | `news_surprise/src/adp_riskunit_check.py` | `a7123f3ca2a75490317a67bc4e7570d702db0a41ce0393b96c70eefdff5d1e68` | 5420 |
| source | `news_surprise/src/replicate_2016.py` | `81075a97780863593376523a7065a4ec95245de9a8db5c512b092cb1ebebc0ba` | 6361 |
| source | `news_surprise/src/ticks.py` | `fe3cc91877a58360374c265a161a79d986550350245909929b7df86ce1f51bf0` | 5191 |
| source | `news_surprise/src/run.py` | `9ed2376ea0a8577c9f7fa07953aa04173f34ec7ad96bdbc1a4f4429302d46b6f` | 7229 |
| source | `news_markets/src/run.py` | `d4c2296d1e35b1fbffab5bcb1ef82c0527e0c303058b70fd5d30f479e4c84ef0` | 10869 |
| source | `gold_kst_news/src/engine.py` | `82685413ceb030e69ee331564e85f893e1c7f856d536ae3d530eefb7671a7c70` | 11897 |
| source | `oil_rsi_vwap/src/oil.py` | `7ac14110df94b3853ae0f9ccf20c8f14668865627569877128014684eb7f6d87` | 7183 |
| source | `rsi_vwap_study/src/study.py` | `77926cedff1d3f60625e026affa90edd973af42a886386ff25e16db6e2ec1c9d` | 12344 |
| source | `long_history/src/report.py` | `afbb53b3b27dce05d8d757ec1aba216c2b2adf11f1ced57862f7d71ef11ef4e8` | 4604 |
| source | `oil_rsi_vwap/src/build_bars.py` | `42031276acaf912b42c6ec23374554ea31d79b9ce3e9ad4b360e4c9eb79291a0` | 4119 |
| protocol/docs | `news_surprise/PROTOCOL.md` | `355bcdd343eb8df53bc30ae9442572c762624841b7b5d23f331280a3334bb1c4` | 11179 |
| protocol/docs | `news_surprise/ROBUSTNESS_ADP.md` | `0b5657ae73eb30a7ce2f16313a683f41b8e806011e656138004ec1ac8a00798f` | 13498 |
| data (in repo) | `news_surprise/data/consensus_investing.csv` | `5ae9e4b146f37043f5ea311d82dbf4170eef4a9d4f28ba32b7e2461f80661755` | 11594 |
| data (in repo) | `news_surprise/data/consensus_investing_2015_2024.csv` | `333f34a9228393ccef2ed1c78c931ccd4a5523072a57e3289b818d83aeb7bbcc` | 18291 |
| data (in repo) | `gold_kst_news/data/nfp_releases.csv` | `1e6135c325ce7724e0ab1a812a90b2b80631bdb01240e2024936cbf59958c194` | 1275 |
| data (in repo) | `gold_kst_news/data/cpi_releases.csv` | `9fb6389e6b4480b5f603a45be238f1349f5ccf127fb63fac3f18eaca82af5524` | 1290 |
| data (in repo) | `gold_kst_news/data/fomc_decisions.csv` | `90392498a08a1e7d2d0d07895bbe4b0fe38276a87eb2486cc6591e7ab3738cd1` | 1926 |
| result | `news_surprise/reports/adp_preposition.json` | `0049654a98d002a6494d03823b34e0a2a788c7fa41f632fbd533983efb22dccf` | 1255 |
| result | `news_surprise/reports/adp_robustness.json` | `3acb81cf298556e7febca60f8d1407338acf966a83fb310d360fcd9753e918d6` | 68000 |
| result | `news_surprise/reports/adp_closing.json` | `0817905fa3b449bc04e758fa9c433d52c4d20e074090867787efdec72e57a282` | 3560 |
| result | `news_surprise/reports/adp_riskunit_check.json` | `a541dff93924f3861e98891bdda085223661da096b1c8207d98e23ca2b521115` | 3416 |
| data manifest | `news_surprise/reports/adp_data_manifest.csv` | `8c9246d6c8c21bf4fa1ab26c2b8797644eacfb6996b4e635f3c6958e90c0fcc8` | |

## External data, not committed (hashes in the manifest)

These files sit in the session's scratch storage and are **not in the repository**: their licences are unclear, and the tick data is large. They will be lost when the container is recycled. Each can be rebuilt from its public source, and the manifest records the SHA-256 needed to verify a rebuild.

| Dataset | SHA-256 | Bytes |
|---|---|---|
| Kaggle iscorod92/economic-calendar-us-2015-2024 (Economic_calendar_US.csv) | `08277d8043e84d29ae1ebf698f3f54ed07b55fe193663c21ac8d35e3416aeaa8` | 4796819 |
| Kaggle youneseloiarm/global-economic-calendar (Calender_data.csv) | `6cd7fa290c0b3d92992a95db5b5d41a7e5a3e31c85954afed02104c06bb962b6` | 43626780 |
| Hugging Face thomas819/eurusd-dax-calendar-data (calendar.csv) | `b81c0371c79457e0f24e4dc52b7fd3362ca1579693a3c287c50fed4da197af5d` | 4515344 |
| Exness XAUUSDm 15-minute bid/ask candles 2020-2026 (built from ticks.ex2archive.com) | `38dc2a242edd6e861a40f9f8a853d95688a0fa49bc8d203ec584e26f0c57c612` | 4639140 |
| Exness EURUSDm 15-minute bid/ask candles 2023-2026 (built from ticks.ex2archive.com) | `f96ce7443d37c7cfa557a2745322993ec5742c1a354e53b809684b7cdcadc4ff` | 1949741 |
| Exness GBPUSDm 15-minute bid/ask candles 2023-2026 (built from ticks.ex2archive.com) | `17864dda38d75b1a2f6243e301178ccc243811c9ec62651f31ae422d9311562b` | 2038068 |
| Exness USDJPYm 15-minute bid/ask candles 2023-2026 (built from ticks.ex2archive.com) | `a4f03dee794daaf18a0051e8597ed18358cc7b1ad7a8a56ecd03eb52ed039303` | 2071943 |
| 384 Exness tick-window cache files for the 2016–19 NFP releases (`*_win2.json`: T−3700 s to T+1000 s; `*_win3.json`: T−4600 s to T+1000 s) | per file in the manifest | |

## Freeze rule

- No further retrospective strategy searches, parameter optimisation, alternative entry or exit combinations, market selection or historical hypothesis mining are permitted in this investigation.
- Any future retrospective work must be separately authorised and separately documented, in new files, outside this investigation.
- Prospective tests (FORWARD_TEST_PLAN.md) read these files but must not modify them. A changed hash means the frozen record has been altered.
