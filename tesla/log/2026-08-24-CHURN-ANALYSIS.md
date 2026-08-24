# Churn analysis — 2026-08-24

Written after the close, at the owner's request, from a self-diagnosis he
offered: *"I am hitting the initial opening moves, riding them for a profit and
exiting, then sabotaging myself by greed in trying to catch the next move."*

Source: Robinhood `get_pnl_trade_history` (per-trade realized) and
`historical-chart/5min`. **The diagnosis is substantially right about the
outcome and wrong about the mechanism.** Both are shown below.

**Sample: one session, 24 entries, 21 closing trades — plus three prior days for
context. This is suggestive, not established.** Everything here is
`UNCALIBRATED`.

---

## 1. A handful of trades carry everything

**Today: three trades made +$862. The other eighteen lost −$842.**

| Trade | P&L |
|---|---|
| 09:44 opening dump — 357.5P | **+170** |
| 10:40 the bounce — 355C, exited by a resting stop at 3.40 | **+270** |
| 15:01 the afternoon dump — 352.5P, exited by a resting stop at 3.82 | **+422** |
| **on-move total** | **+862** |
| everything else, 18 trades | **−842** |
| **net** | **+20** |

Not a one-day artifact:

| Date | Trades | Total | Top 3 | Everything else | Win rate |
|---|---|---|---|---|---|
| 2026-08-19 | 2 | +116 | +116 | — | **100%** |
| 2026-08-20 | 4 | +0 | +53 | −53 | 75% |
| 2026-08-21 | 16 | +580 | +793 | −213 | 69% |
| 2026-08-24 | 21 | +20 | +862 | **−842** | **38%** |

**Week: +$716 total; −$1,108 excluding each day's top three trades.**

Win rate falls monotonically as trade count rises: 100% → 75% → 69% → 38%.

## 2. The mechanism is not greed chasing the next move

Segmenting today by what the tape was doing:

| Window | Trades | P&L |
|---|---|---|
| 09:44–10:16 opening dump + first re-entries | 3 | −113 |
| 10:40–10:42 **the bounce** | 2 | **+246** |
| **11:10–13:32 the chop between moves** | 8 | **−538** |
| 15:01–15:21 **the afternoon dump** + re-entries | 8 | **+425** |

The damage is not in chasing a *next move*. It is in trading when **there is no
move at all**. The −$538 came from a 2h22m stretch with TSLA oscillating between
353 and 358 — the dead centre of the session range.

Visible at the tick level: 350P bought and sold in **18 seconds** (−$6), again in
**57 seconds** (−$35); 360C in **69 seconds** (−$24).

## 3. The decisive test — position in the session range at entry

For each of today's 24 opening trades, where spot sat between the session low
and high at that moment:

| | Entries | P&L |
|---|---|---|
| **Middle third of the range (33–67%)** | **9** | **−415** |
| Outer thirds (the edges) | 15 | **+435** |

Every large winner was at an extreme:

| Entry | Position in range | P&L |
|---|---|---|
| 09:33 357.5P | **6%** | +170 |
| 10:20 355C | **24%** | +270 |
| 14:50 352.5P | **0%** | +422 |

Every mid-third entry except one lost money. `playbook/PLAYBOOK.md` §1b already
forbids this:

> **Don't initiate mid-range.** Entries happen at edges: reclaim/break of a
> mapped level, or a pullback into a prior breakout zone ("discount"), never in
> the middle where odds are worst in both directions.

**The rule that would have prevented most of the damage already exists. It was
not applied.**

## 4. Two plausible fixes the data REJECTS

Both were candidates before testing. Recording the failures because a rule that
sounds right and loses money is worse than no rule.

**A flat time-based re-entry cooldown — rejected.** A 15-minute cooldown after
any close would have blocked the 10:20 entry (10:16 exit → 10:20 re-entry, four
minutes) which became the day's **+$270** bounce trade. Elapsed time does not
separate a good re-entry from a bad one.

**A cap on opening trades per day — rejected.** No monotonic signal:

| Cap | Kept | Forgone |
|---|---|---|
| 2 | +107 | −87 |
| 3 | **−113** | +133 |
| 4 | +157 | −137 |
| 6 | +133 | −113 |
| 8 | **−69** | +89 |

A cap at 3 loses money; a cap at 4 makes money; a cap at 8 loses again. That is
noise, not a rule.

**The playbook's own candidate rule — hard stop after two consecutive losses —
also fails.** Tested: it stops today at 10:16 with the day at **−$113** (actual
+$20) and Friday at 11:34 with **+$500** (actual +$580). It would have hurt both
days, because the best trades came *after* losing runs. **This is evidence
against adopting that candidate rule**, and it should not be promoted out of
candidate status on intuition.

## 5. What the evidence actually supports

A **range-position gate**, not a cooldown. Drafted in
`tesla/PROPOSED-RANGE-GATE.md`, **pending ratification** — not in force.

## 6. What is worth protecting

All three on-move winners, and both of the two largest, were exited by **working
stop orders**. Every loss of size came from a position with no stop or from a
mid-range entry. Execution *while a move is running* is not the problem. The
problem is entirely what happens between moves.

## 7. Limits of this analysis

- **One session of entry-level detail** (24 entries). The three prior days
  contribute P&L distribution only; their entries were not range-tested.
- Range position is computed against the session high/low **as of that moment**,
  which is the only honest way to do it live but means early entries sit in a
  narrow range by construction.
- Attribution of P&L to a specific entry is approximate where the same contract
  was scaled into and out of.
- **n = 9 mid-third entries.** One bad day of luck would move this materially.
  The gate below must be tested forward, not adopted as settled.
