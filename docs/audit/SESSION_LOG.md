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
