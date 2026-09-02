# Ticket 5 — PLTR 0DTE Friday test (SHADOW)

**Written 2026-09-02 15:58 ET, before Friday's session. Pre-registered per §9:
every input and expectation below is recorded while the outcome is unknown.**

**SHADOW TICKET — NO CAPITAL.** Counts toward the §7 gate (10 graded tickets).
CLAUDE.md §2 stands: Claude never executes.

Origin: the owner's proposal that *"PLTR seems to be better suited for a 0DTE
setup."* Background research: `2026-09-02-PLTR-RESEARCH.md`.

---

## What is being tested

**Not** whether the trade makes money. **Whether the instrument is tradeable at
the hour we would trade it.** Everything measured on 9/2 was pulled at
15:39–15:55 ET — the tightest part of the session. The 10:00 window is
`NA_no_data` and it decides the question.

## Gate 1 — the 10:00 ET liquidity test (HARD, decides the ticket)

At **10:00–10:05 ET Friday 2026-09-04**, pull PLTR's 9/4 chain and record, for
the contract nearest 0.50 delta in each direction:

- bid, ask, mid, spread as % of mid
- delta, theta, gamma, volume, open interest
- PLTR spot and the session range so far

**PASS** = spread ≤ 2.0% of mid, per `SWING_STRATEGY.md` §3a.
**FAIL** = anything above. A fail ends the ticket. No entry is considered, no
second look, no "close enough."

### Pre-registered expectation — I expect Gate 1 to FAIL

**Predicted:** PLTR ATM 0DTE spread at 10:00 will be **above 2%**, most likely in
the **3–6%** band.

**Reasoning, recorded so the prediction can be judged on more than its outcome:**
PLTR fails the 2% gate on 78% of its 2-DTE contracts at the *tightest* hour of
the day. TSLA — which passes 81% at 2 DTE — showed **no contract under 3.1%** on
its own expiry day, with the 0.63-delta call at 5.8%. Expiry day widens spreads;
PLTR starts from 2.6× TSLA's baseline.

**If the spread comes in at or under 2%, I am wrong.** That is a genuine finding
about PLTR's Friday liquidity, it should be written up as such, and the idea
earns a second ticket rather than a dismissal.

## Gate 2 — affordability (records a number, does not stop the ticket)

Predicted from 9/2 greeks (9/4 170C: mid $2.50, theta −$0.727/day = 29% of
premium per day): ATM contract prices **$105–150** at Friday's open with spot
unchanged.

**Expectation: this HOLDS.** Record the actual. If it prices above $200, the
affordability argument that motivated the whole proposal is gone, independent of
Gate 1.

## Gate 3 — the setup itself (only reached if Gates 1 and 2 pass)

Standard `SWING_STRATEGY.md` §4, unmodified:

- No entry before **10:00 ET**.
- A **mapped level** — Friday's gamma flip and call/put walls, re-pulled after
  10:30 (`gex-levels` drifts; 8/25 rule).
- **Two consecutive 5-min closes** through the level with participation **≥ 0.40**
  of the 9:30–10:00 mean.
- **Retest over breakout.**
- **Flow gate veto:** persistent adverse net premium = stand down.

**§4 is deliberately not relaxed for this test**, even though the research found
PLTR's opening hour moves 4.6× its 2 PM hour and §4 hands that hour away. That
tension is real and is recorded in the research note. **It is not being resolved
here.** §4 rests on 119 graded trades; a range profile is not that kind of
evidence, and changing two things at once makes the test unreadable.

## If entered (shadow): sizing, stop, exits

- **Shadow account: $475** — the live figure, so the test answers the real
  question.
- **1 contract maximum.** No scaling. If one contract does not fit, the ticket
  ends and that is the finding.
- **Stop:** at the level that invalidates the setup, on the underlying, 15-cent
  buffer. **Never widened to fit the budget** (CLAUDE.md §5).
- **§5a 30-minute rule applies, hard.** Evidence: the 30–60 minute bucket is
  −$1,143 at a 12% win rate; the 15–30 minute bucket is +$305 at 64%.
- **§6b give-back:** at +50%, stop moves to entry, permanently.
- **Hard flat by 15:00 ET.** No exceptions. The 9/2 TSLA chain showed 0DTE delta
  going binary and spreads reaching 3–200% into the close; **there is no such
  thing as a late exit on expiry day.** 159,294 TSLA 360 calls traded on 9/2 and
  expired worthless.

## What a graded outcome looks like

Record, whether or not anything is entered:

1. Gate 1 result, with the actual spread, against the prediction above.
2. Gate 2 actual price against $105–150.
3. Whether a §4 trigger printed at all, and at what time.
4. PLTR's Friday body ÷ range, added to the n=23 weekday sample.
5. **A no-trade outcome grades A** if the gates were applied as written. The
   point of this ticket is the measurement, not a position.

## What this ticket cannot establish

- **Anything about PLTR 0DTE generally.** One Friday is one Friday.
- **Whether the 60% Friday body/range finding is real.** n=23, and the same test
  flags Monday for TSLA and NVDA — probably multiple-comparisons noise. One more
  observation does not fix that.
- **Whether 0DTE is a good idea for this account.** The standing evidence says
  no: 85 trades, −$1,019, 46% win. This ticket tests one narrow instrument
  question the owner raised. **It is not a reopening of the 0DTE question**, and
  a pass on Gate 1 must not be read as one.
