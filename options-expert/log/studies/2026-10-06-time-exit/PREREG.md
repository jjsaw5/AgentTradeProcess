# Pre-registration — "out by 11:00" vs "hold" (written 2026-10-06 08:55 ET, before any qualifying data exists)

Owner request (10/06): "set up both" — (1) record 0DTE/1DTE option prices every evening, (2) test the
time-exit idea that surfaced, unplanned, in `../2026-10-03-0dte-vs-1dte/RESULTS.md` ("Exploratory").

## Where the idea came from (and why that data can't test it)
In the 0DTE-vs-1DTE study (9/23–10/02, 16 trades) the mechanical first-bar entry was up on average at
10:15–12:00 (0DTE mean +34% to +38%) and gave it back by 3:30 (+4%). That pattern was found by looking, so
**those 8 sessions are the hypothesis-generating set and are excluded from this test.** 2026-10-05 is also
excluded: its option marks are unseen, but its underlying path (a steady up-trend from 9:45) was already
graded in the 10/05 review, which would bias the result. **The test sample starts 2026-10-06.**

## Design (fixed now)
- **Data:** `options-expert/log/marks/option_marks.csv`, written each evening by the brief-review
  "option marks" step (`options-expert/tools/record_marks.py`). Real Robinhood 5-minute option bars,
  last trade. An `interpolated` bar is `NA_no_data` — that trade is dropped from the comparison that needs
  it, and the drop is counted, never filled.
- **Contracts:** SPY and QQQ, strike = nearest $1 to the 9:45 underlying price, call AND put, expiring
  today (0DTE) and the next trading day (1DTE).
- **Entry (primary, mechanical):** at 9:45, the side of the first 15-minute bar (9:45 close vs 9:30 open):
  up → call, down → put. Entry price = the 9:45 mark. A flat first bar (|move| < 0.02%) is skipped and counted.
- **Exits compared:** **A = sell at 11:00** vs **B = hold to 3:30**. Also reported, not tested:
  10:15, 10:45, 12:00, 2:00.
- **Primary metric:** % of premium, per trade. Unit of analysis = trade (2 per session).
- **Stopping:** evaluated once, at **20 sessions (≈40 trades)**. Running tallies may be shown as
  descriptive only; no early "it works" call. Early stop only if the data feed breaks.

## What I expect (before any qualifying data)
- **T1** On 0DTE, exit A beats hold B on **55–70%** of trades.
- **T2** On 0DTE, mean(A) − mean(B) is **+15 to +35 points** of premium.
- **T3** The A-vs-B gap is **smaller on 1DTE** than on 0DTE (1DTE decays less while you wait).
- **T4** The rule's cost: on RAN days (|3:30 − 9:45| ≥ 50% of the 9:45–3:30 high-low range, the
  vehicle-study definition), **B beats A on most trades** — the time exit gives up the big days.
- **Would embarrass the idea:** T1 under 50% or T2 ≤ 0 — the exploratory pattern was noise.

## Known limits, stated now
Last-trade marks, not bid/ask. The mechanical entry is a stand-in for the owner's or the 9:46 check's
entries. 20 sessions is a floor for honesty, not proof. UNCALIBRATED (CLAUDE.md §7) whatever it shows.
