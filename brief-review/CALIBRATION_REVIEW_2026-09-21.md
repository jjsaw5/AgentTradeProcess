# CALIBRATION REVIEW — assembled 2026-09-21 (n=24)

**Status: DECISION PACKAGE FOR THE ACCOUNT OWNER.** This document assembles the
nine open PROPOSED items (R-1, R-2, I-8…I-14) and the UNCALIBRATED-graduation
question into one place to rule on. Nothing here self-ratifies — per
`CLAUDE.md` §7 and `brief-review/IMPROVEMENTS.md`, an item becomes RATIFIED only
by the owner's explicit dated decision, and is then edited into its target spec
as its own commit. This file is the worksheet; the rulings land in
`IMPROVEMENTS.md` and the specs.

Recommendations below are the review process's, not decisions. Mark each
`DECISION:` line **ADOPT / ADOPT-MODIFIED / REJECT / KEEP-WATCHING**.

---

## PART 1 — The graduation question: does the process leave UNCALIBRATED?

The scorecard reached its founding bar (n=20, "enough that nobody argues from
anecdotes") on 2026-09-15; it is now **n=24**. But "UNCALIBRATED" covers two
different layers, and the honest answer differs between them.

### Layer A — brief accuracy (facts / open-read / mood / regime / radar)

The evidence, cumulative through n=24:

| Category | Record | Read |
|---|---|---|
| Facts | 202/210 (96%) | Reliable; residual errors are labeling/sourcing, not price data |
| Open read | 24/24 gap/range classification (15 HIT / 9 MIXED on wall-behavior) | The classification engine is perfect |
| Mood | 20/24 (83%) | All 4 misses are one shape (neutral-on-narrow → I-10) |
| Regime | 15 HIT / 8 MIXED / 1 MISS | Trend/pin calls land; wall-precision costs the mixed grades |
| Radar confirmations | **38/53 paid (72%)** | — |
| **Invalidations** | **22/22 (perfect)** | The risk half has never been miscalled |

**Recommendation: the brief-accuracy layer has earned graduation from
UNCALIBRATED — the owner's call to accept the n=24 sample.** The honesty rules
(§3), sentinels (§4) and data-quality discipline are intact throughout; the
invalidation record (22/22) means the system's *protective* claims are proven,
which is the load-bearing part. Graduating this layer means the scorecard drops
the `UNCALIBRATED (n=X of 20)` banner for the brief and reports live rates.

`DECISION: __________`  (graduate brief-accuracy layer to CALIBRATED / keep UNCALIBRATED)

### Layer B — options-expert / day-card edge & selection scores

`CLAUDE.md` §7 is explicit: everything in `options-expert/` (edge tests E1–E5,
liquidity gates, structure matrix, heat accounting, selection framework) stays
`UNCALIBRATED` until the log holds enough **graded paid outcomes** to say
otherwise. The day-card ledger is **19 opened / 19 resolved, but only 8 paid** —
the rest are 9 no-triggers (correct refusals, but not edge validation) and 2
failures. Scale-at-target is 8-for-8, which is a real management finding, but
the *selection* edge (does the framework pick winners?) rests on 8 paid cards.

**Recommendation: KEEP Layer B UNCALIBRATED.** Eight paid outcomes is not yet
the evidence §7 demands; the no-triggers, however correct, don't test whether a
fired card's direction pays. Revisit at ~20 *paid* resolutions.

`DECISION: __________`  (keep options-expert UNCALIBRATED / graduate)

---

## PART 2 — The nine proposals, ranked by evidence strength

### Tier 1 — strongest cases (mechanical, many instances, zero counter-evidence)

**I-10 — Narrow-tape mood rule.** When §7 breadth is NARROW, the Market Mood
may not be a bare "neutral/mixed"; it must state an index-specific lean or claim
a pin.
- **Evidence: 4-for-4, zero counter-instances.** Every lifetime mood miss (9/2,
  9/4, 9/8, 9/16) is the identical shape — a neutral label on a self-declared
  narrow tape that then trended past ±0.25%.
- **Why adopt:** it's the single most-predictive pattern in the whole scorecard,
  it uses the brief's *own* breadth diagnosis (no new data), and it directly
  fixes the worst-performing grade category. Near-zero implementation cost.
- Recommendation: **ADOPT.** `DECISION: __________`

**I-14 — First-eligible-candle rule.** No radar confirmation may be satisfied by
the 9:30–9:45 candle or an opening gap print; the trigger clock starts at 9:45.
- **Evidence: 2 failures in one day (9/18 QQQ + USO), then validated live.** Ran
  as day-plan convention on 9/21 and produced **3 first-candle refusals + 3 paid
  confirms** — its first live day was a clean before/after.
- **Why adopt:** already proven in production; the guard existed elsewhere in
  the same repo (the day-plan event protocol, §0's own "first 10–15 min: watch")
  and just wasn't inherited by the radar template. Complements I-8.
- Recommendation: **ADOPT** (into the brief spec, not just day-plan).
  `DECISION: __________`

**I-12 — Repeat-mover rule.** A watchlist name with ≥2 unflagged ≥3% c-t-c moves
in the trailing 10 sessions can't take "nothing notable" — it carries a
two-sided level line until quiet 5 straight sessions.
- **Evidence: the largest remaining recall leak.** RDDT ×4, HIMS ×6, TE ×3,
  IBRX ×2, SIG ×2, plus GME/ARCT/SLS/WDC/DELL instances across ~six weeks.
- **Why adopt:** mechanically enforceable from the scoring DB exactly like I-4
  (already built); it closes the biggest hole in the 69% recall number.
- Recommendation: **ADOPT.** `DECISION: __________`

### Tier 2 — sound, evidence-backed, worth adopting

**I-8 — Gap rule for §9 triggers.** A level price opens beyond is void until
re-crossed; prefer closing-state triggers ("15-min close above X") over event
"break of X" triggers; the card must state what a gapped-past entry *means*.
- **Evidence: 3 gapped-past instances + a measured cost.** USO 8/26, MRNA 8/28,
  AVGO 9/3 — and on 9/16 XLE gapped 74¢ through its trigger, the protocol-correct
  entry paid 1.10 for a spread priced at 0.55 premarket and **lost 20.9%** with
  the direction right all day. Counter-example (TSLA 9/3 closing-state trigger)
  paid +5.4%. The 9/21 energy card already applied its spirit (built on XLE,
  which didn't gap, not USO, which did) and it paid.
- Recommendation: **ADOPT.** `DECISION: __________`

**I-13 — Carry-forward catalyst calendar.** Dated binaries (PDUFA, earnings,
lockups, index-inclusion) recorded by any prior brief/card/open-item stay on
§4A's checklist until resolved or explicitly retracted-with-source; a fresh API
pull may ADD dates but never silently DELETE one.
- **Evidence: one costly, self-inflicted miss.** The 9/17 brief wrote RARE's
  PDUFA "not near-term" from a fresh low-confidence pull, contradicting our own
  9/14 record of a 9/19 date — and **RARE ran +12.6% pre-binary, unwatched.**
  The information was in our own files.
- **Why adopt:** cheap insurance against a repeat; implementable from the DB
  (open_items already carry catalyst dates — the CMPS/DFTX/HELP watch went in
  tonight exactly this way).
- Recommendation: **ADOPT.** `DECISION: __________`

**I-11 — Card-QA timing rule.** Every §9 card naming a catalyst must state the
catalyst's datetime, and its triggers may only resolve *after* it — a card that
grades itself before its own event is defective by construction.
- **Evidence: 1 clear defect (ORCL 9/9 wired to resolve before its own
  after-close earnings) + 1 counter-example (9/10, fixed).** Narrow, but the
  fix is a write-time QA check at essentially zero cost and zero downside.
- Recommendation: **ADOPT.** `DECISION: __________`

### Tier 3 — rubric housekeeping (review-side, not brief-spec)

**R-1 — Recall-mover floor.** Floor the recall test at ≥3% **AND ≥$0.25**
absolute, so sub-$5 names stop tripping it on single-cent moves.
- **Evidence: 13 penny-artifact trips** (HTZ 7¢, OPEN 14¢, GPRO 5.5¢/6¢, TE
  21¢, …) inflating the recall-miss count with noise.
- **Note:** review-rubric change (`brief-review/SKILL.md`), future reviews only;
  lifetime counts not restated. Low risk, improves signal.
- Recommendation: **ADOPT.** `DECISION: __________`

**R-2 — Named-target grading.** A radar item that names a price target grades
CONF-PAID if the target prints after the trigger and before the window ends,
regardless of the window-end close. Items with no named target keep the strict
basis.
- **Evidence: 2 strict-window inversions.** SPY 9/15 (reached 756.15, closed
  −7¢ → graded FAILED; day-card version paid +6.1%) and SPY 9/16 (its own words
  "next stop 750" printed at 749.60, closed 20¢ over trigger → graded FAILED;
  day-card version paid +27.6%). The rubric currently fails a trade that hit its
  stated target whenever the tape mean-reverts by the bell.
- **One caution:** this loosens a grade, so it makes the radar number look
  better — adopt it because it's *more honest* (the target printed; a managed
  trade booked it), not to flatter the score. The day-card ledger already
  measures the divergence, so the effect is auditable.
- Recommendation: **ADOPT.** `DECISION: __________`

### Tier 4 — sound but higher-cost; scope before adopting

**I-9 — Dated corporate events on watchlist names.** Every watchlist entry
carries any dated company event in the next 5 sessions (product launches,
analyst days, lockup expiries, index-inclusion effective dates), sourced, with
earnings-calendar discipline.
- **Evidence: 2 instances** (TSLA Cybercab 8/31 quiet-lined; RDDT S&P-inclusion
  9/2 missed). Real, but thinner than the Tier-1/2 items.
- **The cost:** tracking non-earnings dated events for all ~34 watchlist names
  every morning is real work with no existing data feed — the other proposals
  reuse the DB, this one doesn't. **Recommend ADOPT-MODIFIED:** scope it to
  FLAGGED names + large caps only, and only events that surface in the news/UW
  passes the brief already runs (don't build a new sweep). Revisit widening
  after it proves out.
- Recommendation: **ADOPT-MODIFIED (scoped).** `DECISION: __________`

---

## PART 3 — Suggested ruling order

If adopting in a batch, this sequence minimizes spec churn (each is one commit
into its target spec, dated RATIFIED in `IMPROVEMENTS.md`):

1. **I-10, I-14, I-12** (Tier 1) — highest evidence, all DB/§-mechanical.
2. **I-8, I-13, I-11** (Tier 2) — sound, low-cost.
3. **R-1, R-2** (rubric-side, `brief-review/SKILL.md`, future reviews only).
4. **I-9** (scoped) — or KEEP-WATCHING for more instances first.

Whatever is adopted, I make the spec edits and the `IMPROVEMENTS.md` RATIFIED
entries as a follow-up commit **only on your explicit go-ahead** — spec changes
sit outside the review's direct-to-main authorization by design (§8 of
`brief-review/SKILL.md`).

---

## Standing owner-action items (carried, not part of the ruling)

- **Rotate the Turso token** — pasted into the session transcript 2026-09-21, a
  known exposure until rotated (§6). Second exposure alongside the UW key.
- **Morning-task reliability** — 6 incidents (double-runs / overwrites /
  late-or-failed pushes); the 9/18 and 9/21 briefs both re-ran and overwrote.
- **Confirm the cash outflows** inferred 9/18 (~$286) and 9/21 (~$76) for the
  journal.
- **Execution note (not a spec item):** the owner's chase-entry-into-a-trend is
  2-for-2 (9/18, 9/21), both rescued by disciplined exits — flagged for the
  journal because two wins is when a rule-break normalizes.
