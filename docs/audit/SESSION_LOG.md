# Session log

Required by `CLAUDE.md` §8. Newest last. Every working session appends an entry:
what changed and why, decisions and their reasoning, and a DEVIATIONS section —
with `None` written explicitly when there are none.

---

## 2026-08-18 — Options expert built; governance established

**Branch:** `claude/dev` (new, from `main` at `34ccc60`)

### What changed

Built the `options-expert/` module: a process that takes the daily brief and
looks for options mispricing rather than restating what the brief already says.

- `DATA_LAYER.md` — probe-verified inventory of FMP, Unusual Whales and
  Robinhood. Written before any spec, so the spec could not be built on
  assumed capability.
- `SKILL.md` — the process. Regime gate, five named edge tests, structure
  matrix, liquidity gates, stop-distance sizing, kill rules, output format.
- `tools/probe_fmp.sh`, `tools/probe_uw.sh` — make the inventory re-verifiable.
- `tools/uw_stream.py` — live websocket monitor; replaces 5-minute REST polling.
- `reference/` — vendored UW docs plus a README recording their errors.
- `log/2026-08-18.md` — first run (post-close).
- `log/2026-08-18-REPLAY-TEST.md` — replay of the session from the open.
- `CLAUDE.md`, this log — governance, which did not exist before today.

### Decisions

- **Probe before specifying.** Discovered FMP serves no options data at all and
  its legacy v3 API is dead for this key. Chain, greeks and IV therefore come
  from Robinhood; FMP is context only.
- **Abandoned GEX reconstruction.** Planned to compute dealer gamma from
  Robinhood gamma × OI; dropped once UW was connected, since UW measures it
  directly and splits by volume as well as open interest.
- **Use vendor `gex-levels` rather than summing strikes** — see DEVIATIONS.
- **Sizing keys off stop distance, not premium paid.** At a four-figure account
  a single near-money contract can exceed a percentage-of-equity loss budget
  while being a perfectly sound trade with a stop. Premium cap and loss cap are
  therefore separate, and the premium cap is conditional on a resting stop.
- **The whitelist in UW's published skill is a subset, not an inventory.** Its
  own text says otherwise. The API documents 207 paths against that list's 26.
  Recorded in `reference/README.md` so the correction travels with the copy.

### Findings worth keeping

- A wrong UW parameter returns `HTTP 200` with `data: []` — indistinguishable
  from a genuine empty result by status code alone.
- Default page sizes truncate silently. This produced a wrong regime read; see
  DEVIATIONS.
- Replay test found a real defect in edge test E1 on its first run: the
  implied-move test is an expiry statistic and was killing sound intraday
  trades. Fixed by splitting E1 into hold-to-expiry and intraday modes.

### DEVIATIONS

**1. Worked from another repository's governance for the whole session.**
The session's working directory was `Aggressive-Trading-Bot`, whose `CLAUDE.md`
auto-loads as standing instruction. This repository had none, so that file
governed everything written here. Its sentinel vocabulary (`NA_no_data`,
`NA_unresolved`) and the `UNCALIBRATED` convention entered `options-expert/`
without a decision, against an explicit instruction that nothing be carried
over from another repo. No file was copied; the leak was at the instruction
level. Surfaced only when the owner asked for an audit, three commits after it
began — it should have been declared in the first turn.
*Resolution:* `CLAUDE.md` §0 records the mechanism; §4 marks the vocabulary as
PENDING RATIFICATION rather than silently keeping it.

**2. Published a wrong market-structure conclusion.**
Reported that SPY sat above a dense negative-gamma shelf at 760–763 and gave a
bearish trigger from it. The finding was an artifact: `spot-exposures/strike`
defaults to ~50 rows ascending by strike, the window ended below spot, and no
strike above spot was ever in the data. Corrected within the session and before
any trade was taken; the trigger was withdrawn. The retraction is written into
`log/2026-08-18.md` inline rather than edited away.
*Resolution:* `SKILL.md` Stage 1 now uses vendor `gex-levels`; per-strike pulls
require `limit=500` and an assertion that the window brackets spot.

**3. A credential was pasted into the session transcript.**
The Unusual Whales API key was sent in chat. The owner was advised to rotate it
and declined. It is a known exposure until rotated, recorded in `CLAUDE.md` §6.
The key was never written to this repository — it was held in a scratchpad file
outside the repo tree, mode 600, and every staged diff was scanned before
commit.

**4. `__pycache__` was committed and removed in a follow-up.**
Created by an import-based unit check of the stream script. Removed, and a
`.gitignore` added.

---

## 2026-08-18 (addendum) — Sentinel vocabulary ratified

**Decision:** the account owner ratified `NA_no_data` and `NA_unresolved` as
this repository's own rules. `CLAUDE.md` §4 changed from PENDING RATIFICATION to
adopted, and now records that they originated elsewhere and were kept by an
explicit decision rather than by inertia.

This closes deviation 1 from the entry above. The vocabulary in
`options-expert/` is no longer an unratified import in active use.

**DEVIATIONS:** None.

---

## 2026-08-18 (evening) — briefs/ archive added; scheduled runs now publish here

**What changed:** The daily brief spec (`daily-market-brief/SKILL.md`) gained an
OUTPUT DELIVERY section: each scheduled run now writes its full brief to
`briefs/YYYY-MM-DD.md`, commits ("Brief YYYY-MM-DD"), and pushes. Chat output
stays the primary copy; delivery failures are reported in one line and never
block or truncate the brief. Automated runs may touch only `briefs/`.
`briefs/2026-08-18.md` was seeded retroactively with today's brief. README
updated. Requested by the owner ("the brief also placed in AgentTradeProcess").

**Decisions:** Runtime task copy needed no change — it was already a thin
loader deferring to this repo's spec, so the edit lands here per the
edit-HERE convention. One file per trading day; same-day re-runs overwrite.

**Merge note:** This session's commit raced the options-expert session's push;
resolved with a plain merge (no conflicts — their changes were new files, ours
were appends). This entry was written after that merge, hence its position
after the addendum.

**DEVIATIONS:** None.

---

## 2026-08-20 — brief-review process built; first two briefs graded

**Branch:** `claude/stock-brief-accuracy-review-z3m0v7` (remote session,
requested by the owner: "review the daily briefs for accuracy and performance
… continuous improvement of the options investing process").

### What changed

- `brief-review/SKILL.md` — the review rubric: seven fixed categories
  (facts, open read, mood, regime, radar-by-its-own-triggers, watchlist
  precision/recall, hindsight-gap analysis), anti-hindsight rules, T+1
  cadence, sentinel vocabulary per §4. **Committed before any grading was
  written**, so the rubric is on record ahead of the grades it produced.
- `brief-review/reviews/2026-08-18.md`, `2026-08-19.md` — first two graded
  reviews, against Robinhood daily + 10/30-minute bars pulled this session.
- `brief-review/SCORECARD.md` — cumulative record, seeded at n=2 of 20,
  displayed UNCALIBRATED.
- `brief-review/IMPROVEMENTS.md` — the PROPOSED→RATIFIED ledger. I-1 logs the
  §4A FDA watch retroactively (the loop ran once before this ledger existed);
  I-2 through I-5 are new PROPOSED items awaiting the owner's decision.
- `CLAUDE.md` §1 — one table row for the new module.

### Decisions

- **Radar items are graded on the brief's own written triggers, never on
  hindsight-optimal ones**, and a clean invalidation counts as a process hit.
  This is what keeps the review from being a stick to beat the brief with.
- **The 2026-08-20 brief is PENDING**, not partially graded — its session was
  in progress at review time (data pulled ~15:05 ET). Reviews run at T+1.
- **Two intraday drivers (HIMS, TSLA 8/19) were researched via web** to
  classify gaps honestly (both were intraday headlines, largely unknowable at
  9:25); sources cited in the 8/19 review.

### DEVIATIONS

**1. The first two reviews are retrospective seeding, not clean
pre-registration.** The rubric was committed before the grades were written,
but partial outcome knowledge existed while the rubric was drafted (the 8/19
and 8/20 briefs report prior-day outcomes, and the grader read all three
briefs before writing the rubric). Each review carries this note inline. The
first cleanly pre-registered review will be of the 2026-08-20 brief, graded
2026-08-21 under a rubric that predates its outcomes.

**2. Session ran from a remote environment, not the local machine.** Working
directory was a fresh clone of this repository (this repo's governance was in
force — the §0 failure mode does not apply), stated here per §0's
say-so-out-loud rule.

---

## 2026-08-20 (later) — scoring database added (Turso)

**Branch:** `claude/stock-brief-accuracy-review-z3m0v7` (same session,
continued). Owner asked for a database to store API keys, brief scores, and
process history.

### What changed

- Created schema v1 in the owner's Turso db `briefscoring-jjsaw5` (6 tables:
  `brief_reviews`, `radar_items`, `watchlist_events`, `improvements`,
  `open_items`, `credentials_registry`) and seeded it with both graded
  reviews, all 10 radar grades, 24 watchlist outcomes, the I-1..I-5 ledger,
  3 open items, and credential *metadata*. Verified by query: confs paid 3/3,
  precision 13/15, recall 13/20 — matches `SCORECARD.md`.
