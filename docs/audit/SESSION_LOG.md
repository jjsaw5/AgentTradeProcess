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
