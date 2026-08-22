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

## 2026-08-22 — TSLA 0–5DTE module: project setup

**Branch:** `claude/tesla-options-trading-setup-aoqwsr`

Working directory was **this repository**, so `CLAUDE.md` governed from the first
turn (cf. §0 and the 2026-08-18 deviation).

### What changed

Step one of a TSLA-focused options process, requested by the owner: "TSLA stock
in the options market, 0–5DTE, main focus 0DTE, run in Claude Code and not a
separate application."

- `tesla/CHARTER.md` — scope, the expiration-calendar constraint, the risk
  configuration, what transfers from the playbook and what does not, the UW gap,
  calibration status.
- `tesla/DATA_LAYER-TSLA.md` — TSLA-specific verified inventory, probed today.
- `tesla/tools/probe_tsla.sh` — re-verifier; run end-to-end before committing.
- `tesla/log/` — the card record, empty.
- `.claude/skills/tsla-{open,scan,watch,close}/SKILL.md` — the four session
  commands the owner selected.
- `CLAUDE.md` §1, §5a, §7 and `README.md` — governance and index.

Existing modules untouched: `daily-market-brief/`, `options-expert/`,
`playbook/` all run as before. The owner chose a new module over a full pivot
specifically so the SPY/QQQ-validated record is not retargeted on assumption.

### Findings from the probes — each one changed the design

1. **TSLA has no daily expirations.** The live chain is Mon/Wed/Fri
   (`08-24, 08-26, 08-28, 08-31, 09-02, 09-04`, then weeklies). 0DTE is a
   three-day-a-week strategy; Tue/Thu the floor is 1DTE. A process assuming
   daily expiries would have traded 1DTE twice a week and mislabelled its log.
2. **Force-close is 15:30 ET, not 15:45.** `sellout_time_to_expiration: 1800`,
   confirmed per-contract as `sellout_datetime 2026-08-24T19:30:00Z`. The
   playbook's 3:30 "decision bell" is TSLA's *liquidation* moment, so the
   charter moves the bell to 15:00 and the hard exit to 15:25.
3. **The OI liquidity gate does not transfer.** Near-dated TSLA OI is tiny
   against same-day volume — the 8/24 365P showed OI 63 against volume 22,541.
   A `< 250 OI` gate would reject the most-traded contracts on the chain.
   Same-day volume is the liquidity test on TSLA; OI is context.
4. **The 5% spread gate is near-binding, not generous.** At Friday's close only
   two of six near-money contracts passed (4.8%); ITM ran 11–15%. SPY near-money
   runs ~0.6%. Recorded with the caveat that these are *closing* spreads and
   need an RTH re-probe before any threshold is changed.
5. **Theta is worse than the SPY precedent.** 2DTE ATM call −32.6%/day, 2DTE OTM
   call −66.8%/day, against the ~55%/day that `options-expert/SKILL.md` already
   calls brutal.
6. **No UW key in this environment.** `UNUSUAL_WHALES_API_KEY` unset; probe
   returned `authentication_required`. Edge tests E2 and E3 cannot run and the
   regime gate has no input. The specs report `NA_unresolved` and declare the
   degraded state at the top of every scan — **not** "neutral", which would be a
   fabricated reading.
7. **Next TSLA earnings 2026-10-28**, outside every 0–5DTE window, so E4 is
   dormant for earnings and re-arms the week of 2026-10-19.
8. Strike spacing is $2.50 near the money and the option tick is $0.05 at/above
   $3.00 — so the playbook's 15-cent stop buffer is exactly 3 ticks and
   transfers, but as a tick-aware rule rather than a fixed number.

### Decisions

- **Probe TSLA before specifying anything**, per the 2026-08-18 precedent. Six
  of the eight findings above would have been wrong assumptions otherwise.
- **`MAX_TRADE_RISK_USD = 450`, ratified by the owner.** Recorded in `CLAUDE.md`
  §5a with the number it replaced ($50.79 at the live equity read) so the size of
  the change stays visible. The owner was shown the arithmetic — 35.4% of equity
  on one trade, three max losses exceeding the account — and set the number
  anyway; that is their call and it is theirs on the record.
- **`MAX_CONCURRENT = 1` is derived, not chosen.** §5's correlation rule
  collapses to one bet in a single-name universe.
