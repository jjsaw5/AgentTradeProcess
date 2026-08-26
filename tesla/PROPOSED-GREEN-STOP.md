# PROPOSAL — the green stop

**STATUS: PENDING RATIFICATION. NOT IN FORCE.**
Drafted 2026-08-26 at the owner's request, after the owner named the same
failure for the third time in three sessions. Nothing in `tesla/` or
`.claude/skills/` enforces this until the owner ratifies it, at which point it
moves into `CHARTER.md` §3 and `/tsla-scan` Stage 0 and this file is deleted.

Evidence: `mcp__Robinhood__get_pnl_trade_history`, span=month, symbol=TSLA —
**62 realized closes across 7 trading sessions** (2026-08-14 → 2026-08-26).

---

## 0. What the owner proposed, in his words

> "I was up on the day multiple times and sit and continue to try and catch the
> next run which has me continuing to bleed money. I need to shut down trading
> on the day after that initial 90 minute window especially if I am plus on the
> day."

Two rules are entangled in that sentence. They were separated and tested
independently, because they do not perform the same.

- **Rule A** — a hard stop 90 minutes after the open, unconditional.
- **Rule B** — a stop 90 minutes after the open **only when green at that
  point**; otherwise the session continues under existing limits.

---

## 1. The result

| | Total, 7 sessions |
|---|---|
| **What actually happened** | **+$888** |
| Rule A — hard 90-minute stop | +$1,011 |
| **Rule B — 90-minute stop when green** | **+$1,245** |

**Rule B is worth +$357, a 40% improvement.** It is the largest effect any
candidate rule tested in this repository has produced.

### Per session, 90-minute cutoff (11:00 ET)

| Date | Closes | Actual | P&L at 11:00 | Rule B | Effect |
|---|---|---|---|---|---|
| 2026-08-14 | 2 | +89 | +89 | +89 | — |
| 2026-08-19 | 2 | +116 | +100 | +100 | −16 |
| 2026-08-20 | 4 | 0 | 0 | 0 | — |
| 2026-08-21 | 16 | +580 | +576 | +576 | −4 |
| **2026-08-24** | 21 | **+20** | +133 | **+133** | **+113** |
| 2026-08-25 | 7 | +117 | **−117** — red, keeps trading | +117 | — |
| **2026-08-26** | 10 | **−34** | +230 | **+230** | **+264** |
| **TOTAL** | **62** | **+888** | | **+1,245** | **+357** |

---

## 2. The 90 minutes is NOT what works. The green condition is.

This is the finding, and it is not what the proposal assumed.

**Rule A survives only at exactly 90 minutes.** Move the cutoff and it destroys
value at every other setting tested:

| Cutoff | 45m | 60m | 75m | **90m** | 105m | 120m | 135m | 150m | 180m | 210m | 240m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Rule A** | 737 | 532 | 778 | **1011** | 798 | 798 | 806 | 599 | 699 | 612 | 632 |
| **Rule B** | 1087 | 1015 | 1128 | **1245** | 1032 | 1032 | 1217 | 1088 | 1188 | 1024 | 973 |
| actual | 888 | 888 | 888 | 888 | 888 | 888 | 888 | 888 | 888 | 888 | 888 |

Rule A beats the actual result at **1 of 11** cutoffs. Rule B beats it at
**11 of 11**, across a range from 45 minutes to four hours.

A rule that works at one parameter value and nowhere else is fitted to the
sample. A rule that works across the whole parameter range is describing
something real about the process. **The clock is close to irrelevant; the
profit condition carries the entire effect.**

### Therefore the rule should be stated by its condition, not its clock

> **Once the session is green, the next trade's expected value is negative.**

That is the honest form of what the data shows. "Stop after 90 minutes" is a
convenient trigger for when that state usually arrives — it is not the
mechanism, and stating it as the rule invites the negotiation the rule exists
to prevent ("it's only 11:15").

---

## 3. Rule B (proposed)

