# PROPOSAL — the range gate and the re-entry condition

**STATUS: PENDING RATIFICATION. NOT IN FORCE.**
Drafted 2026-08-24 at the owner's request. Nothing in `tesla/` or
`.claude/skills/` enforces this until the owner ratifies it, at which point it
moves into `CHARTER.md` §3 and `/tsla-scan` Stage 0 and this file is deleted.

Evidence: `tesla/log/2026-08-24-CHURN-ANALYSIS.md`. **One session, 24 entries.**

---

## Note on what was asked for versus what is proposed

The owner asked for a **re-entry cooldown**. I drafted one, tested it, and **it
fails**: a 15-minute cooldown after any close would have blocked the 10:20 entry
that became the day's +$270 trade. Elapsed time does not distinguish a good
re-entry from a bad one.

What the data does support is a gate on **where price is**, not **how recently
you traded**. That is proposed as Rule 1. A re-entry condition survives as
Rule 2, but reframed: it is conditional on a fresh trigger, not on a clock.

Ratify, amend, or reject either independently.

---

## Rule 1 — RANGE GATE (the one the evidence supports)

> **No opening trade while spot sits in the middle third of the session range.**
>
> At entry, compute `pos = (spot − session_low) / (session_high − session_low)`
> using the high and low established **so far today**. If `0.333 ≤ pos ≤ 0.667`,
> the trade is killed. `/tsla-scan` reports it as a Stage 2 kill:
> `MID-RANGE — pos xx%, no entry`.

**Backtest, 2026-08-24:** 9 of 24 entries fell in the middle third and produced
**−$415**. The other 15 produced **+$435**. Every large winner was at an
extreme: +170 at 6% of range, +270 at 24%, +422 at **0%**.

**Why this and not a trade cap or a cooldown:** it is the only tested rule that
separates the winners from the churn without cutting a winner. Caps and
cooldowns both cut winners (see the analysis, §4).

**This is not a new rule.** `playbook/PLAYBOOK.md` §1b already says *"Don't
initiate mid-range… never in the middle where odds are worst in both
directions."* Rule 1 makes an existing principle **mechanically checkable** so
`/tsla-scan` can enforce it instead of relying on judgement in the moment.

### Carve-outs, deliberately narrow

- **The first 15 minutes** (09:30–09:45) are exempt: the range is too young for
  the ratio to mean anything, and `/tsla-scan` Stage 0 already blocks entries
  before ~09:45 for the same reason.
- **A scheduled catalyst** re-opens the tape and can legitimately break a
  mid-range chop. If an event lands within the previous 10 minutes, the gate
  becomes a warning rather than a kill — and the card must name the event.
- **Exits are never gated.** Stops, scales and invalidation exits always work,
  in any range position. This gates opening trades only.

## Rule 2 — RE-ENTRY CONDITION (reframed from a cooldown)

> **After closing a TSLA position, a new position requires a fresh trigger — a
> 5-minute CLOSE through a mapped level, timestamped after the previous exit.**
>
> Re-entering on the *same* trigger that justified the closed trade is not a new
> trade. It is the same idea, and it needs a new reason, not a new fill.

**No time component.** Four minutes is fine if a new 5-min close through a level
happened in between; forty minutes is not fine if nothing did. Today's
18-second, 57-second and 69-second round trips all fail this test, because no
new 5-min bar even closed between the exit and the re-entry.

## Rule 3 — the daily churn tripwire (softest, and only a warning)

> **At the 6th opening trade of the session, `/tsla-scan` prints a warning
> naming the day's trade count, realized P&L, and win rate so far.** It does not
> block.

Not a limit, because the cap test showed no reliable threshold. It exists so the
count is *visible* at the moment it matters. `playbook` §0: *"Selective
participation is the retail edge. Most days need 0–2 trades."* Today ran 24
opening trades.

---

## What ratification would change

| File | Change |
|---|---|
| `tesla/CHARTER.md` §3 | add Rules 1–3 to the risk configuration, dated and attributed |
| `.claude/skills/tsla-scan/SKILL.md` Stage 0 | add the range gate as a kill, the re-entry condition as a kill, the churn tripwire as a warning |
| `.claude/skills/tsla-scan/SKILL.md` Stage 2 | reference the computed `pos` rather than the prose "mid-range" |
| `.claude/skills/tsla-open/SKILL.md` | print the range gate's thresholds once the opening range is known |
| `tesla/log/rth/PREREGISTRATION.md` | a new prediction P7, so the gate is tested forward rather than assumed |

## The honest case against ratifying today

- **n = 9** mid-third entries. One unlucky day moves the result materially.
- The rule is **fitted to a single session** — the exact failure mode `CLAUDE.md`
  §9 exists to prevent. It should be **pre-registered and tested forward**, not
  adopted because it explains yesterday.
- Session range is **path-dependent**: it widens through the day, so the same
  price can be mid-range at noon and edge-of-range at 15:00. That is arguably
  correct behaviour, but it is not obviously so.
- A gate that blocks 9 of 24 entries is a **large** behavioural change to adopt
  from one day of evidence.

**Recommendation: pre-register it as P7 and run it in warning-only mode for five
sessions before it kills anything.** That gets the discipline of the rule and the
evidence for it at the same time, and it is the only version of this proposal
that does not violate §9.
