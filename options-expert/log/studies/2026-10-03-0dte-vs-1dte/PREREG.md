# Pre-registration — 0DTE vs 1DTE inside the session (written 2026-10-03, before any option data is pulled)

Owner request (10/03): test whether a 1DTE contract is a better vehicle than a 0DTE for the
day trade the brief and the 9:46 check set up. Follows the overnight study in
`../2026-10-03-overnight-1dte/`, which found the overnight hold loses.

## Design (fixed before data)

- **Days:** every session with a graded brief, 2026-08-18 -> 2026-10-02 (33 sessions). SPY and QQQ.
- **Entry rule (mechanical stand-in for "after the first 15-minute bar"):** at 9:45 ET, take the
  direction of the first 15-minute bar (9:45 price vs 9:30 open): up -> call, down -> put.
  The 9:46 check itself only exists from 10/01, so it cannot be replayed; this is a cruder signal on purpose.
- **Contracts:** strike = nearest $1 to the 9:45 underlying price. 0DTE = expires that day.
  1DTE = expires the next trading day. Same side, same strike, same entry minute.
- **Prices:** real Robinhood 5-minute option bars, last trade. Entry = close of the 9:40 bar.
  Checkpoints: 10:15, 10:45, 12:00, 3:30 PM (close of the bar ending then).
  A bar marked `interpolated` (no trade) is `NA_no_data` for that checkpoint, never filled.
- **Measure:** return as % of premium paid, so both use the same dollars. Also dollars per contract.
- **Groups:**
  (a) all days;
  (b) realized character after 9:45 (direction-blind): RAN if |3:30 price - 9:45 price| >= 50% of the
      9:45-3:30 high-low range, else STUCK;
  (c) entry direction right or wrong at 3:30;
  (d) the brief's day-type call, for the 11 days in the SCORECARD day-type record that have archived briefs
      (9/18, 9/21-9/25, 9/28-10/02). Small n, descriptive only.

## What I expect (before looking)

- **P1** A 1DTE ATM costs about 1.6-2.2x the 0DTE at 9:45.
- **P2** When the entry direction is WRONG or the day is STUCK, 1DTE loses a smaller share of premium
  than 0DTE at every checkpoint. At 3:30: 0DTE losers about -60% to -100%; 1DTE about -25% to -55%.
- **P3** When the direction is RIGHT on a RAN day, 0DTE makes the larger % (about 1.5-2x the 1DTE's %).
- **P4** Across all days, the naive first-bar entry has negative mean % return for BOTH at 3:30;
  1DTE's mean is higher (less negative) than 0DTE's. At 10:15 the two means are within 10 points.
- **P5** 1DTE's spread of outcomes is narrower (smaller standard deviation of % return) at every checkpoint.
- **Failure that would embarrass P2/P4:** 1DTE losing as much as 0DTE on STUCK days would mean the
  "slower decay" argument does not survive real prices (IV and spreads on the next-day contract).

## Known limits, stated up front
Last-trade prices, not bid/ask: real fills are worse, more so for the less-traded 1DTE.
33 sessions in one 7-week window. UNCALIBRATED (CLAUDE.md §7) whatever it shows.

## Addendum A — written after the data pull failed for most days, before computing any result

**Coverage check failed (CLAUDE.md §3: "a 200 is not a success").** Robinhood returned HTTP 200 for every
contract, but for every session 2026-08-18 -> 2026-09-22 every 5-minute bar is `interpolated: true`
(a flat placeholder price, no trades). Probed: all of 8/18-8/25 in full; 9/08, 9/15, 9/18, 9/21, 9/22 at the
9:40 bar. Real intraday option prints exist only from 2026-09-23 (seen earlier the same day in the
overnight-study calibration). Robinhood appears to keep roughly the last ~8 sessions of intraday option history.

Consequences, fixed now:
- The test runs on the **8 sessions 9/23, 9/24, 9/25, 9/28, 9/29, 9/30, 10/01, 10/02** (16 trades: SPY+QQQ).
  Everything else in the design is unchanged.
- At n=16, P1-P5 are reported as **descriptive only**. No verdict is "confirmed" on this sample;
  a direction that matches is "consistent", one that doesn't is "inconsistent".
- The day-type group (d) now covers 8 of its 11 days.
- What I had already seen of these sessions: the overnight close->9:45 marks of the 1DTE straddles on
  9/23-10/01 (overnight study, section C). I had NOT seen any 9:45->3:30 intraday option path.
- The way to the full 33-day test is to **record marks going forward**. Robinhood history won't backfill it.
