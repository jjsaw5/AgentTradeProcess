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

## 2026-08-19 — Brief archive verified; live session support; 8/19 journal entry

**What changed:** Appended the 2026-08-19 trading journal entry to
`playbook/PLAYBOOK.md` §6 — full fill-level ledger (10 closes reconstructed from
Robinhood order history), grade **C**, and the decision notes. Written and
committed **before** the 2:00 PM FOMC minutes released, so the record predates
the outcome per §9 pre-registration.

**Verification performed (no changes made):**

- `briefs/2026-08-19.md` confirmed to carry all 16 spec sections including §0,
  §6A, §8A, Gamma Regime and Watchlist Alert — i.e. the run used the current
  `daily-market-brief/SKILL.md`, not a stale copy. Secret scan clean.
- Live-session data support: UW flow, GEX levels, market tide, IV rank, options
  volume; Robinhood chains, quotes, positions and orders. Read-only throughout;
  **no order was placed, modified or cancelled** (§2).

**Findings the owner should act on:**

1. **Cross-contamination is NOT resolved.** Today's brief run
   (`session_01GeR1MYALYndaTFJsBRDdyZ`, 8:57 AM ET) has source repo
   `jjsaw5/aggressive-trading-bot`. The brief output now lands here, but the run
   still starts in another repository, so that repo's `CLAUDE.md` auto-loads as
   standing instruction — the exact §0 mechanism. Fix is the run's working
   directory, not the output path.
2. **A second, stale brief producer is still firing.** Cloud Routine
   `trig_01Gsa2Gqt93asMAbVdPeRwnt` (`0 12 * * 1-5`, 8:00 AM ET) embeds ~4,000
   words of spec inline, frozen 2026-08-13, missing §0 / §6A / §8A / the UW-FMP
   data source. It fired today at 8:07 AM ET. The 8/18 session-log claim that
   "the runtime task copy was already a thin loader" is true of the 9:05 local
   run but not of this one.