- **The resting-stop requirement is restated as an independent hard rule.**
  Raising per-trade risk to $450 above a $400 premium cap means unstopped
  premium now clears the risk cap, so §5's arithmetic no longer forces a stop.
  `CHARTER.md` §3c preserves the intent explicitly. Flagged to the owner rather
  than changed silently.
- **Volume floor is provisional and labelled as such.** Measured from 780 FMP
  5-min bars over ten sessions; the playbook's portable "40% of the opening
  half-hour" form gives a threshold that swings 4× on TSLA (72,544 to 304,124)
  and pointed the wrong way on 2026-08-14. Provisional floor ~185,000, re-arm
  ~237,000, `UNCALIBRATED`, FMP feed units only.

### DEVIATIONS

**1. Every liquidity and greek figure recorded today is a closing snapshot, not
a live reading.** The session ran on a Saturday with the market shut; the
Robinhood quotes carry `updated_at 2026-08-21T19:59:59Z`. `DATA_LAYER-TSLA.md`
states this at the top and repeats it against each affected number, and no
threshold was changed on the basis of them. It is recorded as a deviation
because a data layer verified out-of-hours is weaker evidence than one verified
during RTH, and the file's own standard is verification by probe.
*Resolution:* re-run `tesla/tools/probe_tsla.sh` and the Robinhood calls in §2
during regular trading hours before the spread gate is trusted or tuned.

**2. Two of five edge tests are unavailable and the module was still built.**
E2 and E3 depend on Unusual Whales and no key exists in this environment.
Shipping a scan process that cannot run 40% of its own tests is a real
limitation, not a formality.
*Resolution:* not concealed — `CHARTER.md` §5 and `/tsla-scan` §0 declare it at
the top of every run, the regime reports `NA_unresolved` rather than a value,
and the fix is one environment variable.

**3. A ratified risk limit was raised 8.9× and this session wrote it down
rather than resisting it.** $50.79 → $450. The arithmetic was put to the owner
before they answered, and again after, including the collateral effect on the
stop rule. They confirmed the number.
*Resolution:* recorded in `CLAUDE.md` §5a with both numbers, the live percentage,
the fall-in-equity table, and a $1,000 floor at which sizing stops.

**4. Nothing in this module has been validated.** Stated in `CLAUDE.md` §7 and
`CHARTER.md` §6 rather than left implicit. No card has been written, no session
graded, and `tesla/log/` is empty.

---

## 2026-08-22 (later) — Unusual Whales key added; the edge layer goes live

**Branch:** `claude/tesla-options-trading-setup-aoqwsr`

### What changed

The owner supplied a UW API key. The `tesla/` module was built hours earlier
around the *absence* of one, so this reverses the largest limitation in it.

- `.env` (gitignored, mode 600) holds the key; `.env.example` (committed)
  documents variable **names** only. `tesla/tools/probe_tsla.sh` sources `.env`.
- `tesla/DATA_LAYER-TSLA.md` — new §7, the TSLA UW inventory: 20 of 20 probed
  endpoints returned 200 with data. §0 status table, gaps table and section
  numbering updated.
- `tesla/CHARTER.md` §5 rewritten from "the layer is dark" to what each of the
  five edge tests now runs on, plus the three cautions the probe surfaced.
- `.claude/skills/tsla-scan/SKILL.md` — preflight, Stage 1 regime, E1, E2, E3,
  E4, E5, the structure matrix and the card format all rewritten against live
  endpoints. E2 and E3 go from "cannot run" to full procedures.
- `.claude/skills/tsla-open/SKILL.md` — gamma walls and the vol read are live.
- `.claude/skills/tsla-watch/SKILL.md` — flow tripwires and the websocket
  monitor (`options-expert/tools/uw_stream.py --tickers TSLA`) replace polling.
- `tesla/tools/probe_tsla.sh` — probes 12 TSLA endpoints, prints the rate-limit
  headers, runs the §3e bracket assertion, and **auto-flags the E5 outlier**.
- `options-expert/DATA_LAYER.md` §5 — the "rate limits unmeasured" gap is now
  measured and closed.
- `options-expert/reference/README.md` — records that the upstream skill doc is
  unchanged as of 2026-08-22, so no second copy was vendored.
- `CLAUDE.md` §6 — the second credential exposure, and how a key *should* reach
  this repository.

