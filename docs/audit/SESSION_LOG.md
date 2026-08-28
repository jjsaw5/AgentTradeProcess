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