- `brief-review/DATA_STORE.md` — schema, workflow, and the two governance
  decisions below. `brief-review/tools/scoredb.sh` — committed helper; reads
  `TURSO_URL`/`TURSO_TOKEN` from env/gitignored `.env`, contains no secrets.
- `brief-review/SKILL.md` Output gained step 4: DB sync each review; markdown
  reviews remain the evidence record, the DB is the queryable index.

### Decisions

- **Declined to store raw API keys in the database**, though the owner's
  request named that use. §6 (owner-ratified) confines key values to
  `.env`/secret managers, and a bearer-token-reachable cloud DB is the
  "anywhere else" §6 defines as compromised. Stored instead: a
  `credentials_registry` of key metadata (name, location, exposure status) —
  the queryable part of the request. If the owner wants raw values stored
  anyway, that is an explicit §6 amendment in `CLAUDE.md`, not a quiet
  insert. Decision surfaced to the owner in-session.

### DEVIATIONS

**1. The Turso auth token was pasted into the session transcript** by the
owner during setup. Per §6's own rule it is a known exposure until rotated —
recorded in `credentials_registry` as `KNOWN EXPOSURE — ROTATE RECOMMENDED`,
and the owner was advised to rotate and then keep the new token only in
`.env`. The token was not written into the repo; the runtime copy lives in
the session scratchpad (mode 600) and dies with the container.

---

## 2026-08-21 — 8/20 brief graded; 8/19 open items resolved; 8/21 queued

**Branch:** `claude/stock-brief-accuracy-review-z3m0v7` (continued session).
Owner delivered the 8/21 brief and asked for its review; the 8/21 session was
still open at review time (~2 PM ET), so per the rubric's T+1 rule the final
8/21 grade is scheduled for after today's close. Graded now instead: the
overdue 2026-08-20 review (complete data), plus interim notes only.

### What changed

- `brief-review/reviews/2026-08-20.md` — first review under a rubric that
  predates the graded session. F 4/6 (first factual errors: two secondhand
  %-figures), O MIXED (SPY PDL-resistance hit within 4 cents; QQQ
  first-15-min tell fired false), M HIT, G MIXED, radar 3 paid / 3 fired
  with 2 OPEN into 8/26, W precision 4/9, recall 1/6.
- Resolved 8/19 carried items: RKT **CONF-FAILED** (-4.6% from trigger — the
  first failed confirmation on the books), CORZ **INVALIDATED** (<$18 kill).
- `IMPROVEMENTS.md`: I-4 gains a third instance (ARCT +6.9% one-liner'd the
  day after +25.2%); new **I-6** — %-change claims must be computed from the
  primary record, not quoted from coverage.
- `SCORECARD.md` recomputed at n=3; Turso DB synced (brief_reviews,
  radar_items ×5 new + 2 resolved, watchlist_events ×15, open_items,
  improvements; 8/21 row PENDING).
- Merged `origin/main` to pick up `briefs/2026-08-21.md`.

### DEVIATIONS

None.

---

## 2026-08-21 (post-close) — brief 2026-08-21 graded; n=4

**Branch:** `claude/stock-brief-accuracy-review-z3m0v7`. Triggered by the
scheduled post-close check-in set earlier today; first review fully clean on
pre-registration (rubric predates the session; graded after the close).

### What changed

- `brief-review/reviews/2026-08-21.md` — F 7/7, O HIT (range-day call
  textbook; QQQ gap-fill answered in 10 min), M HIT (mood now 4/4),
  G MIXED (OPEX trap/765-magnet half right, gasoline half wrong again —
  G lifetime 0/3/1), radar: TLT NO-TRIGGER, CRWV UNGRADEABLE (second I-3
  instance), NVDA OPEN, MSTR OPEN with confirmation fired at the close
  (119.24 > 115). Watchlist precision 6/10, recall 3/7 — ARCT +22.4% and
  SLS +15.4% one-liner'd mid-mRNA-halo.
- `IMPROVEMENTS.md`: new **I-7** (active-complex rule). I-2 gains a fourth
  HIMS instance; I-4 a fourth (ARCT).
- `SCORECARD.md` recomputed at n=4; Turso DB synced (review row, 4 radar
  items, 14 watchlist events, I-7, open-items updates).
- PMI actuals verified by web (Mfg 53.2, Services 56.8 vs 54.0, Composite
  56) and labeled as web-sourced — FMP keys are not present in this
  environment.

### Notes

- Closes used are 4:00 PM closing prints (~4:27 pull); the daily-bar feed
  had not settled (returned interpolated bars, which were discarded per
  their flag). Official settles could differ by cents; rows will be
  corrected if a material difference surfaces.

### DEVIATIONS

None.

---

## 2026-08-25 — brief 2026-08-24 graded; NVDA/MSTR items resolved; n=5

**Branch:** `claude/stock-brief-accuracy-review-z3m0v7`. Owner asked for
yesterday's brief graded against the realized market; standard T+1 review.

### What changed

- `brief-review/reviews/2026-08-24.md` — best graded day yet: F 7/7, O HIT,
  M HIT (5/5 lifetime), **G HIT (the first)** — QQQ's PDL break traveled to
  the written targets and died at the called 710 wall; SPY capped at the
  called 765/766 band. Radar: five cards, five clean resolutions (QQQ
  breakdown CONF-PAID with both targets hit in 25 minutes; NVDA, energy-long,
  PDD all INVALIDATED by their own written triggers; SLS NO-TRIGGER).
  Watchlist precision 6/9, recall 5/9.
- Resolved carried items: NVDA 8/20 and 8/21 cards both INVALIDATED ($210
  broke pre-print — all three NVDA bullish structures killed by their own
  invalidations before Wednesday's earnings); MSTR CONF-PAID (+2.83% from
  trigger, peak +7.3%); MRK stays OPEN to the 8/26 window end.
- `IMPROVEMENTS.md` / `SCORECARD.md` / Turso DB updated (n=5). Key finding:
  **all four 8/24 recall misses (HIMS -8.0%, TSLA -3.8%, MRNA -4.3%,
  ARCT +6.6%) are covered by pending I-2/I-4/I-7** — ratification is now the
  bottleneck; the review process has nothing further to add on recall until
  those are decided.
- Bessent presser outcome (symbolic; oil sold the news) verified via web,
  cited in the review. Friday's official settles confirmed the 8/21 review's
  near-settled prints within 3–4¢; no grade changes.
- Merged `origin/main` for `briefs/2026-08-24.md`.

### DEVIATIONS

None.

---

## 2026-08-25 (later) — I-4 ratified: fragility floor written into the brief spec

**Decision:** the account owner ratified I-4 ("fix number 1 first" — phase 1
of adopting the review process's proposals). `daily-market-brief/SKILL.md` §6A
now carries the FRAGILITY FLOOR: a watchlist name ±15% over 3 sessions or ±5%
the prior session cannot get a bare "nothing notable" one-liner — it gets one
sentence naming the trailing move and the level that matters. Evidence: five
quiet-list misses in five graded reviews, all this exact shape.

`IMPROVEMENTS.md` and the Turso ledger flipped I-4 to RATIFIED 2026-08-25.
First brief this binds: 2026-08-26 (tomorrow); the 8/26 review grades against
it. Remaining phases queued per the owner's prioritization: I-7, I-2 (+ the
must-mention automation), I-3/I-6, I-5, then the Day Card spec.

**DEVIATIONS:** None.

---

## 2026-08-25 (later) — I-7 ratified: active-complex rule (phase 2)

**Decision:** owner ratified I-7. `daily-market-brief/SKILL.md` §6A now
requires: when a MATERIAL CATALYST is classified, the brief names its
watchlist complex, and while any member is ±5% within the trailing 2 sessions
every member gets a one-line complex-status note instead of "nothing
notable." Deactivates after two quiet sessions. Evidence: ARCT +22.4% / SLS
+15.4% (8/21) and ARCT +6.6% / MRNA −4.3% (8/24) one-liner'd while the
mRNA-halo complex the briefs themselves named was still paying.

Ledger + Turso flipped to RATIFIED 2026-08-25. Binds on merge to main, same
as I-4. Next phase: I-2 (accumulation escalation) plus the must-mention
automation.

