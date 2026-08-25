# DAY PLAN — the morning strategy card

**Created 2026-08-26 (phase 6 of the owner's improvement program). Status:
UNCALIBRATED** until `brief-review` has graded 20 day cards. This module
turns the brief's *validated* structure into a written, pre-open plan. It
invents nothing: selection rules come from the scorecard's evidence, trade
mechanics come from `options-expert/SKILL.md`, execution discipline comes
from `playbook/PLAYBOOK.md`. Claude never places orders; the human executes.

## What this is

The brief-review scorecard (n=5) shows where the brief's edge actually is:
fired confirmations paid 8/9, fired invalidations were correct kills 9/9,
level scripts keep landing at the turning points — while conviction language
and flow-leans have no record. So the day plan trades the **trigger
structure** and nothing else: 0–3 conditional plans, written before 9:30,
each of the form *"if the written confirmation fires, this is the trade; if
the invalidation fires, there is no trade."* A day with zero cards is a
correct output (playbook §0: selective participation).

## When it runs

~9:15–9:25 ET, after the brief lands, finishing **before 9:30**. The output
file is the pre-registration record (`CLAUDE.md` §9): once the open prints,
the file is append-only — intraday updates go in timestamped addenda, never
edits.

## Step 1 — Candidate selection (from today's brief)

Take the brief's §9 radar cards (all carry trigger pairs per ratified I-3)
plus any §6A flag with an explicit written trigger. Apply these filters, each
earned by graded evidence:

| # | Filter | Evidence |
|---|---|---|
| S1 | **Trigger-complete only.** Confirmation AND invalidation, levels referenced, deadline stated. Anything else is an observation, not a candidate. | TOL/CRWV ungradeable; I-3 |
| S2 | **Prefer intraday structure over gap momentum.** A confirmation that fires *after* an overnight gap has mostly been paid already (COIN 8/20, MSTR 8/21). Level break / retest / range-hold triggers carried the real trigger-to-payoff (QQQ 8/24, WDC 8/18, MRNA 8/19). Gap-momentum cards are allowed only with a same-day structural trigger (e.g., holds the gap through the first hour → retest entry). | Scorecard obs. 4 |
| S3 | **Price outranks flow.** A card whose case rests mainly on flow/OI build is tradable only on its price condition, and flow conviction never upgrades size (NVDA 8/19 MEDIUM-HIGH, MRK 8/20, PLTR 8/24 all failed price while flow leaned). | Scorecard obs. 3; playbook §0; I-5 |
| S4 | **Regime gate** per `options-expert/SKILL.md` Stage 1, re-derived live — the 9:05 snapshot does not gate a 10:30 entry. Continuation cards in strong glue die here. | Playbook §1c |
| S5 | **Event gate.** A card whose trigger window collides with a scheduled print (the brief's §3 table) inherits the playbook §2 event protocol: no entry on the headline candle, triggers evaluated on candles two and three. | Playbook §2 |

Write the kill list — candidates and one-line reasons — exactly as
options-expert §6 does. The kill count is the honest number.

## Step 2 — Build each surviving card

Run the survivor through `options-expert/SKILL.md` Stages 3–7 *as written*
(edge tests with named mode, E1b vehicle comparison when two instruments
express the thesis, structure by IV-rank × regime, liquidity gates, sizing
off the stop distance against live equity, §1 risk limits, heat and
correlation checks). The day card IS an options-expert card — same block
format as its §6 — plus three day-plan fields:

```
WINDOW        <when the trigger is live: e.g. "9:40–11:30; dead after
               11:30 unless the 10:00 print re-opens the tape">
DO NOTHING IF <the states in which no action is correct: invalidation fired;
               neither trigger by window end; volume floor unmet; gap >1%
               beyond the trigger level at the open (the move pre-paid)>
RE-ARM        <whether a fired invalidation can re-arm today (usually NO),
               and what would justify it (a full retest per playbook §1c)>
```

Sizing honesty: if `get_portfolio` fails, cards ship **unsized** with
`NA_no_data` — levels and structure are still useful; invented equity is not.

## Step 3 — The day header

Above the cards, five lines, all from today's brief:

```
BIAS      <brief mood — the direction filter, never a trade by itself (5/5
           on sign, but the moves were ±0.3–1.0%)>
REGIME    <glue/gasoline/flip + walls — where stops and targets live>
EVENTS    <every §3 time, listed; the alert windows>
HEAT      <open positions + current heat vs MAX_OPEN_HEAT_PCT>
CARDS     <n of max 3 — and if 0: "no card passed; watching X and Y">
```

## Output and record

Write `day-plan/cards/YYYY-MM-DD.md` (header + cards + kill list + WHAT THIS
DOES NOT KNOW), before 9:30, and commit it. Chat delivery mirrors the brief's
OUTPUT DELIVERY rules: delivery failure never blocks the plan.

## Grading — what makes this improvable

`brief-review` grades each day card at T+1 with the same rules as radar
items (CONF-PAID / CONF-FAILED / INVALIDATED / NO-TRIGGER, on the card's own
written triggers), **plus** the fill-relevant extras the replay test proved
matter: payoff measured on the *contract mark* via `get_option_historicals`
where liquidity allows, and the adverse excursion between trigger and
resolution. Results go to the `day_cards` table in the scoring DB and roll
into `SCORECARD.md`. Twenty graded cards is the calibration bar — the same
bar as everything else in this repo (`CLAUDE.md` §7).

## What this module refuses to do

- Trade the mood. It is a filter with a 5/5 record on sign and no record on
  magnitude.
- Pre-position before a binary (playbook §2: react, don't predict — the
  process's whole edge is the trigger discipline).
- Ship a card without a written stop, size, and do-nothing condition.
- Edit a card after the open. The pre-registration is the product; a plan
  that can be rewritten mid-day is a mood, not a plan.
