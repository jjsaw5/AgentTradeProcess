# Results — 0DTE vs 1DTE inside the session (computed 2026-10-03)

Pre-registration: `PREREG.md` (design + Addendum A, both written before these numbers).
Script `vehicle.py`, full output `output.txt`, per-trade prices `vehicle_rows.json`.
Real Robinhood 5-minute option bars (last trade), 0 checkpoints missing. **n = 16 trades, 8 sessions
(9/23-10/02), SPY + QQQ. Descriptive only, UNCALIBRATED (CLAUDE.md §7).**

## Scored against the pre-registration

| # | Expected | Got | Verdict |
|---|---|---|---|
| P1 | 1DTE costs 1.6-2.2x the 0DTE | 1.58-1.98x, median 1.79x | Consistent |
| P2 | wrong/STUCK: 1DTE loses less at every checkpoint; at 3:30 0DTE -60 to -100%, 1DTE -25 to -55% | at 3:30: 0DTE mean -56% (median -71%), 1DTE -17% (median -17%), 1DTE better on 10 of 12. At 10:15-12:00 both were still UP on average and 0DTE was ahead | Consistent at 3:30 (1DTE losses even milder than predicted). **Inconsistent at the earlier checkpoints** |
| P3 | right direction on a RAN day: 0DTE makes ~1.5-2x the 1DTE's % | 3:30: +182% vs +92% (2.0x); 10:15: +107% vs +57% (1.9x) | Consistent, n=4 |
| P4 | all days: both negative at 3:30, 1DTE less negative; within 10 pts at 10:15 | 3:30: 0DTE **+3.8%** mean (median -51%), 1DTE **+10.4%** (median -6%). 10:15: 0DTE +35%, 1DTE +19% (16 pts apart) | **Inconsistent**: means were positive, not negative. 1DTE-higher part consistent. 10:15 gap wider than predicted |
| P5 | 1DTE outcomes narrower at every checkpoint | 1DTE standard deviation is about half of 0DTE's at all four checkpoints | Consistent |

**Wrong at 3:30 (n=7): 0DTE -88% average, 1DTE -34%. The 1DTE lost less on all 7.**

## In dollars, one contract each (16 trades)
0DTE total **-$292**; 1DTE total **+$211**. On the 4 big winning days the dollars were nearly equal
(0DTE +$340/+$140/+$260/+$203, 1DTE +$283/+$146/+$250/+$196). On losing days the 1DTE usually lost fewer dollars,
even though it cost ~1.8x as much. One contract cost $98-262 (0DTE) and $178-414 (1DTE).

## Exploratory (NOT pre-registered; a hypothesis for a future test, not a finding)
The naive first-bar direction was ahead at 10:15-12:00 on most days (0DTE mean +34% to +38%) and gave it back by 3:30
(+4%). Examples on the 0DTE: SPY 9/30 +66% at 12:00 -> -64% at 3:30; SPY 10/01 +75% -> -93%; QQQ 10/01 +62% -> -89%.
That matches the owner's own record: the A-graded days were "flat by 11:00". **To test that, a time-exit rule
needs its own pre-registration.**

## Limits
- 8 sessions in one 2-week window. Robinhood keeps only ~8 sessions of intraday option history (Addendum A).
- Last-trade prices, not bid/ask. Wider 1DTE spreads would shave a few points off 1DTE results.
- The entry rule is a mechanical stand-in, not the owner's or the 9:46 check's actual entries.
- Neither contract fits CLAUDE.md §5 at current equity (~$254: 4% = ~$10 of risk).
- Scripts read raw pulls from the session's tool-results folder (not committed: several MB). Re-pull with the
  instrument IDs in `ids.txt`; `vehicle_rows.json` holds every price the results use.
