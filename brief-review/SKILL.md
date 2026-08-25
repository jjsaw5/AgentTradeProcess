# DAILY BRIEF REVIEW — accuracy & performance grading

**Created 2026-08-20. Status: the process itself is UNCALIBRATED** — thresholds
below are reasoned, not validated, until the scorecard holds enough graded days
to say otherwise (target: 20 trading days, per the spirit of `CLAUDE.md` §7).

## Purpose

The 9:05 brief (`daily-market-brief/SKILL.md`) feeds positioning decisions.
This process grades each archived brief against what the market actually did —
that day and the following days — and turns the gaps into candidate
improvements. It is the continuous-improvement loop for the brief:

1. **Accuracy** — were the brief's numbers and checkable calls right?
2. **Performance** — would acting on the brief's own triggers have pointed at
   the right options plays?
3. **Improvement** — what information, available before that open, would have
   caught what the brief missed?

This process never trades and never edits a brief. Reviews are separate
documents; the brief archive is the immutable record being graded.

## Cadence and inputs

- Review day **D** no earlier than **D+1** (the full session plus the overnight
  UW/OI update must exist). Multi-day theses stay OPEN in the ledger and are
  re-graded on D+2…D+5 until resolved.
- Inputs: `briefs/D.md` (the claim source), Robinhood historicals (primary
  price record — same authority ranking as the brief itself), UW/FMP where a
  claim needs them. All honesty rules from `CLAUDE.md` §3 apply: timestamps
  read, windows asserted, `UNVERIFIED` where a number cannot be confirmed,
  sentinels per §4, never `0.0` for a missing measurement.
- Intraday grading granularity: 10-minute bars unless a claim needs finer.
  State the granularity; do not grade a claim finer than the data pulled.

## Anti-hindsight rules (load-bearing)

These exist because a grader with the answer key can make any brief look bad.

1. **Grade the brief's own written triggers, never invented ones.** If a radar
   item said "confirmation: holds $165 after the open," that line — not a
   better line visible in hindsight — is what gets graded.
2. **A clean invalidation is a process HIT.** The brief said what would make
   the idea wrong, and it was wrong on schedule. That is the system working.
   Only a confirmation that fired and then failed, or a scenario the brief
   never priced, counts against it.
3. **Direction hit-rate near 50% is chance, not failure.** The brief's value
   claims are conditional (if X then watch Y); grade the conditions.
4. **Never grade "should have predicted X" when X was unknowable pre-market.**
   An undated Phase 3 readout is unknowable; the ask-side sweep in front of it
   is knowable. §H grades only whether knowable tells were surfaced.
5. **The rubric does not change mid-review.** Anything the rubric can't grade
   goes in the review's post-hoc notes section, and a rubric change is a
   dated commit that applies to *future* reviews only (§9 of `CLAUDE.md`).

## The rubric

Every review file grades exactly these seven categories, in this order.

### F — Factual accuracy

Spot-check at least 5 verifiable numbers from the brief (prev-day H/L/C,
premarket quotes vs. the extended-hours record, earnings figures, expected
moves) against the primary record. Report `n correct / n checked`, list every
discrepancy with both values. A number that cannot be re-verified is
`UNVERIFIED`, not wrong. Distinguish *wrong* from *stale-and-labeled* — a
number the brief itself flagged as stale/UNVERIFIED is graded on the label's
honesty, not the number.

### O — Open read

The brief's §0 "open read" (gap classification + the level script it implies).
- Was the gap classification correct at 9:30?
- Did the named level behave as scripted (e.g., "PDL flips to first
  resistance" — did price stay below PDL, or reclaim it)?
Grade: `HIT / MISS / MIXED`, one sentence of evidence with times.

### M — Mood call

Map the brief's Market Mood to realized SPY direction:
- Bullish (either strength) → HIT if SPY closes above prior close.
- Bearish (either strength) → HIT if SPY closes below prior close.
- Neutral/mixed → HIT if |close-to-close| ≤ 0.25%.
Record close-to-close % and open-to-close % (the mood is read premarket, so
both drifts matter). `MIXED` when the two drifts disagree and the brief's
stated reasoning matches one of them — say which.

### G — Regime / gamma call

Did realized behavior match the characterization (glue = pin/dampened near
named walls; gasoline = breaks extend; chop = rangebound)? Evidence: day range
vs. the prior 5 sessions' average range, whether named walls acted as
magnets/friction, whether breaks continued or whipsawed. Grade:
`HIT / MISS / UNCLEAR`. Walls were labeled approximate; grade the *behavioral
claim*, not wall precision to the cent.

### R — Opportunity radar

For each §9 radar item, in the brief's own terms:
1. Which fired **first** — the written confirmation or the written
   invalidation? (Times from intraday bars.)
2. If confirmation fired: did the stated direction pay from the trigger point
   to the end of the item's stated timing window (underlying %; option marks
   via `get_option_historicals` where a specific structure was implied and
   liquidity allows)?

