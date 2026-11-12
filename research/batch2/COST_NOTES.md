# Batch 2 cost notes (information only; the pre-registered costs are unchanged)

**2026-11-12, swap on Exness BTCUSDm / ETHUSDm**
- Exness's public fees page and its BTCUSD page advertise **swap-free** trading on Bitcoin and Ethereum CFDs: www.exness.com/fees/ and www.exness.com/crypto/btcusd/, found by web search. Direct fetching of those pages from this server is blocked (HTTP 403).
- The live swap table could not be checked: that needs the Exness terminal, and this project never connects to an account.
- **Consequence:** the pre-registered financing charges are probably conservative:
  - 0.03% of notional per day (primary);
  - 0.08% per day (stress).
  - On a 7-day hold (H2, H4) that is about 21 bp and 56 bp per trade.
- **Handling:**
  - The primary and stress costs stay exactly as pre-registered, and PASS/FAIL uses them alone.
  - At each evaluation, results are also shown with **zero financing** (spread costs only), labelled information-only.
  - If the user later confirms the live swap values from the app, they are added here, with the date.
