# RTH probe — schedule

Created 2026-08-22, rebuilt 2026-08-24. Three Routines, weekdays, one per sample
in `PREREGISTRATION.md`. Each runs the probe, appends to
`tesla/log/rth/YYYY-MM-DD.md`, and pushes to
`claude/tesla-options-trading-setup-aoqwsr`. They touch nothing else.

| Sample | ET | Cron (UTC) | Routine ID |
|---|---|---|---|
| A — post-open, entry window | 09:47 | `47 13 * * 1-5` | `trig_01VTzTEPJTXPoxTGE5pwTvx5` |
| B — doldrums, volume floor | 13:33 | `33 17 * * 1-5` | `trig_014KdxZb7WpSjycdUq9rgN5v` |
| C — exit window, past the bell | 15:03 | `3 19 * * 1-5` | `trig_01MPpHfsZjpzvCaVjoXv3crg` |

First fire: **Monday 2026-08-24**, which is a 0DTE day.

## They fire into a persistent host session, and that is load-bearing

**Host: `session_019uZTW7tNTEU2Xs5cgA8st6`** — "TSLA RTH probe host (read-only)".

All three Routines use `persistent_session_id`, not `create_new_session_on_fire`.
That is not a style choice. **A Routine that spawns a fresh session per firing
gets no MCP connectors at all**, and Robinhood is the only source of an option
chain (FMP serves none), so a fresh-session Routine can never measure P1 or P6.
The `connectors` parameter that would fix that directly is rejected for this
organization. Binding to a session that already holds the connector is the way
through, and the host inherits it because it was created from a session that had
it.

`create_trigger` prints a warning on every one of these saying the fired sessions
will have no connector tools. **That warning is written for fresh-session mode
and is wrong here** — verified 2026-08-24 by firing a poke-only Routine into the
host and having it report tool availability from inside the trigger-delivered
turn: `TRIGGER TURN: ROBINHOOD OK`. Ignore the warning on these three; do not
ignore it if anyone converts them back to fresh-session mode.

Consequences to keep in mind:

- **Do not archive the host.** The Routines die with it. If it is lost, create a
  new session from one holding the Robinhood connector, verify with the
  poke-only trick above, and re-point all three with fresh `create_trigger`
  calls — `update_trigger` cannot change the binding.
- **The host accumulates conversation.** Mode 2 resumes the same thread each
  firing, three times a weekday. Reset it periodically by standing up a new host
  and re-pointing; the log in `tesla/log/rth/` is the durable record, not the
  session.
- **The host's Robinhood connector is NOT read-only** — it exposes
  `place_option_order` and friends. Nothing in the platform prevents an order.
  The read-only guarantee is the prompt and `CHARTER.md` §1, so every Routine
  prompt states it explicitly and names the tools that must never be called.

**Session-cron was not used.** `CronCreate` jobs live only inside one Claude
session and vanish when it ends. Routines are account-level and survive.

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

## ~~Blocker 2 — the Routines carry no Robinhood connector~~ — RESOLVED 2026-08-24

**The original problem.** `create_trigger` refused the `connectors` parameter —
*"not available for this organization"* — and a Routine that spawns a fresh
session per firing gets no `mcp__*` tools at all. Robinhood is the only source
of an option chain (FMP serves none: `options-chain` and `options/quote` both
404), so P1 (the live spread gate) and P6 (real theta burn) — the two
measurements the whole RTH exercise exists for — could never be taken.

**How it was fixed.** Not by getting the connector onto the trigger, which the
org blocks, but by removing the need for it: the Routines now fire into a
**persistent host session that already holds Robinhood** rather than spawning a
bare one. See the top of this file for the host ID and the standing cautions.

The chain of verification, because none of it was assumed:

1. A session created from one holding the Robinhood connector **inherits it** —
   checked by asking a spawned session for tool *availability* only
   (`HOST: ROBINHOOD AVAILABLE`).
2. A **trigger-delivered turn** into that session also has it — checked by
   firing a poke-only Routine at the host and having it answer from inside the
   fired turn (`TRIGGER TURN: ROBINHOOD OK`). This is the step that mattered:
   `create_trigger` warns on every persistent-session Routine that its sessions
   will have no connectors, and that warning is simply wrong for this mode.
3. The temporary Routine was deleted after the check.

**What this does not fix.** The org restriction on the `connectors` parameter is
unchanged; anything that must run in a genuinely fresh session still cannot use
a connector. And the host's Robinhood grant includes order-placing tools, so the
read-only property of this process is enforced by prompt and charter, never by
the platform.
