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

## 2026-08-22 — uw-earnings-vol-scan vendored in as a skill

**What changed:** Added `uw-earnings-vol-scan/`, holding a third-party skill
supplied by the owner: an Unusual Whales earnings-volatility scanner that scores
upcoming earnings names for long call calendar spreads (Volatility Vibes
strategy) and walks the human through execution. `SKILL.md` is the supplied
document, byte-for-byte. `uw-earnings-vol-scan/README.md` is ours and is the
governance wrapper. `.claude/skills/uw-earnings-vol-scan` is a symlink to the
module directory so a session started from this repo loads the skill without a
second copy existing. Root README updated.

**Verification:** The skill embeds its own scanner script and requires
`--selftest` before any scan. The Python block was extracted from the committed
`SKILL.md` and run: **124/124 checks passed, zero API calls** — the count the
skill documents, so the ~1,000-line script transcribed faithfully. No live scan
was run; every live figure cited inside the skill is the vendor's, not ours.

**Decisions:**

1. *Vendored verbatim, not adapted.* Same treatment as
   `options-expert/reference/`: the body is untouched and every correction of
   ours lives in a sibling README. The skill's constants are calibrated as a
   set and its script is the specification for its own numbers, so a local
   "improvement" would silently invalidate the figures it publishes.
2. *Verdicts are `UNCALIBRATED` here (§7).* The backtest behind it (2007–2024,
   7,313 trades) is real but external; this process has neither reproduced nor
   graded it. That is reasoned, not proven, and gets labelled as such.
3. *§5 overrides the skill's sizing prose.* The skill relays a ≈6%-of-bankroll
   Kelly recommendation, which exceeds `MAX_TRADE_RISK_PCT = 0.04`. Recorded in
   the module README along with the rest: a calendar is a debit with no resting
   stop, so its risk is the full premium and it must also fit
   `MAX_TRADE_PREMIUM_USD`; the skill's own 5–10% open-exposure cap is tighter
   than `MAX_OPEN_HEAT_PCT` and the tighter number stands; an earnings night's
   Recommended list clusters by sector, which is §5's correlation rule.
4. *§2 unaffected.* The skill's "Executing a Recommended trade" section
   instructs the human. Claude scans, frames and checks structure; the human
   places every order.

**DEVIATIONS:** None. Worked from this repository's own directory, so §0's
contamination case does not apply. No credential was written, printed or
committed — `UW_API_KEY` appears by name only, `.env` was already gitignored,
and the staged diff was scanned before commit.

---

## 2026-08-22 (cont.) — dark pool wired into options-expert as E2b

**Context:** A repo audit for dark pool usage found `/api/darkpool/recent` in
active use by the brief's §8A discovery scan, `/api/darkpool/{ticker}` verified
and probed but read by nothing, and the websocket `off_lit_trades` channel
documented in `DATA_LAYER.md` §3f but absent from `tools/uw_stream.py`'s handler.
The owner asked for the per-ticker endpoint to be wired into `options-expert/`.

**What changed:**

- `options-expert/SKILL.md` — new **E2b, Off-exchange print corroboration**,
  placed after E2. Requires three computations before the layer may be cited:
  above/at/below-mid classification against the NBBO at execution, aggregate
  size as a percent of 30-day ADV, and print count with `executed_at` span.
  Adds a `CORROBORATION` line to the output card, the E2b inputs to §8 logging,
  the per-candidate pull to §3b, and the aggressor-inference caveat to §9.
- `options-expert/DATA_LAYER.md` — records that the above/below-mid split is
  **ours, not the vendor's**; flags the ticker endpoint's paging as UNVERIFIED;
  names both consumers. Split the §4 division-of-labour row that had dark pool
  sharing a line with signed flow under "nothing else has aggressor side" —
  true of options flow, not of block prints.
- `options-expert/tools/probe_uw.sh` — added `darkpool_tkr_lim` requesting the
  ticker route with an explicit `limit=200`, so the byte count can be compared
  against the unlimited call and the paging question settled by measurement.