> **When the session's realized P&L is positive at the 90-minute mark
> (11:00 ET), the trading day is over. No new opening trade for the rest of the
> session.**
>
> `/tsla-scan` reports it as a Stage 0 kill:
> `GREEN STOP — session +$xxx at 11:00, no further entries.`

### Deliberately one-sided

Rule B as measured also implies "if red at 11:00, keep trading." **That half is
NOT proposed and should not be read as endorsed.**

- It rests on **n = 1** (2026-08-25, −$117 at 11:00 → +$117 final).
- Structurally it is a rule granting permission to keep trading while losing,
  which is the shape that produces a catastrophic session. One observation
  cannot rule that out.

A red session therefore gains **nothing** from this proposal. It stays governed
by `CHARTER.md` §3/§3a and the §5a equity floor exactly as it is today.

### Carve-outs, deliberately narrow

- **Exits are never gated.** Stops, scales and invalidation exits work in every
  state. This gates opening trades only.
- **An open position at 11:00 is not force-closed.** It runs to its written
  invalidation or the 15:00 bell. The gate blocks *new* entries.
- **A scheduled catalyst** after 11:00 does not re-open the day. If the owner
  wants an exception it must be ratified separately; no discretionary override
  is built in, because a discretionary override is the behaviour being fixed.

---

## 4. What ratification would change

| File | Change |
|---|---|
| `tesla/CHARTER.md` §3 | add the green stop to the risk configuration, dated and attributed |
| `.claude/skills/tsla-scan/SKILL.md` Stage 0 | add the green stop as a kill |
| `.claude/skills/tsla-open/SKILL.md` | state the 11:00 mark in the session plan |
| `.claude/skills/tsla-watch/SKILL.md` §5 | announce the 11:00 mark alongside the 15:00 bell |
| `tesla/log/rth/PREREGISTRATION.md` | **P8**, so the gate is tested forward rather than assumed |

---

## 5. The honest case against ratifying today

- **n = 7 sessions**, and two of them (08-14, 08-20) contribute nothing. Five
  informative days.
- **The effect is concentrated in two sessions** — 08-24 (+113) and 08-26
  (+264) — which are the two sessions that prompted the analysis. That is the
  fitting failure `CLAUDE.md` §9 exists to prevent. The cutoff-robustness result
  in §2 is what distinguishes this from the range gate, but robustness across
  parameters is not the same as validation out of sample.
- **Realized P&L at a timestamp is not the same as "green."** Open positions are
  not marked in this measure. A session showing +$100 realized with an open
  −$200 position is not green in any meaningful sense, and the rule as written
  would stop it anyway. `/tsla-scan` must compute the mark-inclusive figure, not
  the realized one, if this is ratified.
- **It is a large behavioural change.** On 4 of 7 sessions it ends the day
  before noon.

**Recommendation: pre-register as P8 and run warning-only for five sessions
before it kills anything.** Same discipline applied to
`PROPOSED-RANGE-GATE.md`, and the only version of this that does not violate §9.

---

## 6. Method, so it can be re-run and disputed

Source: `get_pnl_trade_history(account_number, span="month", symbol="TSLA")`.
Timestamps are UTC and were converted at **UTC−4 (EDT)**. The 90-minute mark is
**11:00 ET**; minutes-since-open = `hour*60 + minute − 570`.

**Known limitation, measured rather than assumed.** The P&L feed timestamps
**closes**, not entries, while the rule gates **entries**. On 2026-08-26 both
are known from `get_option_orders`, so the proxy error was measured directly:

| Cutoff | By entry time | By exit time | Difference |
|---|---|---|---|
| 60m | +$127 | +$127 | **0** |
| 90m | +$230 | +$230 | **0** |
| 120m | +$201 | +$160 | +$41 |

At the cutoffs that matter the proxy is exact, because holds in the first two
hours are short. It degrades past 120 minutes. Prior sessions were not
entry-verified and this remains an unquantified assumption for them.

**Everything here is `UNCALIBRATED`.** It is arithmetic on realized fills —
factual about what happened, silent on whether trading this way works.
