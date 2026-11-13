# Archival manifest: external data of the frozen ADP investigation

Written on 2026-11-12. It contains metadata only: no restricted data is stored in this public repository. The file-level SHA-256 values are in `reports/adp_data_manifest.csv`, which is frozen and listed in FREEZE_NOTE.md.

## Repository visibility

`alkaabiz-crypto/Octabot` is **public**: the GitHub API serves it without authentication. So it is **not** used as an archive for any third-party data.

## Classification

| Dataset | Files | Licence / terms found | Archive decision |
|---|---|---|---|
| Exness tick-window caches (from `ticks.ex2archive.com`) | 384 JSON files (196 `*_win2.json`, 188 `*_win3.json`) | Exness publishes the tick archive for public download; no licence is stated | **Archive privately** as the user's personal research copy. Do not redistribute publicly. |
| Exness 15-minute bid/ask candles built from the same archive | 4 files (XAUUSDm, EURUSDm, GBPUSDm, USDJPYm) | as above | **Archive privately** |
| Kaggle `iscorod92/economic-calendar-us-2015-2024`, version 1 (updated 2025-03-17) | `Economic_calendar_US.csv` | Licence "Other (specified in description)". The description grants nothing and says the data was "extracted from Investing.com". | **Restricted**: reference only |
| Kaggle `youneseloiarm/global-economic-calendar`, version 1 (updated 2025-10-26) | `Calender_data.csv` | The uploader labels it CC BY-NC-SA 4.0, but the content is Investing.com calendar data, whose terms restrict reproduction, so the uploader's right to license it is doubtful | **Restricted**: reference only |
| Hugging Face `thomas819/eurusd-dax-calendar-data`, revision `bd0d806d09be1380fbac69cbbf3dac6119745168` (modified 2026-08-02) | `calendar.csv` | "Unlicensed". Its own card says the calendar was copied from Investing.com and that Investing.com's terms restrict reproduction and redistribution | **Restricted**: reference only |

## Archivable set

- **Package.** `exness_adp_archive_2026-11-12.tar.gz`: 29,860,289 bytes, SHA-256 `a83f6c5804defa2974f74d232ba454b60b72d0c9db60f3f1edf6d6152ab00ff0`. It contains folders `ticks/`, `ticks3/` and `candles/`.
- **Integrity check.** It was unpacked into an empty folder on 2026-11-12, and all **388 of 388** files match `reports/adp_data_manifest.csv` (0 mismatches, 0 missing).
- **Status: NOT YET IN DURABLE STORAGE.** The package exists only in the session's temporary scratch storage. It needs a **private** repository owned by the user to be pushed to; it has not been pushed anywhere yet. This line is to be updated only after a push **and** a re-download check succeed.

## Restricted datasets: how to retrieve and verify

| Dataset | Retrieved (UTC) | SHA-256 of the file used | Bytes | Retrieval instructions |
|---|---|---|---|---|
| Kaggle US calendar | 2026-11-12 12:21:12 (zip download) | `08277d8043e84d29ae1ebf698f3f54ed07b55fe193663c21ac8d35e3416aeaa8` | 4796819 | `curl -L -H 'Authorization: Bearer <your Kaggle token>' https://www.kaggle.com/api/v1/datasets/download/iscorod92/economic-calendar-us-2015-2024 -o d.zip && unzip d.zip`, file `Economic_calendar_US.csv`. Alternatively `kaggle datasets download -d iscorod92/economic-calendar-us-2015-2024`. |
| Kaggle global calendar | 2026-11-12 12:21:09 (zip download) | `6cd7fa290c0b3d92992a95db5b5d41a7e5a3e31c85954afed02104c06bb962b6` | 43626780 | As above, with `youneseloiarm/global-economic-calendar`, file `Calender_data.csv` |
| Hugging Face calendar | 2026-11-12 12:09:02 | `b81c0371c79457e0f24e4dc52b7fd3362ca1579693a3c287c50fed4da197af5d` | 4515344 | `curl -L https://huggingface.co/datasets/thomas819/eurusd-dax-calendar-data/resolve/bd0d806d09be1380fbac69cbbf3dac6119745168/calendar.csv -o calendar.csv` (pinned to the revision used) |

**Verification.** Compute SHA-256 of the downloaded file and compare it with the table.
- A mismatch means the source changed. The frozen ADP results can then **not** be reproduced exactly from it.
- Kaggle serves only the latest dataset version unless one is requested explicitly. If version 1 is replaced, the original bytes may be unavailable.

## Already in the public repository (for the user's attention, not changed)

The repository was public before this manifest, and it already contains derived data from these sources:
- `news_surprise/data/consensus_investing.csv` and `consensus_investing_2015_2024.csv`: small extracts of Investing.com calendar values from the Hugging Face and Kaggle copies;
- Exness 15-minute candle files committed by earlier studies (for example `oil_rsi_vwap/data/`, `gold_rsi_vwap/data/`, `community_indicators/data/`).

They are left unchanged, because the research is frozen. The user may wish to make the repository private.

## Archived (2026-11-13), verified

- **Where:** the private repository `alkaabiz-crypto/octabot-data-archive-` (private; created by the user), folder `exness_adp_2026-11-12/`, commit `cb7b2a6`.
- **What:** `exness_adp_archive_2026-11-12.tar.gz` (29,860,289 bytes, SHA-256 `a83f6c5804defa2974f74d232ba454b60b72d0c9db60f3f1edf6d6152ab00ff0`), a copy of `adp_data_manifest.csv`, `SHA256SUMS` and `verify.py`.
- **Verification:**
  - after pushing, the repository was cloned fresh from GitHub into an empty folder;
  - `sha256sum -c` passed;
  - `verify.py` unpacked the archive and found **388 of 388** files matching the manifest (0 mismatched, 0 missing, 0 extra).
- **Not archived:** the three public calendar datasets (Kaggle ×2, Hugging Face). They are identified by SHA-256 in the manifest and can be re-downloaded.
