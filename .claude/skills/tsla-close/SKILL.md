---
name: tsla-close
description: End-of-session grading and logging for the TSLA 0-5DTE process. Grades execution against the card's pre-recorded inputs using real contract OHLC, writes the outcome to tesla/log/, and appends the session grade to the playbook journal. This is the only path off UNCALIBRATED. Use after 15:30 ET or when the user asks to close out and grade the TSLA session.
---

# /tsla-close — grade the session and log it

Read `tesla/CHARTER.md` §6 and `playbook/PLAYBOOK.md` §5.

**Grade execution, not P&L.** A rule-following loss is a good loss; a
rule-bending win is a bad win. This is the standard, and it is the whole point
of the exercise.

Run after **15:30 ET** (TSLA's force-close) — not 16:00.

---

## 1. What actually happened, from the broker

- `get_option_orders` (today) — every fill: time, price, quantity, order type.
- `get_option_positions` — anything still open. A 0DTE position still open after
  15:30 was force-closed; say so.
- `get_realized_pnl` / `get_pnl_trade_history` — realized dollars.
- **`get_option_historicals(instrument_ids, interval)` — OHLC on the contract
  itself.** This is what makes a card checkable against the **real mark**
  rather than a modeled price, and it is the reason §11 of `/tsla-scan` demands
  the inputs be written before the outcome.

## 2. Grade the card against what it predicted

Open today's `tesla/log/YYYY-MM-DD.md` and take each card's **pre-recorded**
inputs. Do not edit them. Do not rewrite a thesis to fit the outcome —
`CLAUDE.md` §9 forbids changing an analysis plan after seeing results.

For each card, answer in writing:

| Question | Evidence |
|---|---|
| Did the trigger actually fire as written? | the 5-min bar that closed through the level |
| Was the entry at the trigger, or ahead of it? | fill time vs bar close |
| Was the stop resting before the entry filled? | `get_option_orders` timestamps |
| Was the stop honoured, or moved? | order history |
| Was the resting limit at the target working when it was touched? | order history vs contract OHLC high |
| Did the invalidation get hit, and was it obeyed? | underlying bars vs the written level |
| Did E1's theta arithmetic hold? | θ spent vs Δ earned over the actual hold |
| Was the exit inside the clock (15:00 bell / 15:25 hard)? | fill time |

**Where a card was written and no trade was taken, grade that too.** A correct
no-trade is a result, and the kill reasons are what make the process gradeable.

## 3. The pre-registration check

`CLAUDE.md` §9: state what a test should show *before* running it, and record
what it actually showed — **including when the test embarrasses the design.**

So, explicitly:

- Which numbers in `tesla/DATA_LAYER-TSLA.md` did today test?
  The provisional volume floor (~185,000)? The 5% spread gate against live
  intraday quotes? The 3-tick stop buffer? The 15:00 bell?
- What did each show?
- **If a threshold was wrong, write that down here and fix the spec in a
  separate commit.** The model is `options-expert/log/2026-08-18-REPLAY-TEST.md`:
  the failure stayed in the log, the fix went into the spec, and the log was not
  rewritten to look prescient.

## 4. Grade

A / B / C on **execution**:

- **A** — entries only at levels with confirmation, stop resting before the fill,
  invalidation obeyed, exit inside the clock, size inside the caps.
- **B** — one rule bent, named.
- **C** — anticipation without confirmation, chased entry, stop moved, size
  outside the caps, or trading past 15:25.

Consistency comes from deleting C-game sessions, not adding A-games.

## 5. Write it down

**Append to `tesla/log/YYYY-MM-DD.md`** — under the existing cards, never over
them:

```
## OUTCOME — <YYYY-MM-DD>

RESULT        <realized $ | no trade taken>
CARD          <contract, or "none — n candidates killed">
TRIGGER       <fired as written | fired and not taken | never fired>
STOP          <resting before entry? honoured?>
CLOCK         <exit time vs 15:00 bell / 15:25 hard exit>
CONTRACT OHLC <the real high/low the card could have achieved>
E1 CHECK      Δ earned $xx vs θ spent $xx over <n> min actual hold — <held | failed>
GRADE         <A|B|C> — <the one decision-quality note>
SPEC IMPACT   <threshold tested, what it showed, and whether a spec change is owed>
```

**Then append one line to `playbook/PLAYBOOK.md` §6** — the journal table. That
file is the durable home for the human's trading record and TSLA sessions belong
in it: `| date | realized P&L | grade | note |`.

## 6. Calibration status — update it honestly

CHARTER §6 says everything in this module is `UNCALIBRATED`. Each graded session
is one data point against that. State the running count:

```
tesla/log/ holds n graded sessions. Status: UNCALIBRATED.
```

It stops being uncalibrated when the log shows the edge tests working
out-of-sample — and **not before**, no matter how good a run of sessions looks.
A winning week is not calibration; it is a small sample with a pleasant sign.

## 7. Session log

If the session changed a spec, a threshold, or a governance rule, append an
entry to `docs/audit/SESSION_LOG.md` per `CLAUDE.md` §8 — what changed and why,
decisions with reasoning, and a **DEVIATIONS** section with `None` written
explicitly when there are none.

Grading a trade is not a spec change and does not need an entry. Discovering the
volume floor is wrong and editing it **is**.
