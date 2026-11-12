# New discovery program

An independent research program for new strategies and indicators. It reads earlier studies only to avoid repeating them. It **never modifies, pauses or replaces** any existing study, frozen result or active paper test.

- `PROTOCOL.md`: the experimental process every idea goes through.
- `INSTRUMENTS.md`: the exact instruments, symbols, price sources and their limits.
- `REGISTRY.csv` / `REGISTRY.md`: every experiment, including failures.
- `batch_NNN/`: pre-registration (`PREREG.md`, committed before results), code, results and summary.
- `src/`: shared code (data loading, costs, statistics).

**What was already tested elsewhere**, and is not repeated without a new hypothesis:
- this branch: 62 TradingView built-in indicators and 26 strategies, community indicators and filters on 33 markets; gold KST exits; news timing and news surprise; ADP;
- branch `claude/download-skill-27d08k`: 64 theories (trend, mean reversion, candle patterns, sessions/ICT, calendar effects, TradingView/YouTube systems, academic anomalies including intraday momentum, 20-day time-series momentum, overnight drift, turn of month, pre-FOMC), opening-range breakouts, session timing, zone reversals and a 2025+ shortlist.

**Promotion.** A candidate is only considered for a paper test after it passes its batch's out-of-sample, cost and multiple-testing rules **and** a separate robustness batch. Promoted strategies get their own new paper-test folder. Existing paper tests are never replaced.

**Data.** The Exness price data used here sits in session scratch storage and is **not archived**. It can be rebuilt from `ticks.ex2archive.com`, but that is only reproducible while Exness keeps serving the same files (see `../news_surprise/ARCHIVE_MANIFEST.md` for the archive status).