**Corrections made in-session:** two of my own aggregation errors were caught
and fixed before anything was reported — UW `oi_change` is a ratio (use
`oi_diff_plain` or `curr_oi − last_oi`), and flow-alert `volume` is a running
contract total that must be taken as MAX, not summed across alerts (summing
inflated the 8/21 350C to 90,070 against Robinhood's 32,441). Also corrected a
wrong claim to the owner that he had "missed the opening runs" — the order
history shows trading from 9:36 AM.

### DEVIATIONS

**1. A credential was pasted into the session transcript — second occurrence.**
The owner sent the Unusual Whales API key in chat. Per §6 that key is
compromised regardless of who saw it, and rotation was advised. It was written
only to a scratchpad file outside the repo tree, mode 600, never committed,
never echoed in output; every staged diff was secret-scanned before commit. The
§6 standing exception from 2026-08-18 now covers a second exposure of the same
credential. **Still unrotated at the time of writing.**

**2. Data sources reported as unavailable rather than assumed:** UW
variance-risk-premium is stale (last row 2026-07-22, ~4 weeks old) and was not
used; `flow-alerts` `limit` caps at 200 (250/300 return 422), so only the oldest
day in that window is truncated; `oi-change` reflects UW's top-200 ranking, not
the whole chain. Each stated at point of use.

---

## 2026-08-19 (afternoon) — FMP data-layer repair: sector regression, VWAP closed

**What changed:**

- `options-expert/DATA_LAYER.md` §1c: recorded that
  `sector-performance-snapshot` is dead in both modes — `400` without `date`,
  and `200` with **all-zero rows** when given one. On 2026-08-18 it failed
  loudly (`400`); it now fails silently, which is worse. Documented
  `industry-performance-snapshot?date=` as the verified substitute (124
  industries, real values) and required a non-zero assertion before any breadth
  claim.
- `options-expert/DATA_LAYER.md` §1c-2 (new): the intraday VWAP and
  participation-ratio recipe, with a worked SPY example from this session.
- §5 gaps table: "No intraday VWAP from any vendor" marked **CLOSED**; the
  sector regression added as a new gap.
- `daily-market-brief/SKILL.md` §0, §7, §8: participation ratio into the setup
  block, industry-snapshot substitution + all-zero guard into breadth, and
  computed session/30-min VWAP into the levels section.

**Why:** the owner supplied an FMP key mid-session, so the FMP layer could be
probed live for the first time since 2026-08-18. Thirteen endpoints were
probed; twelve returned usable data, one regressed.

**Decision:** VWAP is labelled "VWAP (computed)" wherever it appears. It is our
number, not a vendor quote, and §3's fact/interpretation separation applies to
its provenance as much as its value.

**Note on the §1c finding:** this is the third distinct instance in this
repository of a `200` carrying a false payload (UW bad-parameter empty array,
UW default page-size truncation, now FMP all-zero sectors). The pattern is not
vendor-specific and the guard belongs at every read site, not in a vendor
adapter.

### DEVIATIONS

**1. A second credential was pasted into the session transcript, and the owner
declined rotation of both.** The FMP key was sent in chat; the owner stated
explicitly that neither it nor the Unusual Whales key will be rotated for now.
Per §6 both are compromised from the moment they were written down, and both
are now known exposures until rotated. Handling matched the UW precedent: each
key written only to a scratchpad file outside the repo tree, mode 600, never
echoed to output, never committed; every staged diff secret-scanned. This
extends the §6 standing exception to a second credential — recorded, per that
section's own reasoning, because a rule quietly broken is worse than one that
names its violation.

**2. Trading support continued alongside spec work.** Read-only throughout; no
order placed, modified or cancelled (§2). Position and sizing analysis reported
§5 breaches as found rather than softening them.

---

## 2026-08-19 (close) — journal amended with the settled ledger

**What changed:** The 2026-08-19 row in `playbook/PLAYBOOK.md` §6 was amended with
the settled close. The grade (**C**) and the decision notes were written before the
2:00 PM FOMC minutes and are unchanged — only the ledger moved.

**Settled ledger (fill-level, from Robinhood order history — 20 fills):**

- 8 intraday round trips: **-$147** (QQQ 720P -$1, SPY 769C -$65, QQQ 716P +$88,
  QQQ 711P -$134, TSLA 345C x2 +$100, QQQ 717C +$21, TSLA 345C +$16,
  MRNA 115P **-$172**)
- 3 carry closes: **+$132** (SLS $0, CVX +$60, USO +$72)
- **Net realized: -$15.** Flat at the close: $1,239.76, all cash, zero heat.

The intraday count went from 7 to 8 because MRNA was opened *and* closed on the same
session; the earlier +$157 figure was correct as of 12:21 ET and became -$15 once
MRNA was booked.

**Closing prints:** SPY 769.10 (+0.21%) below settled VWAP 770.01 (computed);
QQQ 716.08 (-0.20%); TSLA 351.12 (+4.23%) above its 350 call wall; MRNA 174.38
(**+176.97%**); TLT 83.01 (+1.65%); GLD 413.83 (+3.83%).

**Added to §6:** a "Monitoring and confirmation" note carrying four failures from
the live afternoon — tick-vs-close, the in-progress-bar trap (twice), stale alert
text asserting a closed position was open, and a "breakdown confirmed" call made on
one of §1c pattern 3's three conditions. All four are marked **REASONED, not
validated** per §7, with the proposed two-close-plus-volume fix flagged untested.

**Decision:** the proposed fix was retro-checked against this session and would have
suppressed the false call while still catching the real late break — but one session
is not calibration, so it enters as a hypothesis and not a rule.

**Recorded against the assistant:** the monitor was stood down at 15:34 reasoning
that a flat account had "nothing left to signal on." That conflated position state
with signal occurrence; the genuine break fired ~13 minutes later. No cost here, but
the reasoning was wrong and is logged rather than omitted.

### DEVIATIONS

**1. Both API keys remain compromised by owner decision.** The Unusual Whales key
(2026-08-18, again this session) and the FMP key (this session) were pasted into the
transcript; the owner explicitly declined to rotate either. Per §6 both are known
exposures until rotated. Handling: each written only to a scratchpad file outside the
repo tree, mode 600, never echoed, never committed; every staged diff secret-scanned.
Already recorded in the two entries above — restated here because the exposure is
still live at session end.

**2. No other deviations.** Trading support was read-only throughout; **no order was
placed, modified or cancelled** (§2). §5 breaches were reported as found, not
softened. Data sources that failed were named at point of use rather than assumed
(FMP sector snapshot all-zero, UW variance-risk-premium stale, UW flow-alerts limit
cap, QQQ put_wall implausible on two consecutive pulls).

---

## 2026-08-19 (evening) — stale cloud brief routine deleted

**What changed (by the owner, not by this session):** Routine
`trig_01Gsa2Gqt93asMAbVdPeRwnt` — "Daily Pre-Market Research Brief", `0 12 * * 1-5`
(8:00 AM ET) — was **deleted**. Verified absent from `list_triggers` afterwards.

**Why:** it carried the brief spec pasted inline, frozen 2026-08-13, and had drifted
badly from `daily-market-brief/SKILL.md` (now 1,118 lines / 5,414 words). Missing:
the entire `OPTIONS FLOW & MACRO — UNUSUAL WHALES + FMP` data source, `§0`,
`§6A`, `§8A`, the `§8` gamma-regime block, the dashboard's `Gamma Regime` and
`Watchlist Alert` rows, and `OUTPUT DELIVERY` — plus everything added 2026-08-19.

It was also **structurally orphaned**: no `environment_id`, no
`session_context.allowed_tools`, no `persist_session`, where every other routine in
the account has all three. With no environment it had no repo clone, so it could not
have written to `briefs/` even with the delivery section pasted in, and connector
availability was unverified while its prompt asserted Robinhood data was
authoritative. Net effect: a degraded brief pushed to the phone at 8:07 AM each
weekday, an hour before the real one.

**Consequence to watch:** the ~9:05 AM local run is now the **sole producer** of the
daily brief. There is no cloud fallback. If the desktop is asleep, there is no brief
that day. A replacement — environment attached, connectors granted, and a thin
loader reading `daily-market-brief/SKILL.md` at run time rather than a pasted copy —
would restore redundancy without reintroducing the drift. Not built; recorded as an
open option.

**Related observation, unverified:** of the eleven remaining routines, only
"AI-Trade-Agent premarket watch" (`trig_012frXueorsqZeGC7CuTXtpZ`) shows
`enabled: true` with a future `next_run_at`. The rest carry `next_run_at` values in
the past (2026-07-13 through 2026-08-13) and no `enabled` flag, which reads as
paused. Worth confirming in the Routines UI — this was inferred from the API
listing, not from the UI itself.

**Still open from earlier today:** the brief run's working directory is still
`aggressive-trading-bot`, so the `CLAUDE.md` §0 instruction-level contamination is
unresolved. Deleting the cloud routine does not touch it, and now that the local run
is the only producer, that run's governance context matters more, not less.

### DEVIATIONS

**None** beyond the two already recorded today: both API keys remain compromised by
owner decision, and trading support was read-only throughout (no order placed,
modified or cancelled).
