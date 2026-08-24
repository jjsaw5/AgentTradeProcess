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

## ~~Blocker 1 — the UW key is not in the environment~~ — RESOLVED 2026-08-24

`UNUSUAL_WHALES_API_KEY` currently lives only in the gitignored `.env` of one
ephemeral container. **A scheduled session starts from a fresh container and
will not have it.** `FMP_API_KEY` *is* in the environment config, so the FMP
half runs; the UW half will report `NA_unresolved` on every firing until this
is fixed.

**This cannot be fixed from inside a session.** There is no tool that writes
environment configuration, and `FMP_API_KEY` is not set by any file in the repo
or by a dotfile — the platform injects it directly into the container's process
environment. The only two in-session alternatives are both wrong: committing the
value to `.claude/settings.json` would put a credential in git history
permanently, and writing another container-local file recreates the same problem.

**Fix — owner action, in the claude.ai web UI:**

> claude.ai/code → Environments → **Default**
> (`env_01Vboeyh6hiThjfupiAj2yWG`, `anthropic_cloud`) → environment variables
>
> ```
> UNUSUAL_WHALES_API_KEY = <the rotated key>
> ```

Same place `FMP_API_KEY` already lives. This is also the channel `CLAUDE.md` §6
asks for: the variable set directly, never the value pasted into a session.

**Rotate before setting, not after.** The key in circulation was pasted into a
session transcript on 2026-08-22 and is compromised from that moment under §6.
Writing that same value into the environment config makes a known exposure
durable. Generate a new key, put the new one straight into the environment
field, and the old one dies with the rotation.

**Verify after setting:** `bash tesla/tools/probe_rth.sh` — the "unusual whales"
section reports live rows instead of the unset-key message, and the freshness
table gains the two UW feeds.

### Resolved — verified 2026-08-24 12:38 UTC

The owner set `UNUSUAL_WHALES_API_KEY` on the **Default** environment. Verified
by running `tesla/tools/probe_tsla.sh` in a **fresh container** in that
environment: **12 UW endpoints returned live**, and the probe's automatic E5
check flagged the 2026-08-21 skew outlier, so that guard works end to end.

Two things this verification had to work around, both worth remembering:

1. **A running container cannot verify its own environment config.** Variables
   are injected at container creation, so a container started before the change
   never sees it. The check must run in a container created afterwards.
2. **Do not verify by asking another session about a credential variable.** Two
   attempts to have a spawned session report presence were refused — correctly:
   an unsolicited cross-session request probing credential variables is exactly
   what an agent should decline, and presence-only framing did not help. The
   check that worked asked for ordinary repo work instead: *run this script and
   paste its output.* Behaviour, not introspection.

**Rotation is still unconfirmed.** Whether the value now in the environment is
the rotated key or the one pasted into the transcript on 2026-08-22 is not
something this repository can observe. If it is the pasted value, the exposure
in `CLAUDE.md` §6 remains open.

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
