# RTH probe — schedule and its two open blockers

Created 2026-08-22. Three Routines, weekdays, one per sample in
`PREREGISTRATION.md`. They fire a **fresh session** each time, run the probe,
append to `tesla/log/rth/YYYY-MM-DD.md`, and push to
`claude/tesla-options-trading-setup-aoqwsr`. They touch nothing else.

| Sample | ET | Cron (UTC) | Routine ID |
|---|---|---|---|
| A — post-open, entry window | 09:47 | `47 13 * * 1-5` | `trig_01EjvbocxB2KKHjxUJ2aUhfD` |
| B — doldrums, volume floor | 13:33 | `33 17 * * 1-5` | `trig_013iPtUtCghE64ND5Hm6rfku` |
| C — exit window, past the bell | 15:03 | `3 19 * * 1-5` | `trig_016hTqkKvKZTrb3w3ETGtD9X` |

First fire: **Monday 2026-08-24**, which is a 0DTE day.

**Session-cron was not used.** `CronCreate` jobs live only inside one Claude
session and vanish when it ends; this container is ephemeral. Routines are
account-level and survive.

---

## DST — these will be an hour wrong on 2026-11-01

Routine crons are evaluated in **UTC** and do not follow US daylight time.
They were set while ET is **EDT (UTC−4)**. When ET returns to **EST (UTC−5)**
on **2026-11-01**, every fire lands an hour early:

| Sample | Intended ET | After 2026-11-01, without a fix |
|---|---|---|
| A | 09:47 | 08:47 — **pre-market, before the open** |
| B | 13:33 | 12:33 |
| C | 15:03 | 14:03 — **before the decision bell** |

Sample A would fire before the market opens and self-abort; Sample C would miss
the window it exists to measure. **On 2026-11-01, add one hour to each cron:**
`47 14 * * 1-5`, `33 18 * * 1-5`, `3 20 * * 1-5`. Reverse it when EDT resumes.

---

## Blocker 1 — the UW key is not in the environment

`UNUSUAL_WHALES_API_KEY` currently lives only in the gitignored `.env` of one
ephemeral container. **A scheduled session starts from a fresh container and
will not have it.** `FMP_API_KEY` *is* in the environment config, so the FMP
half runs; the UW half will report `NA_unresolved` on every firing until this
is fixed.

**Fix:** set `UNUSUAL_WHALES_API_KEY` as an environment variable in the Claude
Code environment settings (the same place `FMP_API_KEY` is set), not in a file.
That is also the channel `CLAUDE.md` §6 asks for — the variable set directly,
never the value pasted into a session.

Blocked while this holds: the live regime read, the E5 skew follow-up (**P4**),
the flow section, and the freshness measurements for the two UW feeds in **P3**.

## Blocker 2 — the Routines carry no Robinhood connector

`create_trigger` refused the `connectors` parameter: *"not available for this
organization."* The Routines therefore fire **without any `mcp__*` tools**, and
Robinhood is the only source of an option chain — FMP serves no options data at
all (`options-chain` and `options/quote` both 404).

**Blocked while this holds: P1 and P6** — the live spread gate and the real
theta burn. Those are the two measurements the whole RTH exercise was built for.
The probe degrades honestly rather than substituting: each sample records
`P1/P6: NA_unresolved — no Robinhood connector in this run`.

**Fix, either one:**

1. Recreate these three Routines from the **claude.ai Routines UI** with the
   Robinhood connector attached, using the prompts already stored on them; or
2. Run `/tsla-open` and `/tsla-scan` interactively during a session — an
   interactive session *does* hold the connector, and either command records
   the same chain measurements.

Until one of those happens the schedule measures P2, P3 (FMP leg), and P5, and
records the rest as unresolved. That is two of six predictions on a good day —
worth having, and not what was asked for.