**Decisions:**

1. *A corroboration layer that can nominate is not a corroboration layer.* E2b
   runs only on names that already passed a test, cannot be the named test
   Stage 3 requires (Stage 3's rule was amended to say so explicitly, since E2b
   is literally "a named test below"), and moves conviction at most one notch.
   It cannot kill and it cannot promote.
2. *The mid-relative split is labelled as inference everywhere it appears.* The
   tape does not mark which side initiated an off-exchange print. Calling this
   "aggressor side" would have imported the credibility of UW's options flow
   fields onto a heuristic of ours — the greek-provenance rule (§2) applied to
   flow. Cards must write "9 of 14 prints above mid", never "institutional
   buying".
3. *A size denominator is mandatory.* Aggregate premium with no ADV comparison
   is the same defect as the 2026-08-18 GEX window: a number that looks like a
   market fact and is really a fact about what was measured.
4. *Paging flagged rather than assumed.* `limit` is verified on `/recent` and
   untested on `/{ticker}`, and §3d means a bad parameter returns `200` with an
   empty array. E2b requires a row count and an `executed_at` span assertion
   before first citation, and the card says "window unverified" until
   `DATA_LAYER.md` records the check.

**Pre-registration (§9), stated before any live run:** E2b is expected to change
conviction on a minority of cards and to change the entry decision on none. A
logged card whose entry turned on E2b means the layer exceeded its remit; the
fix would be the spec, not the card.

**Not done, and deliberately:** `off_lit_trades` is still unwired —
`uw_stream.py` would join the channel and print nothing, since `handle()` has no
branch for it. Out of scope for this request; recorded here so it stays visible.

**Status:** UNCALIBRATED per `CLAUDE.md` §7, like everything else in
`options-expert/`. This is reasoned, not evidenced — no live dark pool pull was
made this session, and no card has yet cited the layer.

**DEVIATIONS:** None.

---

## 2026-08-22 (cont.) — off_lit_trades wired into uw_stream.py

**What changed:** `tools/uw_stream.py` gained a dark pool layer behind `--dark`,
closing the gap the previous entry recorded as deliberately left open. New:
`DarkPool` accumulator, `_dp_fields` parser, a handler branch, CLI flags, and an
unparsed counter surfaced in the heartbeat. `tools/test_uw_stream.py` is new —
31 offline checks, no key, no network. `DATA_LAYER.md` §3f and `SKILL.md`
Stage 7 record the wiring and its limits.

**Decisions:**

1. *Opt-in, never default.* `off_lit_trades` is the whole off-exchange print
   tape, and off-exchange is a large share of consolidated volume. Joining it
   market-wide pushes every print through `json.loads` in the processor, which
   is exactly how the client falls behind and starts taking server-side drops on
   `market_tide` and `gex` — the channels that decide things. It is absent from
   the default channel list, requires a non-empty watch list (the tool exits
   rather than firehosing), and is filtered to that list before anything prints.
2. *Emits on clusters, not prints.* Mirrors E2b's reading rule that a lone block
   means nothing and repetition is the pattern. Default gate: ≥4 prints and
   ≥$5M inside 15 minutes, with a cooldown. A single print above $25M surfaces
   separately and is labelled `not citable on its own (E2b)` so the two cannot
   be confused. The thresholds are console ergonomics, not calibrated edge, and
   say so in the code.
3. *Unclassifiable prints stay `NA_unresolved`.* When the payload carries no
   NBBO the side is `None` and is reported as its own bucket in the split. It is
   never folded into `at mid` to make the counts add up — that is precisely the
   `NA_no_data` / `NA_unresolved` collapse `CLAUDE.md` §4 forbids, and it would
   hide a parser failure inside a plausible-looking result.
