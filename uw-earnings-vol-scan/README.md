# uw-earnings-vol-scan — provenance and how it sits under this repo's governance

`SKILL.md` in this directory is a **third-party skill, vendored verbatim**. It
was authored for Unusual Whales' subscriber audience around the Volatility
Vibes earnings-calendar-spread backtest, and was added to this repository on
2026-08-22 at the account owner's request.

This file is the wrapper `CLAUDE.md` requires. It is *not* part of the skill.
Nothing here edits the skill's body.

---

## Where it lives, and why

| Path | What it is |
|---|---|
| `uw-earnings-vol-scan/SKILL.md` | The vendored skill, byte-for-byte as supplied. |
| `.claude/skills/uw-earnings-vol-scan` | Symlink to this directory, so a session started from this repo loads the skill. One source of truth, no second copy to drift. |

**Do not edit `SKILL.md` to fix something.** It is a vendored artifact, like
`options-expert/reference/`. Corrections belong in this file, where they are
visibly ours; changes to the skill itself belong upstream. The skill's own text
is emphatic on this point for the embedded script in particular, and it is right
to be: the four constants are calibrated as a set, and the script is the
specification for every number the skill produces.

## Verification performed on import (2026-08-22)

The skill's `--selftest` is the check it asks for before any scan. The Python
block was extracted from `SKILL.md` and run:

```
selftest: 124/124 checks passed
All checks passed with zero API calls. Safe to scan.
```

124 is the count `SKILL.md` documents, so the embedded script transcribed
faithfully into this repository. **Re-run this after any change to `SKILL.md`,
and never scan from a copy that fails.** From the repo root:

```bash
python3 - <<'PY'
import re
src = open('uw-earnings-vol-scan/SKILL.md').read()
open('/tmp/uw_earnings_vol_scan.py','w').write(
    re.findall(r'```python\n(.*?)```', src, re.S)[0])
PY
python3 /tmp/uw_earnings_vol_scan.py --selftest
```

No live scan has been run from this repository. The skill's live-scan figures
(the 2026-07-15 runs it cites) are the vendor's, not ours.

## §7 — what is proven here, and what is only reasoned

**Nothing in this skill has been validated by this process.** Its filters,
thresholds and verdicts come from an external backtest (US equity earnings
2007–2024, 7,313 trades) that this repository has neither reproduced nor
audited. Under `CLAUDE.md` §7 that is *reasoned*, not *proven* — the strongest
class of reasoned, since it cites a real out-of-sample record, but still not
this process's evidence.

**Therefore every verdict this skill produces is `UNCALIBRATED` in this
repository's terms**, exactly as `options-expert/` output is. The skill's own
framing says the same thing in its own words ("'Recommended' is a label, not a
recommendation"); the two rules agree, and the strict reading governs.

The path off `UNCALIBRATED` is the same as everywhere else here: log the inputs
before the outcome is known, grade against the real mark later. If this skill
starts driving trades, its cards belong in a log alongside `options-expert/log/`.

## §5 — this repo's risk limits bind over the skill's sizing prose

Where the skill's §5 ("Position sizing") and `CLAUDE.md` §5 disagree, **this
repository's limits win.** They are the account owner's, set on 2026-08-18, and
a vendored document cannot raise them.

The specific conflicts, so nobody has to derive them mid-trade:

- The skill relays the Volatility Vibes recommendation of **≈6% of bankroll per
  trade** (10% Kelly). That **exceeds `MAX_TRADE_RISK_PCT = 0.04`** and is not
  available here. The skill's own practitioner refinement (1–2%) sits inside
  the limit and is the one to use.
- A long call calendar is a **net debit with no resting stop**, so under §5 its
  risk is the **full premium**, which must fit `MAX_TRADE_RISK_PCT` on its own
  *and* under `MAX_TRADE_PREMIUM_USD = 400`. Debit × contracts × 100 is both
  the max loss and the spend.
- The skill's "cap open exposure at ~5–10% of bankroll" is **tighter** than
  `MAX_OPEN_HEAT_PCT = 0.12`. Tighter is fine; take the tighter number.
- The skill's own warning that a night's Recommended list clusters by sector is
  §5's **correlation rule** arriving from the other direction: names driven by
  the same thing are one bet against `MAX_CONCURRENT = 4` and combine against
  the per-trade limit. An earnings-night calendar book is exactly that case.
- Equity is read live from the brokerage on every run. Never size off a
  remembered account value.

## §2 — no order placement

Consistent, and worth stating because the skill contains a section titled
"Executing a Recommended trade": that section instructs **the human**. Claude
frames the trade, pulls the data, and checks the structure. The human places
every order. Read-only brokerage access is unchanged by this addition.

## §6 — the API key

`UW_API_KEY` is referenced by name only, here and in the skill. The skill's
script reads it from the environment or a local `.env`; `.env` is already in
this repo's `.gitignore`. Never commit it, and note `CLAUDE.md` §6's standing
exception: the UW key pasted into a transcript on 2026-08-18 is a known
exposure until rotated. This skill increases how often that key is used, which
makes rotating it more worthwhile, not less.

## §4 — sentinels

The skill's script emits `-` for a missing expected move and reports skipped
tickers with a specific per-ticker reason rather than a sentinel. That is its
own vocabulary and it is internally honest: it never substitutes `0.0` for a
missing measurement, and it distinguishes "no value" from "could not be
resolved" through the skip reason. `CLAUDE.md` §4's sentinels govern **this
repository's** exports; if a scan's output is ever written into a repo artifact,
translate at that boundary — `NA_no_data` for a field the name genuinely lacks,
`NA_unresolved` for a name the script skipped.

## Known tension worth watching

The skill's honesty posture and this repo's are close but not identical. The
skill is a *product* for newer traders: it leads with the strategy and sets
expectations after. `daily-market-brief/SKILL.md` and `playbook/PLAYBOOK.md`
lead with the counter-case. Nothing in the skill violates §3 — it labels its
uncertainty, cites its source, and refuses to hand-estimate — but when its
output is presented alongside this process's own work, present it under this
process's rules: counter-case first, `UNCALIBRATED` on every verdict.