**DEVIATIONS:** None.

---

## 2026-08-25 (later) — I-2 ratified + must-mention automation (phase 3)

**Decision:** owner ratified I-2 (accumulation escalation: same flow lean in
≥3 consecutive briefs ⇒ FLAGGED with the cumulative build quantified) into
`daily-market-brief/SKILL.md` §6A, alongside a new MUST-MENTION CHECKLIST
instruction: each brief run reads `brief-review/MUST_MENTION.md` as its §6A
coverage floor, with a staleness fallback.

**Infrastructure:** the rule needs cross-brief memory, so the memory is now
mechanical rather than judgment:
- Two new Turso tables — `flow_observations` (per-brief per-name flow lean,
  seeded honestly from the archived briefs' own wording for HIMS/NVDA/SLS/
  PLTR) and `complexes` (mrna-halo seeded, activated 2026-08-19).
- `brief-review/tools/must_mention.py` — queries the DB and regenerates
  `MUST_MENTION.md` with every name tripping I-2/I-4/I-7 and the exact
  reason. Missing coverage is NA_no_data, never treated as cleared.
- `brief-review/SKILL.md` Output now requires: move_pct rows for ALL
  watchlist names daily (QUIET-OK for non-events), flow-lean recording, and
  regenerating the checklist as part of each review.

**First generated checklist** (data through 2026-08-24): ARCT (all three
rules), MRNA, SLS, MRK (complex), HIMS, SOXL, WDC (fragility), NVDA (I-2:
bull lean 4 consecutive briefs). Honest seeding note: HIMS's current streak
reads bull-bull-mixed-none per the briefs' own words, so I-2 alone would not
fire on it today — it makes the list via I-4. The rules complement rather
than overlap.

Binds on merge to main, as with I-4/I-7. Next phases queued: I-3/I-6, I-5,
Day Card.

**DEVIATIONS:** None.

---

## 2026-08-25 (later) — I-3 and I-6 ratified (phase 4)

**Decision:** owner ratified both discipline rules.

- **I-3 (no card without triggers)** → `daily-market-brief/SKILL.md` §9:
  every radar card carries a written confirmation AND invalidation with level
  and deadline; levels name their reference; two-sided cards arm both
  directions; pricing/volatility cards state a falsifiable test; same-morning
  whipsaw precedence stated when plausible. Evidence: TOL and CRWV
  ungradeable; the energy 8/24 sell-the-news branch described-but-unarmed;
  TLT "new lows" without a reference. The rule encodes the process's most
  validated finding (confirmations 8/9, invalidations 9/9).