4. *The schema is guessed, and the code says so out loud.* The socket payload
   for this channel has never been observed. The parser tries a short list of
   candidate keys, counts what it cannot parse, prints that count in every
   heartbeat, and dumps the first payload's keys to the console on connect so
   the real schema can be recorded in `DATA_LAYER.md` rather than inferred
   forever. A rising `dark_unparsed` with a silent console is the failure this
   guards: it would otherwise be indistinguishable from "no prints today."
5. *Per-ticker subscription left as an experiment.* `gex` and `net_flow` take a
   `:TICKER` suffix; this channel is documented bare. `--dark-ticker-channels`
   joins the suffixed form for whoever wants to establish the answer.

**Verification:** `python3 test_uw_stream.py` — **31/31 passed**, zero network,
zero credentials. Covers mid classification in both directions and at the
midpoint, the float-noise tolerance, missing-NBBO handling, notional from
`price × size` versus an explicit premium field, cluster gating on both count
and notional, the watch filter, window eviction, cooldown, the single-print
path, the `NA_unresolved` bucket, the unparsed counter, and handler routing for
both the bare and suffixed channel names. `py_compile` clean.

**What this does NOT establish:** that the live payload resembles the fixtures.
The tests prove the parser handles the shape we guessed. Only a live run settles
the schema, and no live run was made — no key is present in this repo and none
was requested.

**DEVIATIONS:** None.

---

## 2026-08-24 — dark pool paging measured; E2b's denominator was broken and is fixed

**What happened:** The owner asked how the UW data looked on TSLA. Answering it
meant a live pull, which was the first time E2b met real data — two days after
it shipped. It failed on first contact.

**The measurement.** `/api/darkpool/{ticker}` honours `limit` up to 500 and
rejects more with a `422` naming the cap; **`page` and `date` are both accepted
and silently ignored**. The route returns the most recent ≤500 prints and offers
no way back through a session. On TSLA at 12:36 ET those 500 rows spanned
**27 minutes**. Full transcript, including the pre-registration that got it
wrong, in `options-expert/log/2026-08-24-DARKPOOL-PAGING.md`.

**The defect.** E2b required aggregate block size as a **percent of 30-day
ADV** — a one-day denominator against a 27-minute numerator. On live TSLA it
produced "0.82% of 30d ADV": specific, plausible, and meaningless. Same class of
error as the 2026-08-18 GEX incident, and it survived review that morning
because the spec was written against an endpoint nobody had called yet.

**The fix.** The denominator is now rate-matched to the window actually
returned:

```
normal_rate  = ADV30 / 390
off_lit_rate = dark_shares / (normal_rate * window_min)
```

TSLA read 11.7%. E2b now also requires the row count to be checked against the
500 cap (exactly 500 = truncated by the endpoint, not by the market) and the
card to state the window in wall-clock terms rather than saying "today's dark
pool". §9 gained three new entries: E2b sees minutes not sessions, and the
off-lit rate has no baseline.

**Decisions:**

1. *Report the rate, never threshold it.* One name on one day is not a baseline.
   Nothing here establishes a normal off-lit reading for any ticker, so the
   figure is context on a card and never a pass/fail. Building the baseline is
   named as future work rather than quietly invented.
2. *Name the denominator precisely.* It includes lit volume, and UW's feed may
   not carry every off-exchange print, so it is "off-exchange prints as a
   fraction of normal TOTAL volume for an equal span" — not dark-versus-dark.
   The shorter phrasing would have been wrong in a way nobody would catch.
3. *The log entry keeps its failed pre-registration.* Per §9 and the E1
   precedent, the entry records what was expected before the calls, states
   plainly that both expectations were wrong, and was not rewritten to look
   prescient.
4. *Mid-split base rate recorded, not used.* TSLA's window was 219 above / 83 at
   / 198 below — near balanced, which is `NA_no_data` under E2b's own table. It
   is in the log as a first data point for a baseline that does not yet exist,
   flagged as unusable as a reference level.

