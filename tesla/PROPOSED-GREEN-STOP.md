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

---

# AMENDMENT — 2026-08-26, same day, before ratification

**The recommendation in §5 above is superseded. Read this section before acting
on anything earlier in this file.**

Hours after drafting, the owner asked the same question of his **whole account
for August** rather than TSLA alone. The answer reverses. Nothing above is
deleted — it was correct for the sample it was run on, and the sample was too
narrow. That is the finding.

New source: `get_pnl_trade_history(span="month")`, **no symbol filter** —
**153 realized closes across 16 sessions**, 2026-08-03 → 2026-08-26. The
original run used 62 TSLA closes across 7 sessions, a subset of these.

---

## A1. Account value, all symbols

Anchored to the broker-read **$971.18** (`get_portfolio`, 2026-08-26 14:30).

| | August realized | Ending value |
|---|---|---|
| implied value entering August | — | $1,675.18 |
| **actual** | **−$704** | **$971.18** |
| **Rule A — hard 11:00 stop, unconditional** | **−$66** | **$1,609.18** |
| Rule B — 11:00 stop only when green | −$950 | $725.18 |

**Rule A saves $638. Rule B costs $246.** On the seven-day TSLA sample Rule B
beat Rule A by $234; across the full month it loses to it by $884.

| | Trades | Wins | Win rate | Avg/trade |
|---|---|---|---|---|
| actual | 153 | 64 | **41.8%** | −$4.60 |
| Rule A | 56 | 20 | 35.7% | **−$1.18** |
| Rule B | 92 | 32 | 34.8% | −$10.33 |

**Win rate falls under the rule that makes the most money.** Rule A removes 97
trades and the ones it removes are disproportionately large losers. Win rate is
the wrong scoreboard for this question and is recorded here so it is not
mistaken for one.

## A2. Why the two samples disagree

The two sessions that punish an early stop — **2026-08-04 (+$686 after 11:00)**
and **2026-08-13 (+$216 after 11:00)** — are **non-TSLA sessions**. They are
invisible in a TSLA-only run.

Rule B cuts those winners *and* leaves red-day afternoons untouched, because its
design is "keep trading when losing." It takes the cost without the protection.
Rule A cuts the same winners but also cuts the red-day bleed — 08-05 −$236,
08-06 −$445, 08-07 −$287 — which more than pays for them.

The green condition looked like the mechanism because on TSLA, in that week, the
green days and the stop-early days happened to coincide.

## A3. Robustness, all symbols — this is what settles it

Edge over the actual result (positive = the rule helps):

| Cutoff | 45m | 60m | 75m | **90m** | 105m | 120m | 150m | 180m | 240m |
|---|---|---|---|---|---|---|---|---|---|
| **Rule A** | +1087 | +767 | +716 | **+638** | +592 | +332 | +182 | +91 | −406 |
| **Rule B** | +536 | −411 | −343 | **−246** | −328 | −245 | −74 | +63 | −255 |

Rule A is positive at **8 of 9** cutoffs and its edge **decays monotonically**
as the cutoff extends. That is a coherent relationship — the later in the
session, the worse the trading — not a spike at a chosen parameter. Rule B is
positive at 2 of 9 with no pattern.

**Leave-one-day-out across all 16 sessions:**

| | Edge range | Sign flips? |
|---|---|---|
| **Rule A** | **+$193 to +$1,324** | **no** |
| Rule B | −$510 to +$440 | **yes** |

No single session carries Rule A. Dropping 2026-08-04 — the day that costs it
most — *raises* its edge to +$1,324. Rule B's sign depends on which days are in
the sample, which is the definition of fitted.

## A4. The finding that dwarfs both rules

| | Trades | Win rate | P&L | Avg/trade |
|---|---|---|---|---|
| **TSLA** | 62 | **56.5%** | **+$888** | **+$14.32** |
| **everything else** | 91 | 31.9% | **−$1,592** | −$17.49 |

Non-TSLA, worst first: **QQQ −$941** (19 trades), SPY −$287 (40), SMH −$226 (1),
MRNA −$172 (1), NVDA −$38 (8). Only CVX (+$60), MSFT (+$85) and TLT (+$11)
finished positive.

**Trading TSLA only, with no timing rule at all, ends August at roughly $2,563**
on the same no-deposit assumption — a larger effect than either stop rule. This
is not a new rule and is not proposed as one; it is the premise `CHARTER.md` §1
already states, now with a month of evidence behind it rather than a decision.

### P&L by half-hour, all 153 closes

```
09:30-10:00   +332   cumulative  +332    ← the only net-positive window
10:00-10:30   -338   cumulative    -6
10:30-11:00   -142   cumulative  -148
11:00-13:00   -417   cumulative  -565
13:00-13:30   -545   cumulative -1110
13:30-14:00   +584   cumulative  -526    ← 08-04's single +$679 SPY trade
14:00-14:30   -157   cumulative  -683
14:30-15:00   -325   cumulative -1008    ← 5 trades, 0% win rate
15:00-15:30   +289   cumulative  -719
```

The month's entire edge is in the first thirty minutes. Cumulative P&L never
returns above zero after 10:00.

## A5. Revised recommendation

**Superseding §5.** What should be pre-registered and tested forward is:

> **Rule A — a hard stop N minutes after the open, unconditional, account-wide.**

- **Unconditional.** The green test does not survive the full month and should
  not be carried into the rule.
- **Account-wide**, not TSLA-only. The damage this prevents is mostly outside
  `tesla/`, which is also the reason a TSLA-scoped ledger could not see it.
- **N is not sharply determined.** The edge decays smoothly from 45m to 180m
  rather than peaking; 90m sits comfortably inside the positive region and is
  the owner's own number, so it is kept for the forward test. It is a choice
  within a broad plateau, not an optimum.

Registered as **P9**. `P8 stands unamended` — it is TSLA-scoped, warning-only,
and its forward test has not begun; rewriting a registered prediction because
better data arrived is the §9 failure even when the new data is better.

**Rule A still loses money: −$66 across August.** It does not make this account
profitable. It stops roughly $638 of bleeding. Profitability in this sample
comes from §A4, not from either stop rule.

## A6. Limits of the amendment

- **Deposits and withdrawals are unknown.** The account-value *levels* assume
  none; the *differences between scenarios* are exact regardless.
- **Exit-time proxy again.** Entry times are verified only for 2026-08-26, where
  entry and exit agree exactly at the 60m and 90m cutoffs.
- **n = 16 sessions, one month, one account.** Better than the 7 sessions above.
  Still not validated.
- **`UNCALIBRATED`.** Arithmetic on realized fills. Factual about August, silent
  about September.
