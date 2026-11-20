# Results: gold KST + session VWAP exits and news rules

1152 combinations. Fit 2020-07 to 2024-12, test 2025-01 to the latest candle. Legs: count, win rate, expectancy, total, worst drawdown, z against random entries with the same exits.

| | Rules | Fit | Test |
|---|---|---|---|
| Original rule | no hard stop, no trailing stop, no news rule | 565, 40%, +0.115R, +65R, DD 29R, z +1.36 | 223, 51%, +0.399R (stress +0.321), +89R, DD 9R, z +1.37 |
| **Chosen (highest fit z)** | no hard stop, no trailing stop, time stop 48 h, no news rule | 565, 41%, +0.114R, +64R, DD 24R, z +1.65 | 224, 51%, +0.316R (stress +0.241), +71R, DD 8R, z +1.65 |
| Most profitable in fit | no hard stop, no trailing stop, no news rule | 565, 40%, +0.115R, +65R, DD 29R, z +1.36 | 223, 51%, +0.399R (stress +0.321), +89R, DD 9R, z +1.37 |

Verdict on the pre-registered rule: **improvement confirmed** (needs test expectancy > 0 at stress cost, z ≥ 1.645, and a smaller worst drawdown than the original rule's 8.8R).

The 20 best fit combinations, in the test period: median z +1.37, median expectancy +0.399R, 6 of 20 profitable.

## What each option does on average

Each value's average over every combination of the other options. z is against random entries with the same rules.

| Option | Value | Fit z | Fit expectancy | Test z | Test expectancy | Test worst drawdown |
|---|---|---|---|---|---|---|
| stop | 0 | +1.33 | +0.025R | +1.91 | +0.306R | 6.5R |
| stop | 1.5 | +1.22 | +0.001R | +2.15 | +0.288R | 5.4R |
| stop | 2 | +1.44 | +0.016R | +2.09 | +0.294R | 5.7R |
| stop | 3 | +1.18 | +0.011R | +2.08 | +0.304R | 6.1R |
| trail | 0 | +1.21 | +0.023R | +2.04 | +0.335R | 6.0R |
| trail | 2 | +1.52 | +0.009R | +1.94 | +0.237R | 5.5R |
| trail | 3 | +1.28 | +0.010R | +2.13 | +0.295R | 6.1R |
| trail | 4 | +1.17 | +0.011R | +2.13 | +0.325R | 6.0R |
| be | 0 | +1.21 | +0.011R | +2.08 | +0.305R | 5.8R |
| be | 1 | +1.38 | +0.016R | +2.04 | +0.291R | 6.0R |
| time | 0 | +1.28 | +0.012R | +2.03 | +0.316R | 5.9R |
| time | 120 | +1.27 | +0.012R | +2.03 | +0.316R | 5.9R |
| time | 48 | +1.33 | +0.016R | +2.11 | +0.261R | 5.9R |
| lose | 0 | +1.33 | +0.021R | +2.10 | +0.323R | 6.4R |
| lose | 12 | +1.29 | +0.015R | +2.26 | +0.316R | 5.9R |
| lose | 6 | +1.27 | +0.004R | +1.81 | +0.255R | 5.5R |
| news | no entry 2 h before to 1 h after news | +1.39 | +0.020R | +2.06 | +0.281R | 6.2R |
| news | no entry in the 24 h before news | +1.35 | +0.016R | +2.09 | +0.343R | 5.5R |
| news | no entry 2 h before to 1 h after news, close 30 min before news | +1.15 | -0.000R | +2.08 | +0.298R | 5.8R |
| news | no news rule | +1.29 | +0.018R | +2.01 | +0.269R | 6.1R |

## Does the first 15 minutes after news tell the direction?

Enter in (follow) or against (fade) the first 15-minute move after the release, exit 4 h after the release, 2×ATR stop. Compared with the same clock time on normal days.

| Event | Mode | Fit: events, win, E, z | Test: events, win, E, z | Gold's 4 h move after the event vs normal days |
|---|---|---|---|---|
| FOMC | follow | 36, 47%, +0.188R, +4.64 | 15, 40%, -0.025R, +0.23 | 2.9× ATR vs 0.5× ATR |
| FOMC | fade | 36, 42%, +0.092R, +2.64 | 15, 40%, -0.161R, -1.18 | 2.9× ATR vs 0.5× ATR |
| CPI | follow | 54, 43%, -0.089R, -0.24 | 21, 33%, -0.365R, -1.82 | 1.5× ATR vs 1.1× ATR |
| CPI | fade | 54, 35%, -0.054R, +0.27 | 21, 43%, +0.011R, +0.25 | 1.5× ATR vs 1.1× ATR |
| NFP | follow | 52, 40%, -0.112R, -0.35 | 21, 43%, +0.075R, +0.51 | 2.4× ATR vs 1.2× ATR |
| NFP | fade | 52, 40%, +0.054R, +0.94 | 21, 48%, -0.004R, +0.23 | 2.4× ATR vs 1.2× ATR |