Grades per item:
- `CONF-PAID` — confirmation fired, direction paid.
- `CONF-FAILED` — confirmation fired, direction did not pay. The costly miss.
- `INVALIDATED` — invalidation fired first. Process HIT (rule 2).
- `NO-TRIGGER` — neither fired inside the timing window.
- `OPEN` — multi-day, unresolved; carried in the ledger.

Roll-up: `x CONF-PAID / y confirmations fired`, plus counts of the rest.

### W — Watchlist flags (§6A)

- **Precision:** of the names the brief FLAGGED, how many either moved ≥2%
  (close-to-close) that day or had their specific story confirm within D+1
  (e.g., the OI build the flag cited persisted)? Report `hits / flags`.
- **Recall proxy:** of watchlist names that moved ≥3% close-to-close on D,
  how many had been flagged or mentioned with the right lean? Report
  `caught / movers`. Quiet-name one-liners that stayed quiet are silent hits;
  a "nothing notable" on a name that moved ≥3% is a named miss.

### H — Hindsight gap analysis (the improvement engine)

**Post-hoc by construction — every finding here is labeled hindsight and is a
candidate, never a conclusion** (`CLAUDE.md` §9). For each material move the
brief missed or underweighted (market-wide or watchlist):

| Field | Content |
|---|---|
| What happened | The move, with numbers |
| What was knowable pre-market | Specific data that existed before 9:30 that day, named source |
| Gap type | `SPEC GAP` (brief spec doesn't ask for it) / `EXECUTION GAP` (spec asks, run missed it) / `UNKNOWABLE` (no pre-market tell existed) |
| Candidate change | Concrete spec edit, or `NONE` |

Candidate changes go to `brief-review/IMPROVEMENTS.md` as `PROPOSED`. They are
adopted into `daily-market-brief/SKILL.md` only by the account owner's
decision, recorded there as `RATIFIED` with a date. Precedent: the §4A FDA
watch (proposed and adopted 2026-08-19 after the MRNA miss) is exactly this
loop — it predates this spec and is logged in IMPROVEMENTS.md retroactively.

## Output

1. `brief-review/reviews/D.md` — the graded review, rubric order, every grade
   with its evidence. Open items listed at the end with what would resolve
   them.
2. `brief-review/SCORECARD.md` — one row per reviewed brief plus recomputed
   cumulative rates. The scorecard is the calibration record; it displays
   `UNCALIBRATED (n=X of 20)` until 20 trading days are graded.
3. `brief-review/IMPROVEMENTS.md` — append any new PROPOSED items.
4. **Database sync** (added 2026-08-20; see `DATA_STORE.md`): upsert the
   review's `brief_reviews` row, its `radar_items` and `watchlist_events`,
   ledger/open-item changes, and resolve any OPEN items that closed. The
   markdown review is the evidence record; the DB is the queryable index —
   on disagreement the markdown wins and the row gets corrected. Credentials
   for the sync come from the environment/`.env` by variable name only.
   **Coverage additions (2026-08-25, for the must-mention automation):**
   (a) record a `watchlist_events` row with `move_pct` for EVERY watchlist
   name each graded day — quiet names that stayed quiet get outcome
   `QUIET-OK` — so the I-4 trailing-move math never has silent gaps;
   (b) record each name's flow lean as stated by the graded brief into
   `flow_observations` (`bull` / `bear` / `mixed` / `none`, with the brief's
   own wording as the note) — this is what powers I-2's streak detection;
   (c) maintain the `complexes` table when a MATERIAL CATALYST names or
   deactivates a complex (deactivation is a deliberate edit, prompted by the
   generator's "deactivation due" note, never automatic).
5. **Regenerate the checklist:** run `tools/must_mention.py` (reads the DB,
   writes `brief-review/MUST_MENTION.md`) and commit the refreshed file with
   the review. The morning brief reads that file as its coverage floor per
   `daily-market-brief/SKILL.md` §6A.
6. **Grade the day plan (added 2026-08-25):** if `day-plan/cards/D.md`
   exists, grade each of its cards under the same rules as §R — on the
   card's own written triggers — plus the fill-relevant extras: payoff on
   the contract mark (`get_option_historicals`) where liquidity allows, and
   the adverse excursion between trigger and resolution. Record to the
   `day_cards` DB table and note the roll-up in the review file and
   `SCORECARD.md`. Day cards are UNCALIBRATED until 20 are graded.
7. Session log entry per `CLAUDE.md` §8 when a review session touches the
   repo.

## What this process does not do

- It does not grade the human's execution (that is `playbook/PLAYBOOK.md` §5's
  journal).
- It does not rewrite briefs, re-run briefs, or score interpretive prose.
- It does not treat one week as evidence. The scorecard exists precisely so
  that nobody has to argue from anecdotes — in either direction.