**Incidental:** the dark pool **REST** payload schema is now confirmed and
recorded in `DATA_LAYER.md`, and every `_dp_fields` candidate key in
`uw_stream.py` hit on its first choice. That is evidence for the socket parser,
not proof — the `off_lit_trades` websocket payload has still never been observed,
and the code and docs both continue to say so.

**Verification:** `test_uw_stream.py` 31/31, `py_compile` clean. No code path
changed — this commit is a spec fix plus recorded measurement.

**Credential handling:** `UNUSUAL_WHALES_API_KEY` was read from the environment
and never printed, never written to a file, and never passed on argv. The probe
helper lives in the session scratchpad outside the repo tree. The staged diff
was scanned before commit.

**DEVIATIONS:** None.

---

## 2026-08-26 — `gex-levels` measured moving intraday; Stage 1 amended

**What happened:** The owner asked for live TSLA levels to trade against. Serving
that meant four `gex-levels` pulls across 65 minutes, which turned into a
measurement nobody set out to make.

**The measurement.** All four frames `source: "vol"`, same session:

| level | 09:36 | 09:44 | 10:05 | 10:41 | range |
|---|---|---|---|---|---|
| `call_wall` | 345.00 | 357.50 | 352.50 | 352.50 | 12.50 |
| `gamma_flip` | 341.50 | 348.70 | 351.59 | 347.28 | 10.09 |
| `gamma_magnet` | 340.00 | 350.00 | 350.00 | 345.00 | 10.00 |
| `put_wall` | 342.50 | 347.50 | 340.00 | 335.00 | 12.50 |

TSLA's own range over the window was 9.40 points. **The levels moved about as far
as the underlying did.** `gamma_magnet` held 21 minutes, looked like the one
reliable number, then moved 5 points.

**The finding that drove the amendment.** At 09:44 price sat 0.45 above the flip;
at 10:05, 3.18 below it. Price fell 0.75 while the flip rose 2.89 — about
four-fifths of the regime change came from the model moving, not the market. A
trigger reading "5-min close below the flip" would have fired on a recalculation
while price stood still.

**What changed:**

- `options-expert/SKILL.md` Stage 1 — gamma is a **character read, not a
  coordinate, and never a trigger**. Triggers, stops and invalidations stay on
  price structure that does not move underneath you. Any gamma level older than
  ~15 minutes is void. Cross-check against the static OI-based
  `greek-exposure/strike`.
- `options-expert/DATA_LAYER.md` — new §3e-2 with the table and the constraint.
- `options-expert/log/2026-08-26-GEX-FRAME-INSTABILITY.md` — the measurement, the
  failed pre-registration, and the open experiment.

**Decisions:**

1. *Pre-registration kept verbatim, and it was wrong.* At 09:36 the prediction
   was that the frame would firm up by 10:00 with ~30 minutes of volume behind
   it. It did not, and it was still moving at 10:41. Recorded as written, per §9
   and the E1 precedent, rather than quietly reframed as caution.
2. *Not called vendor error.* A volume-weighted frame rebuilding on volume is the
   endpoint working correctly. The claim is about usability as a static level,
   and the §3e rule (use vendor levels, never sum strikes) is untouched.
3. *Scope held to one expiry day.* 0DTE churns hardest into expiry, so this is
   plausibly the worst case, not the typical one. The spec says so, and the
   ordinary-session comparison is named as the next experiment instead of the
   conclusion being widened to fit.
4. *No trade card was produced all session.* Every exchange was levels and
   regime; execution stayed with the human per §2.

**Also recorded in the log entry:** `NO CLEAR DRIVER FOUND` across four news
checks between 09:36 and 10:41, spanning a 2% gap down, a 6.6-point recovery and
a 3.5-point fade. Stated as a limit of one feed rather than as an absence of news.

**Verification:** No code changed — spec and log only. Live API reads only; the
key was read from the environment, never printed, never written to a file, never
passed on argv. Probe helper lives in the session scratchpad outside the repo.

**DEVIATIONS:** None.