### Findings

1. **All 20 probed TSLA endpoints return data**, including six absent from UW's
   published whitelist (`gex-levels`, `volatility/stats`, `iv-rank`,
   `term-structure`, `max-pain`, `historical-risk-reversal-skew`). This is the
   third confirmation that the whitelist is a guardrail, not an inventory.
2. **First TSLA regime read in this repository.** `gamma_flip` 351.08 against
   spot 362.86 → positive gamma, GLUE, at Friday's close. `call_wall` 400,
   `put_wall` 350, `gamma_magnet` 350.
3. **The magnet and max pain disagree** — 350 vs 337.5–340 on the near
   expiries. Reported as a disagreement rather than resolved, per Stage 1.
4. **The §3e bracket assertion passes on TSLA** — 202 rows, 113 strikes above
   spot and 89 below. Wired into the probe so it is checked, not remembered.
5. **`historical-risk-reversal-skew` printed a 60× outlier on 2026-08-21**
   (−0.0101 → −0.6636 against a stable −0.010/−0.030 band, on an OPEX Friday).
   Treated as an anomaly requiring a second session to confirm, not a reading.
   E5 is therefore degraded by data quality rather than by access.
6. **`variance-risk-premium` lags ~28 days on TSLA** (newest row 2026-07-24),
   and `volatility/realized` returns `realized_volatility: null` on recent rows.
   The IV-vs-RV comparison must come from `volatility/stats`, which carries both.
7. **`interpolated-iv` uses `days`, not `dte`, and `volatility`, not `iv`.**
   My first probe asked for `dte`, got nulls, and I nearly recorded an API
   defect that did not exist — see DEVIATIONS.
8. **Rate limits are not a constraint** and there is no `/api-usage` endpoint;
   limits arrive as `x-uw-*` response headers.
9. **IV is cheap in its own range but rich against realized** — `iv_rank` 14.19
   with IV 0.408 over RV 0.373. The two halves point opposite ways and the spec
   now requires both to be stated.

### Decisions

- **Did not vendor a second copy of the UW skill doc.** The pasted text is
  byte-identical to `options-expert/reference/uw-api-skill.md` (fetched
  2026-08-18) across every marker checked. A duplicate would have two copies of
  a document whose known errors are recorded once. Re-confirmation noted in the
  reference README instead.
- **The pasted doc's "strict whitelist" instruction was not adopted.** Following
  it would forbid six endpoints this module depends on and which demonstrably
  work. The repository's existing correction stands.
- **E5 degraded rather than disabled.** The trajectory through 2026-08-20 is
  usable; the single outlier is not. Encoded as a rule and an automatic check in
  the probe rather than a note someone has to remember.

### DEVIATIONS

**1. A credential was pasted into the session transcript — the second time in
five days.** Under `CLAUDE.md` §6 the key is compromised from the moment it was
typed, regardless of who saw it. Rotation was recommended immediately and again
in this entry; it is outstanding. The value was written only to the gitignored
`.env` (mode 600), never to a tracked file, and the staged diff was scanned for
both the literal value and key-shaped strings before commit.
*Resolution:* `CLAUDE.md` §6 now carries both exposures and states the correct
channel — set the variable in the environment and say it is there, never paste
the value. This remains an open exposure until the key is rotated.

**2. I nearly recorded a defect that was my own bug.** The first probe requested
`dte` from `interpolated-iv`, received nulls, and I began writing it up as "the
DTE field is null for TSLA — the endpoint is unusable." The real field is
`days`. Caught by re-reading the raw payload keys before publishing. It is
logged because the honesty rules cut both ways: inventing a vendor failure is
the same class of error as inventing a driver, and a wrong entry in a data layer
that other specs treat as ground truth would have propagated silently.
*Resolution:* the correct field names are recorded in §7c, and the raw key list
is checked before any "field is missing" claim.

**3. Two data-quality findings are stated on a single observation each.** The
E5 outlier and the VRP lag are each one probe on one Saturday. They are written
as "verify before use" rather than as established behaviour.
*Resolution:* the probe re-checks both on every run and flags the outlier
automatically; a second session either confirms or clears them.

**4. All UW readings recorded today remain a Friday-close snapshot.** The
market was shut. Deviation 1 of the earlier entry still stands unresolved for
the same reason, and now covers the UW numbers too.