- **I-6 (compute, don't quote, %-changes)** → DATA FAILURE RULE section:
  %-changes computed from the primary record; coverage-only figures carry
  source + UNVERIFIED; trailing-window claims name endpoints. Evidence: the
  only 2 factual errors in 31 checks were both quoted secondhand figures.

Ledger + Turso flipped both to RATIFIED 2026-08-25. Six of seven ledger items
are now ratified; I-5 and the Day Card remain queued. Binds on merge to main.

**DEVIATIONS:** None.

---

## 2026-08-25 (later) — I-5 ratified (phase 5); ledger complete

**Decision:** owner ratified I-5 into `daily-market-brief/SKILL.md` §6A: a
carry-over flag whose written price trigger has CONFIRMED must be restated
with its status, and may not be softened on flow evidence alone — only a
price development changes the call (playbook §0 applied to the brief's own
follow-through). Evidence: WDC "cooling" on 8/19 one session after its
loses-$500 trigger confirmed, followed by a −6.9% day off an exact $500.00
rejection; plus three flow-lean-vs-price flag misses (NVDA 8/19, MRK 8/20,
PLTR 8/24).

**All seven ledger items are now RATIFIED** (I-1 retroactive; I-2 through
I-7 owner-ratified 2026-08-25). Ledger + Turso in sync. Remaining queue: the
Day Card spec (brief → options-expert intake → pre-open conditional plans).
All rules bind the live brief on merge to main.

**DEVIATIONS:** None.

---

## 2026-08-25 (later) — Day Plan module built (phase 6, final phase of the program)

**Branch:** `claude/stock-brief-accuracy-review-z3m0v7`. Owner: "do both" —
build the Day Card and open the merge PR.

### What changed

- `day-plan/SKILL.md` — the ~9:20 strategy layer. Selects the brief's §9
  cards through five evidence-cited filters (trigger-complete only; intraday
  structure over gap momentum; price outranks flow; live regime gate; event
  gate), runs survivors through options-expert Stages 3–7 unchanged, and
  writes 0–3 pre-open conditional plans to `day-plan/cards/YYYY-MM-DD.md`
  with three added fields (WINDOW / DO NOTHING IF / RE-ARM). Pre-open file
  is append-only after 9:30 — the pre-registration is the product. Zero
  cards is a correct output. UNCALIBRATED until 20 graded cards.
- `brief-review/SKILL.md` Output step 6 (added 2026-08-25): reviews now grade day cards on
  their own triggers plus contract-mark payoff and adverse excursion; new
  `day_cards` table created in the scoring DB.
- `CLAUDE.md` §1: rows updated for `day-plan/` and MUST_MENTION.md.

### Decisions

- The Day Plan is deliberately a THIN layer: no new edge tests, no new risk
  math — options-expert and the playbook already own those. Its value is
  selection (what the scorecard validated) and pre-registration (what makes
  it gradeable). First live run: the first trading morning after this
  branch merges.

**DEVIATIONS:** None.

---

## 2026-08-26 — brief 2026-08-25 graded; n=6; checklist refreshed

**Branch:** `claude/stock-brief-accuracy-review-z3m0v7`. Standard T+1 review,
owner-requested. Last brief graded under the old spec (it ran ~25 min before
the seven ratified rules merged to main).

### What changed

- `brief-review/reviews/2026-08-25.md` — F 7/7 (third clean run), O MIXED
  (gap classification right; PDH support broke intraday and recovered; the
  766 call-wall observation capped the day to the penny), M HIT (6/6),
  G MIXED (fuzzy-zone framing apt; CC 89.4 landed in the scripted in-line
  band and the market shrugged as written). Radar: DKS washout CONF-PAID
  (-9.7% from the VWAP trigger) and energy unwind CONF-PAID (USO -4.58%);
  NVDA conf fired and held into tonight's print; MRK interim +3.84% the day
  after its 165C build was surfaced; BABA no-trigger. Watchlist precision
  8/9 (best on record); recall 7/10 — ARCT +7.7% missed for the fifth time
  (it was on that morning's generated checklist, which the pre-merge brief
  couldn't read); RDDT +6.4% was an afternoon headline (unknowable); OPEN
  +5.0% uncovered by any rule.
- Resolved: MRK 8/20 card closed NO-TRIGGER at window end.
- Scorecard n=6; DB synced (incl. first QUIET-OK full-coverage rows and 8/25
  flow leans per the new spec); MUST_MENTION.md regenerated — 7 names, data
  through 8/25.
- Today (8/26) is the first brief under all seven rules + the checklist —
  tomorrow's review is the test of whether the recall leak closes.

### DEVIATIONS

None.

---

## 2026-08-26 (post-close) — brief 2026-08-26 graded; first day under the full ruleset: recall 7/7

**Branch:** `claude/stock-brief-accuracy-review-z3m0v7`. Triggered by the
scheduled post-close check-in (interim grading was delivered to the owner at
3:55 PM; this entry finalizes with settled closes and the NVDA print).

### What changed

- `brief-review/reviews/2026-08-26.md` — includes the first RULE COMPLIANCE
  section: all seven ratified rules executed on their first live run,
  including the staleness fallback (checklist one day behind → rules
  hand-applied). F 7/7 (with a chart-feed vs consolidated-low provenance
  note), O HIT, M HIT (7/7 lifetime; first neutral call, on a +0.005% day),
  G HIT (second ever — SPY lived in the called 764–767 box; QQQ closed ON
  the called 711 magnet). Radar: MRNA CONF-PAID to its written 145.50
  target; QQQ card correctly stood itself down; USO bear thesis wrong but
  the I-3 armed bull trigger caught the reversal (OPEN); NVDA OPEN — the
  print beat everything (EPS $2.22, rev $96.22B, Q3 guide $108B, per CNBC)
  and slipped AH anyway; vol test resolves at Thursday's open.
- **Watchlist recall 7/7 — first review with an empty recall-gap section.**
  Precision 9/11. The five-day ARCT/HIMS leak produced zero misses.
- Scorecard n=7; DB synced (review row, 4 radar items, 23 watchlist rows,
  8/26 flow leans); MUST_MENTION regenerated (5 names, data through 8/26 —
  current for tomorrow's brief IF this branch's refresh reaches main).

### DEVIATIONS

None.

---

## 2026-08-26 (evening) — branch merged to main; review pushes now publish to main

**Decision (owner):** "merge it and make review pushes go to main
automatically." The working branch (review system + 7 graded reviews +
ratified spec + day-plan + tonight's current checklist) is merged into
`main`, and `brief-review/SKILL.md` Output gains step 8: review sessions
push their own output (brief-review/**, day-plan/cards/** grading,
SESSION_LOG) directly to `main`. Spec changes (SKILL.md/CLAUDE.md/playbook
edits) remain outside the authorization and still require the owner's
explicit go-ahead. This closes the daily checklist-staleness gap: tomorrow's
brief reads tonight's MUST_MENTION (5 names, data through 8/26).

**DEVIATIONS:** None.

---

## 2026-08-28 (morning) — review of brief 2026-08-27 (T+1, settled data)

**Trigger:** owner pasted the 8/27 brief and asked for the review.
Graded at ~9:10–9:40 AM ET 8/28 against settled 8/27 closes, 10-minute
bars (NVDA/QQQ/MRNA), and this morning's labeled premarket quotes.

### What changed

- `brief-review/reviews/2026-08-27.md` — RULE COMPLIANCE day two (all
  seven rules ran, checklist read current). F 6/6 (fifth straight clean).
  O HIT (gap-and-go answered emphatically). M HIT (8/8 lifetime).
  **G HIT — third straight** — the "walls stale after the gap, use 770/720
  rounds" substitution called the trend day's actual friction. Radar:
  NVDA hold-or-fade CONF-PAID to the called $230 magnet (high 230.47);
  QQQ gap-and-go CONF-PAID (714.53 held over PDH → 721.11);
  **MRNA CONF-FAILED — second lifetime** (bear break of 138.89 fired
  ~11:40 on volume and reversed +2.9%, a textbook playbook pattern-2
  failed breakdown); MRVL vol card OPEN to today's close (beat sold −7.6%
  AH; premarket −6.8% vs ±10.5% straddle = overpriced branch leading).
  Carried resolutions: NVDA 8/26 vol test neither-branch (open +4.6%,
  inside ±5.9%; footnote: close +7.0% outside it); USO 8/26 bull leg
  CONF-PAID (+1.5%); BABA 8/25 INVALIDATED through its written kill;
  **late carry fixed** — the 8/25 NVDA into-the-print card, dropped by the
  8/26 review's table, resolved CONF-PAID (up-branch realized, +4.6% at
  Thursday's open).
- W: precision 7/10; recall 6/7 — 13/14 across the two days under the
  full ruleset. PLTR's I-2 escalation paid +4.75% same day; HIMS +6.13%
  against the put-flip lean is flow-lean-vs-price instance #5 (its written
  29.62 level said no-short — I-5 working). Only recall miss: HTZ −3.32%
  = 7¢ on a $2.11 stock → **R-1 PROPOSED** in IMPROVEMENTS.md (recall
  floor ≥3% AND ≥$0.25, future reviews only) — a rubric change, left for
  the owner; outside the direct-to-main scope.
- Scorecard n=8 (facts 49/51, mood 8/8, radar paid 15/17, invalidations
  11/11, precision 53/73, recall 42/66). DB synced (review row, 4 radar
  items, 22 watchlist rows, 11 flow leans, R-1; stale open_items states
  flipped to RESOLVED to match their recorded resolutions).
  MUST_MENTION regenerated: 7 names, data through 8/27 — current for
  tomorrow. Pushed to the working branch and to `main` per the 8/26
  standing authorization (all files in scope: brief-review/**,
  SESSION_LOG).

### DEVIATIONS

None.

---

## 2026-09-07 (Labor Day evening) — catch-up: six reviews, 8/28 through 9/4

**Trigger:** owner asked to "pull and get caught up and give me a read out."
The review process had not run since the morning of 8/28 (six unreviewed
briefs); every brief in the gap correctly executed the stale-checklist
fallback, but the checklist itself sat at data-through-8/27 for five
sessions — a review-process failure, logged here as such.

### What changed

- `brief-review/reviews/2026-08-28.md … 2026-09-04.md` — six T+N reviews
  graded against settled Robinhood data (daily bars all names; 5- or
  10-minute bars where card triggers needed timing; VIX via the index
  feed; earnings via the Robinhood record). Highlights: Warsh-day card
  CONF-FAILED after confirming at the session top; 8/31 the best radar
  day on the books (3/3 paid) alongside the worst recall day under the
  ruleset (1/4 — TSLA's dated Cybercab event and RDDT quiet-lined);
  9/1 USO card +5.0% above trigger; 9/2 first mood MISS, DELL's clean
  kill at −6% before a +15.8% close, HIMS's I-2 call build invalidated
  (calls expired worthless); 9/3 TSLA card the biggest single-name payoff
  (+5.4% event day) and LULU's straddle demolished (−19.4% vs ±9.3%);
  9/4 TSLA fade card paid both targets, WDC's $4.2M put buyer
  wrong-footed same day, GPRO +22.3% quiet-lined (execution gap).
- `SCORECARD.md` → n=14: facts 100/104, mood 12/14, radar 28/34 paid +
  15/15 invalidations, precision 80/113, recall 79/113; vol-card series
  summarized (3 dead-heats, AVGO rich, LULU cheap).
- `IMPROVEMENTS.md` — **I-8 (gap rule for triggers)** and **I-9 (dated
  corporate events)** PROPOSED with evidence trails; both await the
  owner. R-1 (recall floor) gained three more sub-$5 artifacts.
- DB synced in one 228-statement batch: 6 review rows, 28 radar items +
  2 lineage resolutions (MRVL 8/27 vol test — corrected to its written
  open-to-open basis; MRNA 8/28 lineage closed CONF-PAID via the late
  bull leg), 143 watchlist rows, 49 flow leans, open-items updates
  (NVDA Sep-9 240C now the only radar OPEN besides MRK Sep 165C).
- `MUST_MENTION.md` regenerated: **12 names, data through 9/4, current
  for Tuesday's open** — including two automated I-2 escalations (WDC
  bear-flow streak, XLE bull-flow streak) and GPRO forced into coverage.
  Note: the 9/7 evening brief (prepped for Tuesday) ran at 7:25 PM with
  the stale file; Tuesday's scheduled 9:05 run will read the fresh one.
- Pushed to the working branch and `main` per the 8/26 standing
  authorization (scope: brief-review/**, SESSION_LOG).

### DEVIATIONS

None — with one boundary note: grading six days in one sitting is batch
work the cadence rules allow (each day graded no earlier than T+1, all
data settled), but it is exactly the failure mode the scheduled
post-close review would prevent; the offer to automate stands.

---

## 2026-09-08 (evening, ET 9/7) — scheduled post-close review stood up

**Decision (owner):** "set up the scheduled post-close." Two changes:

1. `brief-review/SKILL.md` Cadence gains the **evening-cadence amendment**
   (owner-directed): the scheduled run grades day D on the evening of D
   from settled closing data; claims needing the overnight UW/OI update
   carry OPEN to the next evening. Spec change made on the owner's direct
   instruction — outside the auto-push scope, authorized by this request.
2. A weekday Routine now fires at **6:00 PM ET (22:00 UTC)** into the
   standing review session (`trig_01Cwd7hmgvqH1pWXJejtRMor`), which holds
   the Robinhood connector and the DB credentials. A fresh-session-per-run
   design was tried first and abandoned: routines created from this
   surface cannot carry the Robinhood connector, and the environment has
   no TURSO_URL/TURSO_TOKEN variables (UW/FMP keys only). If the owner
   adds those two variables to the environment and recreates the routine
   from the claude.ai UI with the Robinhood connector attached, the
   fresh-session design becomes viable; until then, self-bind is the
   working configuration.

First fire: Tuesday 2026-09-08 ~6 PM ET (grades the 9/8 brief).

**DEVIATIONS:** None.

---

## 2026-09-08 (evening) — scheduled post-close review #1 (brief 9/8)

**Trigger:** the 6:00 PM ET routine (first scheduled fire). Graded the 9/8
brief same-evening under the evening-cadence amendment; closes are 4:00 PM
near-settled prints, labeled as such (SOXL from its settled bar).

### What changed

- `brief-review/reviews/2026-09-08.md` — F 10/10 (with a 5¢ SPY-low feed
  provenance note); O HIT (both index scripts surgical: SPY lost 769.05
  at the open and ran the scripted look-out-below to 765.99; QQQ tagged
  721.886 vs the 721.86 rejection line by 3¢ and reversed); **M MISS —
  third, same shape → I-10 PROPOSED** (no bare neutral/mixed on
  NARROW-breadth mornings); G HIT (SPY's below-768.35 acceleration +
  768-wall cap exact). Radar: energy CONF-PAID (USO +2.9%, week 4), WDC
  CONF-PAID via its own 10:30 whipsaw arbiter (+2.1%, bear-flow streak
  dead), NVDA INVALIDATED (failed gap; armed bear branch paid −1.5%),
  GME vol card OPEN to tomorrow's open. W: precision 6/7 (TE +10.1% a
  first-day flag hit), recall 7/10 (SPCX +3.7% quiet-lined again, RDDT
  −3.3%, HTZ 11¢ artifact).
- **RULE COMPLIANCE milestone: first brief since 8/27 with a current
  checklist; both I-2 auto-escalations (WDC, XLE) executed** — the full
  automation loop ran end-to-end for the first time.
- **mrna-halo complex DEACTIVATED** (deliberate edit: no member ±5% in
  the last two sessions; active 8/19–9/8).
- Scorecard n=15 (facts 110/114, mood 12/15, radar 30/36 + 16/16 kills,
  precision 86/120, recall 86/123, flow-lean instances 10). DB synced
  (48 stmts). MUST_MENTION regenerated: 6 names, data through 9/8.
- Open: GME vol card (9/9 open), NVDA Sep-9 240C final note (9/9), MRK
  Sep 165C.

### DEVIATIONS

None. (Closes graded on labeled near-settled 4 PM prints per the
amendment; officials land overnight and any cent-level drift is checked
next run.)

---

## 2026-09-09 (evening) — scheduled run #2: NO BRIEF RAN today

**Trigger:** the 6:00 PM routine. Markets were open; **`briefs/2026-09-09.md`
does not exist** — the morning brief task (which runs outside this
session's visible Routines, likely the local desktop scheduled task)
produced nothing and pushed nothing. Nothing to grade; no scorecard row
(n stays 15). `reviews/2026-09-09.md` written as a NO-BRIEF marker so the
archive shows the gap was caught same-day. **Escalated to the owner in
the evening summary — the checklist loop closed two days ago and the
brief side went down the day after.**

### Done tonight anyway

- Official 9/8 closes re-checked: every 9/8 grade stands (cent drift
  only, max DELL 39¢); the 12 drifted move_pct rows corrected in the DB
  (one materially: HTZ 9/8 is −5.0% official, crossing the I-4 line).
- Open items resolved: **GME vol card INVALIDATED by its own text**
  (opened 19.10 inside the 17.65/20.70 band; +5.3% close vs ±7.9%
  straddle — vol rich; series now 3 fair / 2 rich / 1 cheap). **NVDA
  Sep-9 240C final:** card stays CONF-PAID, but the 78k-OI calls it rode
  expired worthless (NVDA 223.70) — direction right, strike wrong. MRK
  Sep 165C interim −2.2%, dying quietly.
- 9/9 watchlist moves recorded (outcome NO-BRIEF, I-4 continuity only —
  they grade nothing; no flow leans recorded, so I-2 streaks neither
  advance nor reset). MUST_MENTION regenerated: 5 names, data through
  9/9, current for tomorrow IF a brief runs.

### DEVIATIONS

None by this process. The missing brief is the deviation — it belongs to
the morning task and is escalated, not papered over.

---

## 2026-09-10 (evening) — scheduled run #3: two reviews (9/9 T+1, 9/10 same-evening)

**Correction to last night's escalation:** the 9/9 brief DID run on time —
committed 9:14:55 AM ET Wednesday, pre-registration intact by commit
timestamp — but its push failed to reach `main` until Thursday morning.
The failure was in the morning task's push step, not its run. Yesterday's
NO-BRIEF marker file was rewritten as the full T+1 review with the
incident note preserved at the top (original text remains in git history;
CLAUDE.md §9 — not rewritten to look prescient, the correction is dated).

### What changed

- `reviews/2026-09-09.md` (T+1, officials): F 8/9 — the error is the
  **ORCL card wired to resolve before its own catalyst → I-11 PROPOSED**
  (card-QA timing rule). O/M/G all HIT (760 wall held within 94¢; the
  52-wk-high breakout attempt was rejected exactly where the hold rule
  said to wait — chasing the 9:31 high bought the top). Radar: SPY bear
  card paid to its magnet; META Muse card paid +6.55%; XLE NO-TRIGGER.
  Recall 3/6 — GME/ARCT/HTZ all mentioned leanlessly.
- `reviews/2026-09-10.md` (same-evening): F 9/9, O/M/G HIT (the 760 wall
  capped the bounce within 9¢). Radar: a kill-side day — ORCL card's
  de-risk branch fired at 2:25 and named the whole AI-complex leak;
  **XLE's 6-brief escalation took its first loss and its own armed
  sell-the-news branch caught it** (USO +5.6% while XLE fell); SPY
  fired-and-flat (−3¢); PLTR card OPEN. Recall 8/13 — **RDDT's 4th
  unflagged ≥3% move → I-12 PROPOSED** (repeat-mover rule), TE/SIG/OPEN/
  SLS also quiet-lined into ≥3% moves.
- Scorecard **n=17** (facts 127/132, mood 14/17, O 11H/6M with six
  straight HITs, G 10H/6M/1X, radar 32/39 + 18/18 kills, precision
  99/136, recall 98/143). Vol series: 6 resolved (3 fair / 2 rich /
  1 cheap), ORCL open. DB synced (91 stmts; 9/9 NO-BRIEF rows replaced
  with graded outcomes on officials).
- MUST_MENTION regenerated: **12 names through 9/10**, incl. three I-2
  escalations (XLE 6th brief, MRNA, NBIS) — current for tomorrow's
  CPI-day brief.
- Open: ORCL vol test + PLTR card (both 9/11), MRK Sep 165C (dying).

### DEVIATIONS

None.

---

## 2026-09-11 (evening) — scheduled run #4: brief 9/11 graded (n=18)

**Trigger:** the 6:00 PM routine. CPI day, ORCL aftermath, weekly opex.

### What changed

- `reviews/2026-09-11.md`: F 7/8 (GPRO 3-session % off 0.5pt — the
  computed-means-computed class); O HIT (7th straight — flipped PDH
  supports never retested); M HIT (15/18); **G HIT (11th) — the
  above-764-glue + opex-pin call WAS the day** (SPY settled 764.20 in
  the named 765 zone, QQQ 714.85 on the 715 pin; expiry-pin calls now
  3-for-4). Radar: **ORCL's failed gap** (+7.5% open on a blowout, red
  close) INVALIDATED the continuation card with the armed bear read
  paying −3%; oil-unwind card paid (USO −2.2%); the index gap-test fired
  and went flat (8th CONF-FAILED, −0.2%); SPCX card survived a 145.92
  stress test and rides to Monday's OI print.
- Resolutions: **ORCL vol test → RICH (third straight seller win**; max
  close-basis ±7.6% vs ±11.7% priced, despite a 10.4% intraday range on
  resolution day); PLTR Dec-27 190C window closed NO-TRIGGER (thesis
  expired unproven); MRK Sep 165C −6.7%, near-certain worthless.
- W: precision 4/6 (**MRNA +5.4% — the I-2 escalation's second same-day
  payoff**, flagged that morning; WDC −3.0% on the only fresh-put-buying
  flag). Recall 4/6: **SLS −14.4% quiet-lined** (worst single recall
  miss of the era, driver unattributed) and CSCO +4.4% quiet-lined.
  **DELL +12% driver also unattributed — Monday's brief must answer for
  both** (logged as an open item).
- Scorecard n=18; DB synced (54 stmts); MUST_MENTION regenerated (7
  names through 9/11; I-2 escalations: XLE 7th, MRNA 4th, DELL and USO
  new).

### DEVIATIONS

None.

---

## 2026-09-14 ~9:15 AM ET — first live day-plan run (session_011KkW5BCTCJtexFUdkGVPsU)

**What ran:** owner asked (9/14 morning) for the brief-to-options-plays
layer to run live against today's brief. First-ever invocation of
`day-plan/` since its 8/25 creation. Brief landed on main 9:01;
`day-plan/cards/2026-09-14.md` written 9:08–9:15, before the open.

- Candidate pool: 9 (5 radar cards + 4 triggered §6A flags). All 9 killed;
  3 survived every filter except Stage 6 sizing and ship as PAPER cards
  (QQQ two-sided gap, NVDA 215-reclaim vs the call build, MRNA 144 band),
  pre-registered for T+1 grading.
- **Load-bearing finding: live equity $384.73** (default margin acct,
  level 3; agentic-visible acct holds $7.35) → 4% risk cap = $15.39/trade.
  No honest structure on any candidate fits. Per §5, no stop was widened
  and no thesis shrunk to fit; the plan says "unaffordable" plainly.
- Live pulls: UW gex-levels (Fri-vintage, stated), volatility/stats
  (NVDA iv_rank 0.9 pctile Fri close — the run's best E1 fact; USO 28.9
  beats XLE 52.2 on E1b), Robinhood portfolio/positions (heat 0).
  Liquidity gates NOT run — no live option quotes premarket; stated in
  the card file.

**Decisions:**
- Sized against the default margin account by inference (the config's
  ACCOUNT field was never set; agentic account is $7.35). Stated on the
  card; owner corrects if wrong.
- Killed-at-sizing survivors shipped as labeled PAPER cards rather than
  discarded — keeps the pre-registration/grading loop alive (the module's
  calibration path needs graded cards) without pretending they are sized
  recommendations.

### DEVIATIONS

- The day-plan spec's Stage 6 kill rule strictly implies a zero-card
  output; shipping the three survivors as explicitly-labeled paper cards
  is a judgment call, logged here rather than papered over. Spec text
  unchanged (spec edits need the owner).

---

## 2026-09-14 evening — scheduled post-close review run #5 (session_011KkW5BCTCJtexFUdkGVPsU)

**Graded `briefs/2026-09-14.md` (the 9:15 re-run — the standing version;
both morning versions authored pre-open) per SKILL.md evening cadence.
n=19. First-ever day-card grading (day_cards n=3 of 20).**

- Grades: F 15/15 · O HIT (8th straight — flipped PDL capped SPY's high
  to 8 cents) · M HIT (16/19) · G HIT (12th — both indexes stalled
  inside the named flip zones) · R: 2 paid / 3 fired · 1 INVALIDATED
  (XLE 65.14 break, armed bear paid; USO green = divergence #2) · 1
  NO-TRIGGER (QQQ — right structure, 10:30 clock expired before the
  11:40–12:50 completion). W precision 10/12, recall 10/13.
- **Day cards (real contract marks):** SPY 762C CONF-FAILED −24.3%
  (fired 10:10, time-stopped 11:30; thesis validated one bar post-window,
  +21% untaken); NVDA NO-TRIGGER (clean I-5 stand-down, name −3.4%);
  MRNA 144C fired 11:25 → OPEN, **+17.5% day 1** ($5.73→$6.73),
  validation (close >145) met same day.
- Resolutions: DELL attribution ✓ (RBC $640 + $95B backlog); **SLS
  attribution ✗** (NO CLEAR DRIVER persists; closed +1.6% green —
  flow-lean #13 → I-12 evidence). SPCX carried (closed 5¢ above its
  kill; OI leg needs 9/15 print). MRK interim 13.9% OTM.
- I-12 evidence appended (HIMS 6th quiet-burn, IBRX +5.9%, SLS). New
  standing observations: #5 pre-open clocks vs gap-recovery structure
  (2 instances, one day — watch, don't propose); #6 XLE/USO divergence
  n=2.
- DB: 53 stmts (incl. first 3 day_cards rows); MUST_MENTION regenerated
  (10 names through 9/14; XLE 8th escalation, MRNA 5th, USO 4th).
- **Process incidents for the owner:** morning brief task ran TWICE
  (8:50 + 9:15 re-run) and the 9:15 push reached main after the open
  (9/9 delivery-lag family). Scheduler needs a look.

### DEVIATIONS

- Two competing pre-open brief versions existed; this review graded the
  9:15 standing version while the morning's day-plan (committed 9:16)
  was necessarily built on the 8:50 version. Both pre-registrations
  respected; the divergence is recorded rather than reconciled
  retroactively.

---

## 2026-09-15 evening — scheduled post-close review run #6 (session_011KkW5BCTCJtexFUdkGVPsU)

**Graded `briefs/2026-09-15.md` (the 9:25 standing re-run) per SKILL.md
evening cadence. n=20 — THE CALIBRATION BAR IS REACHED; owner review
due. Scorecard header updated to say so (no self-ratification).**

- Grades: F 10/10 · O MIXED (SPY closed 55¢ outside its range; the
  8-HIT streak ends) · M HIT (17/20) · G MIXED (flip-sign call worked;
  index gasoline pinned — 3rd single-complex displacement, energy) ·
  R: 0 paid / 1 fired (range-break −7¢, fired-and-flat #6) · 2
  NO-TRIGGER (TLT's auction-conditioned confirm — auction verified
  0.5bp tail / 2.53x; SMH's hold-leg refused a fade) · 2 OPEN (TCOM
  straddle, RARE tell) · W 4/7, 6/8.
- **SPCX resolved: INVALIDATED, clean kill #21** (143.54 vs the 148.18
  line, day 4). **SLS attribution resolved** (Ph3 disclosure-probe,
  brief §4A) — both halves of the 9/11 item closed.
- **Day cards (real marks):** SPY 756P CONF-PAID ≈+6% managed (3.59 →
  scale 4.02 → ratchet 3.60); NVDA 215C fired 10:00, OPEN −10.6%
  (hard exit 9/16 1 PM); USO 160C fired 10:00 via the XLE leg, OPEN
  **+31.7%** (peak +57%; exit 9/16 10:00; pipeline/cargo driver
  verified); MRNA 144C day 2 −28.9% vs entry — gave back +17.5% with
  no written exit between entry and the distant invalidation
  (management-asymmetry observation #7, logged not proposed).
- Live coaching day 2: owner watched the SPY bear trade fire, pay,
  and exit by rule in real time; declined a late USO chase on advice
  consistent with the card's own R/R; a real-money +$146 day was
  reported by the owner (fills not shared; no journal entry written).
  Owner equity read $495.68 at the morning run (deposit observed) and
  $642.08 intraday per owner screenshot.
- DB: 57 stmts; MUST_MENTION regenerated (5 names through 9/15).
  Evidence appended to R-1 (OPEN 14¢) and I-12 (ARCT leanless).
- **Owner action items:** (1) n=20 calibration review + six PROPOSED
  items; (2) morning-task reliability — 4 incidents this week.

### DEVIATIONS

- The 2:35 PM intraday addendum estimated the energy-card fire as
  "midday"; settled bars show the XLE leg armed at 10:00. Corrected in
  tonight's grading with the earlier (more adverse-inclusive) time;
  the addendum text stands unedited per §9, with the correction noted
  in the review and the addendum trail.

---

## 2026-09-16 — FOMC-day live session + evening review #7 (n=21)

**Session:** continued CCR session (branch
`claude/stock-brief-accuracy-review-z3m0v7`, pushes mirrored to main
under the standing review authorization).

- **FOMC day, live:** decision readout delivered at 2:03 via a
  pre-armed wake (+25bp to 3.75–4.00%, unanimous, first hike since
  July 2023 — verified from live coverage; dots UNVERIFIED all
  session and carried). Presser board at 2:30; trigger reads at 2:45
  (NO FIRE — whipsaw candle pierced 756.15 by a dime, closed 759;
  refused in real time) and 3:00 (**BEAR FIRE** — candle closed
  753.89). Paper SPY 9/18 754P round trip managed live by the card's
  written rules: fire addendum, 752 first scale, 750 hard scale at
  the put wall (749.60 print, immediate bounce), flat 22 minutes
  before the 3:45 deadline. Three addenda pushed in-session at 3:02,
  3:16 and 3:31 (§9 pre-registration honored at each step).
- **Evening review #7 graded `briefs/2026-09-16.md`:** F 10/10 · O
  MIXED (PDH poked on closes; the 760 magnet was the better script) ·
  M **MISS** (neutral on −0.44%; 4th miss, 4-for-4 on NARROW tapes →
  I-10) · G **HIT, emphatic** (post-presser run 756.15→749.60, wall
  terminal print, whipsaw warning worth −25%) · R 0 paid / 2 fired
  (both strict-window inversions → **R-2 PROPOSED**) · 1 no-trig · 2
  OPEN · W 7/12, 5/8.
- **Day-card ledger's best day (real marks):** SPY 754P **+27.6%**
  managed (5.19 → 6.68/6.56); NVDA 215C resolved **+30.1%** (215.50
  scale 5.18 + pre-FOMC 1:00 exit 5.10, from −10.6% interim); META
  680C **+13.5%** managed vs **−9.8% held** — the counterfactual
  measured on one fire; USO 160C resolved **+16.0%** (163-print scale
  7.75 on 9/15; deadline exit 4.55 after the overnight oil dump gave
  back the +57% peak — asymmetry exhibit #2); XLE 65/63 vertical
  **−20.9%** (EIA gapped 74¢ through the trigger; the chase doubled
  the entry cost → I-8 quantified). MRNA 144C rides (−20.1%,
  checkpoint passed at 145.65). Ledger: 9 opened / 8 resolved (5
  paid, 2 failed, 1 no-trigger) / 1 riding; every paid resolution
  used scale-at-target (observation #7 now 5-for-5).
- **Resolutions:** TCOM straddle RICH (gap +3.22% vs ±7.1%; vol
  sellers 4 straight). LEN straddle OPEN (AH −4.96% vs ±6.8%).
- **Ledger:** R-2 born PROPOSED (target-print rule for radar items);
  evidence appended to R-1 (GPRO 5.5¢, #11), I-8 (XLE chase price
  tag; META gap-entry nuance), I-10 (4-for-4), I-12 (TE wrong-lean,
  SIG 2nd quiet-line).
- DB: 65 stmts; MUST_MENTION regenerated (GME/NVDA I-2 escalations,
  SPCX I-4 floor, data through 9/16). Secret-scan clean on every push.
- **Owner action items:** (1) calibration review — n=21, seven
  PROPOSED items (R-1, R-2, I-8..I-12) all evidence-complete; (2)
  morning-task reliability (today ran clean but ~65 min late).

### DEVIATIONS

- None in grading or governance. Two process notes recorded for
  completeness: (1) no in-session addenda were logged for the USO
  10:00 exit, the META fire, or the XLE fire (the fire hours
  coincided with the day-plan write and FOMC prep) — all three were
  graded tonight from bars per each card's written text, exits at
  written deadlines; (2) the SPY 754P grading entry (5.19, next-bar-
  open convention) differs from the live-logged ask (4.72) because
  option prints are sparse — both were recorded at 3:02, the
  convention number governs the ledger.

---

## 2026-09-17 — post-Fed live session + evening review #8 (n=22)

**Session:** continued CCR session (branch
`claude/stock-brief-accuracy-review-z3m0v7`, pushes mirrored to main
under the standing review authorization).

- **Day-plan run #4** written pre-open: MRNA scale-at-open (the written
  ≈151 level gapped past), 3 paper cards (SPY gap go/fill, WDC
  hold-check, NVDA 220 shelf; WDC/NVDA declared one bet). Live equity
  read $1,212.11 — another deposit observed; 4% cap $48.48, the first
  run where a defined-risk vertical is within reach of the cap.
- **Live coverage:** morning gap read (bull check failed at 9:45,
  correctly — the day chopped); 1:00 TIPS auction covered with the
  event protocol (headline candle refused); **card 1 bull fired 1:17**
  on post-auction candles 2–3 (765C @ 1.335) and **time-exited +3.0%**
  at 3:41 (765 never approached; invalidation never threatened).
  **MRNA 144C scale-at-open @ 10.25 = +78.9% banked** — largest
  realized mark in the ledger; riding half marked +149% at the bell,
  mandatory expiry exit tomorrow.
- **Evening review #8:** F 9/10 (**RARE PDUFA "not near-term"
  contradicts our own 9/14 record of a 9/19 binary; RARE +12.58%
  pre-binary unwatched → I-13 PROPOSED, carry-forward catalyst
  calendar**) · O MIXED (3rd straight shallow-breach) · M HIT (18/22)
  · G MIXED (760/765 wall box exact; "rarely chop" chopped — 2nd
  shrinking-negative≠gasoline instance) · R 0 paid / 1 fired (SPCX
  bull, OPEN) · **3 NO-TRIGGER, all correct refusals** (WDC hold-leg
  dodged a −2.7% flush, compound-trigger save #4) · W precision
  **7/8 — best on record** · recall 8/12 (RARE/IBRX real misses;
  TE/GPRO are R-1 artifacts #12–13).
- **Resolutions:** RARE tell-watch (no tell → stand-aside per text,
  cost recorded); dots verified (16/18 ≥1 more); TIPS stats verified
  post-close (tailed: 2.653%, 2.24 cover — the intraday "in-line"
  tape read corrected on the record). LEN straddle −0.45% cumulative
  (AH spike fully reversed) and XLE put-map +0.17% adverse — both
  resolve at tomorrow's close, with SPCX, MRK 165C, and the NVDA
  9/18 220C pin-vs-fuel test.
- **Ledger:** I-13 born PROPOSED; evidence appended R-1 (#12–13) and
  I-12 (IBRX ×2, TE ×3). Scorecard n=22; day-cards 12 opened / 11
  resolved (6 paid, 2 failed, 3 no-trigger) / 1 riding.
- DB: 59 stmts; MUST_MENTION regenerated (8 names: GME/NVDA I-2 4th
  consecutive; ARCT/IBRX/MRNA/RARE/SOXL/TE I-4 floors; data through
  9/17). Secret-scan clean.
- **Owner action items:** (1) calibration review — n=22, eight
  PROPOSED items (R-1, R-2, I-8..I-13); (2) RARE PDUFA true date must
  be resolved from a primary source in tomorrow's brief; (3) tomorrow
  is expiry day — MRNA mandatory exit is the one live position.

### DEVIATIONS

- **Late file-logging:** the MRNA scale-at-open decision was stated
  in-chat pre-open but written to the card file only at 1:17 PM
  (with the card-1 fire addendum). The decision content was
  pre-registered in the plan's management table; the addendum
  timestamp discipline slipped. Noted; no grading impact (the scale
  mark is the opening bar either way).
- **Intraday label error, corrected same-day:** the 1:17 fire
  addendum called the TIPS auction "in-line" from the tape;
  official stats (tailed, weakest cover in a year) were verified
  post-close and the correction was logged in the 3:41 addendum and
  this review. The fire itself was price-conditioned and unaffected.
- No in-session addenda for the WDC/NVDA non-fires (nothing fired;
  nothing to log). None otherwise.

---

## 2026-09-18 — evening review #9 (scheduled): quad-witching day graded; the ledger's two biggest trades closed; owner's live account rode the release

- **Review:** `brief-review/reviews/2026-09-18.md` graded the standing
  ~9:20 brief (the 8:55 version was overwritten by a re-run — pipeline
  incident #5). F 18/19 (GME "Thu low 21.97" was 21.92); O HIT (both
  index scripts realized); M HIT — mildly bullish on +0.12% div-adj,
  19-for-23; G HIT (the cleanest structural call yet: pin → 2:30
  witching release → dissolved walls; QQQ closed through the 720 wall
  exactly per the OPEX caveat).
- **Radar (hardest day on record):** 0 paid / 2 CONF-FAILED — both
  first-candle traps (QQQ long confirmed on the 9:30–9:45 bar and
  reversed; USO's up line satisfied by the opening gap) → **I-14
  PROPOSED** (first-eligible-candle rule); 1 INVALIDATED (SPCX — whose
  155-pin claim broke in 30 min; pre-registered pin study resolved PIN
  LOST at 4.45% range); 1 NO-TRIGGER (INTC, protective); RARE and the
  USO down-branch carried OPEN to Monday.
- **Five carried items resolved:** LEN straddle RICH (−4.47% vs ±6.8%;
  sellers five straight), XLE map CONF-FAILED (−0.05% scratch), SPCX
  9/17 bull CONF-FAILED (−0.60%), MRK 165C worthless, RARE date =
  9/19 approved EARLY 9/17 (I-13 case file complete).
- **Day cards — the ledger's biggest day, both paid on written rules:**
  MRNA 144C RESOLVED **+85.0% blended graded** (the 155-ratchet fired
  at 10:15; graded exit 10.95 supersedes the 12:51 deadline mark per
  the card's own convention); the 2 PM release SPY 761C **+132.7%
  blended in 68 minutes** — tripwires pre-computed, headline candle
  refused, first §5-compliant entry in program history, 761-print
  scale, 3:45-wall time exit. Three protective NO-TRIGGERs (Bowman
  two-sided, INTC, NVDA — whose 220 break came only on the forbidden
  3:45–4:00 bar, closing 222.08). Ledger: 16/16 resolved, 8 paid /
  2 failed / 6 no-trigger, scale-at-target 8-for-8.
- **W:** precision 1/5 (worst on record — three failed flags had
  open-satisfied confirms, the same first-candle shape); recall 1/4
  (WDC "nothing notable" +4.12% the day after being a failed flag →
  I-12 append; DELL ceiling-only −3.38%; ARCT bullish-hold lean
  −5.14%).
- **Owner's live-account day, logged for the journal (playbook §5 —
  the human executed every order, §2):** a real morning loss (−$188.24,
  −20.3%, shape consistent with an untriggered SPY put chased in the
  10:00 dip); a real MRNA sale ~10:05 (ahead of the paper deadline,
  orderly tape); then 5x SPY 9/18 759C bought BEFORE the 2:15–2:30
  confirmation completed (~10x the §5 cap) — coached in-chat to
  bank-3/run-2 with the 760.00 ratchet; owner sold all 5 into the
  761.3–761.5 push and finished **+$386.85 (+41.76%) on the day at
  $1,313.20**, flat 50 minutes before the wall. Graded as executed:
  rule-breaking entry, rule-following exit — both named plainly in
  chat and here.
- **Ledger:** I-14 born PROPOSED; I-12 evidence appended (WDC).
  Scorecard n=23. Vol-card series 9 resolved, sellers 5 straight.
- DB: 63 stmts; MUST_MENTION regenerated (5 names: GME/NVDA I-2 5th
  consecutive, META I-2 new escalation, ARCT/SOXL I-4 floors; data
  through 9/18). Secret-scan clean.
- **Owner action items:** (1) calibration review — n=23, NINE proposed
  items (R-1, R-2, I-8..I-14), all evidence-complete; (2) morning-task
  reliability — incident #5 (9:20 re-run overwrote the 8:55 brief and
  changed trigger levels under the day plan's feet); (3) confirm the
  ~$286 morning cash outflow inferred at 9:09; (4) Monday's brief must
  carry the broken NVDA 220 shelf, RARE and USO open legs.

### DEVIATIONS

- **Unwatched ratchet on the MRNA exit:** the card's 155-line (15-min
  close below 155) fired at 10:15 while the session was mid-morning
  coaching; the paper exit was logged only at the 12:51 deadline. The
  12:52 addendum self-flagged the gap and tonight's grading applied
  the earlier, rule-correct mark (10.95 — which happened to be the
  more adverse one). Same class as the 9/15 energy-card correction.
- **Addendum figure error, corrected in the review:** the 12:52
  addendum's "closest SPY 15-min close 759.37" was actually 759.00
  (10:30–10:45 bar). No grading impact (both above 758).
- **Card-numbering drift:** the afternoon addenda called the release
  card "card 4"/"4b" against the file's own CARD 2/CARD 4 headers.
  Content unambiguous; noted.
- **Owner traded outside §5 sizing on an owner-directed 0DTE day**
  (entry before confirmation, ~10x cap): logged above and in the card
  addenda at the time, not silently. The ratified spec was not
  amended; the coaching enforced the written exits.
- None otherwise.

---

## 2026-09-21 — evening review #10 (scheduled): gap-and-go graded; radar's best day since 9/16; owner's biggest day on record; DB sync deferred

- **Review:** `brief-review/reviews/2026-09-21.md` graded the standing ~9:25
  brief (the 8:55 version was overwritten by a re-run — pipeline incident #6).
  F 6/6; O HIT (clean gap-and-go, SPY held 762 from bar 1, closed 773.53); M
  HIT (mildly bullish/broad, SPY +1.55% / QQQ +2.88%, 20-for-24); G HIT
  (negative-gamma gasoline trend day — the break traveled all day, no pullback).
- **Radar — best day since 9/16:** 3 CONF-PAID (SPY/QQQ gap → 770+; semis
  SMH/INTC, both closed big; energy XLE-bear, which correctly did NOT gap past
  its trigger — the brief built it on XLE not the gapped-past USO) / 2 OPEN
  (SPCX bear fired late −0.5% multi-day; WBD research card, OI test tomorrow).
  Each paid confirm refused a first-candle trap — the **I-14 guard's first
  live day and its first keep**.
- **Three carried items resolved:** NVDA broken-220 shelf **CONFIRMED >225
  (+2.24%)** — the 5-brief I-2 escalation's cleanest payoff, zero premature
  entry; USO down-branch CONF-PAID (−3.7%); RARE post-approval CONF-FAILED
  (−0.3%, the sell-the-news drift the card priced).
- **Day cards:** all three NO-TRIGGER and correct — SPY gap retest never
  offered (no-pullback trend), INTC retest never came (closed +12% but chase
  refused), DELL sat 568–585 (the card's own do-nothing branch). Ledger 19/19,
  8 paid / 2 failed / 9 no-trigger.
- **W:** precision 5/8 (NVDA, META +11.3%, SOXL +14.9%, MRNA +12.3%, ARCT on
  its 16-breakdown level; misses GME 5th-lean-no-price, DELL, WDC); recall 8/8
  on the checked core movers (full 34-name sweep deferred with the DB).
- **Owner's live-account day (playbook §5; §2 human executes):** 7× 0DTE index
  calls bought into the running gap (a chase entry, ~88% of the account, the
  same shape as 9/18 — now 2-for-2), then managed textbook: banked 5 of 7 into
  the first wall touch, ran 2 on written ratchet/break rules, flat by ~11:20.
  Account **$1,237 → $3,426, +$2,189 / +177%** — the largest day on record.
  Journaled, not card-graded. Rule-breaking entry, rule-following exit; the
  exit is the repeatable half, and two wins on a chase is exactly when the
  discipline erodes (standing observation #9).
- **Ledger:** no new numbered PROPOSED item; standing observation #9 added
  (trend-day card silence — watch-not-propose). Scorecard n=24.
- **DB sync DEFERRED:** the weekend container recycle wiped `turso.env` and the
  local `.env`; the owner had not re-provisioned the Turso token by 6 PM, and
  per §6 it was not requested into chat. The markdown review is authoritative;
  the DB and MUST_MENTION.md (left at its 9/18 generation) catch up when the
  token returns. Tomorrow's brief must hand-apply I-2/I-4 and note the
  checklist staleness in §13.
- **Owner action items:** (1) re-provision the Turso token to the deployment
  secret store or a gitignored `.env`; (2) calibration review — n=24, nine
  PROPOSED items (R-1, R-2, I-8..I-14); (3) morning-task reliability —
  incident #6 (9:25 re-run overwrote the 8:55 brief); (4) the chase-entry
  pattern (2-for-2) for the execution journal.

### DEVIATIONS

- **DB sync not performed** (Turso credentials wiped by the container recycle,
  not re-provisioned by review time). Declared here rather than silently
  skipped; the review, scorecard, card annotation and this log were still
  written and pushed. Sync + MUST_MENTION regen owed once the token returns.
- **MUST_MENTION.md not regenerated** (depends on the DB) — it remains at its
  9/18 data, now 2 sessions stale; flagged for tomorrow's brief to hand-apply.
- **Owner traded outside the written cards** (7× 0DTE chase entry, ~88% of the
  account) on a self-directed basis — logged in the card addenda in real time
  and journaled in the review, not silently. The ratified §5 limits were not
  amended; the coaching enforced the written exits.
- None otherwise.

---

## 2026-09-21 (late) — deferred DB sync COMPLETED + credential exposure

- The owner provided the Turso token to unblock the sync deferred at the 6 PM
  review. Rebuilt the recycle-wiped tooling in the gitignored scratchpad
  (`db_exec.py` via the Turso HTTP pipeline API, creds from env only), ran
  **sync0921.py — 43 statements OK** (brief_reviews now n=24; 9/21 radar_items,
  3 day_cards, watchlist_events, flow_observations, and the carried open-item
  resolutions: NVDA 220-shelf CONFIRMED, USO down-branch CONF-PAID, RARE
  CONF-FAILED). **MUST_MENTION.md regenerated — data through 2026-09-21** (7
  names; GME/NVDA I-2 6th consecutive, META I-2 4th + I-4, ARCT/INTC/MRNA/SOXL
  I-4 floors) and committed. Tomorrow's brief reads a current checklist — no
  hand-application needed.
- Added an open_item for the owner's **psychedelics MAHA-summit watch
  (CMPS/DFTX/HELP)** — CMPS the only near-term catalyst (year-end FDA NDA),
  DFTX 1H27, HELP 2028; summit ~Sept 20–22 is sentiment, not a binary; the
  9/22 brief should pin the date and add a flow read. **Owner to add the three
  tickers to the "Options plays" Robinhood watchlist** (the live-fetched list;
  §2 keeps my brokerage access read-only, so the owner edits it in the app).

### DEVIATIONS

- **CREDENTIAL EXPOSURE (§6):** the Turso `TURSO_AUTH_TOKEN` was pasted into
  the session transcript by the owner to enable the sync. Per §6 a key written
  into a transcript is compromised and must be rotated regardless of who saw
  it — this is a **new known exposure**, second to the standing UW-key exposure
  (2026-08-18). It was used once to complete tonight's sync, stored only in the
  gitignored scratchpad `turso.env` (mode 600), never printed, echoed, or
  committed; every staged diff was secret-scanned clean. **ACTION REQUIRED:
  rotate the Turso database token** and re-provision the new one to the
  deployment secret store / gitignored `.env`. Until rotated, this token is a
  known exposure.
- None otherwise.
