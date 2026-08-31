# Ticket 1 — XLE shares  [LIVE]

**Written 2026-08-31, 09:22 ET. XLE $63.73 premarket (bid 63.70 / ask 63.79),
Friday close 62.68, +1.67%. Market not yet open. Outcome unknown at write time (§9).**

Account ••••4971: **$188.40 cash**, $205.03 total.

---

## Why shares and not options

At $188 a tradeable XLE 4DTE call is ~$120–140 — **64–74% of the account in one
contract.** CLAUDE.md §5 caps per-trade risk at 4% ($8); `SWING_STRATEGY.md` §7
gates live options at $1,500. No options position at this account size satisfies
either rule.

Shares satisfy both, carry no theta against a multi-day thesis, and let every
discipline mechanic in `SWING_STRATEGY.md` be practiced for real money at a size
where being wrong does not end the practice. **This ticket is a discipline rep,
not a money-maker — the dollars are small on purpose.**

## Thesis

US struck Iranian rocket launchers Sunday, reportedly preparing to mine the
Strait of Hormuz. WTI +3.1% (~$86). Energy is the only green sector into a red
tape: XLE +1.67%, USO +2.54%, CVX +2.08%, XOM +2.02% vs SPY −0.29%, QQQ −0.25%.
Friday's USO options flow was **95% call-sided** ($593k calls vs $31k puts, Sep
$138–140) — positioned *before* the weekend strikes, not chasing after.

## Levels (all pre-open, verified)

| Level | Value | Source |
|---|---|---|
| Friday high | **62.74** | brief §9 — the invalidation line |
| Friday close | 62.68 | official |
| Premarket | 63.73 | live 09:21 |
| Gamma call wall | **63.00** | UW, Fri close |
| Gamma flip | **63.51** | UW, Fri close |
| Magnet / put wall | 62.50 | UW, Fri close |
| Upside flip | 64.46 | UW nearby_flips |
| IV / rank / RV | 24.2% / 41.7 / 22.9% | UW |

XLE opens **above** its call wall (63.00) and flip (63.51). Gapping through a
call wall is the same mechanic that carried TSLA through 360 on 8/21 — **if it
holds.**

## Entry condition — must print; no condition, no trade

1. **No entry before 10:00 ET.** (`SWING_STRATEGY` §4 — the 8/25 evidence.)
2. **Do NOT buy the open.** XLE is already $1 through the brief's 62.74 trigger.
   Buying the gap is the behavior that has been punished.
3. **Entry is the retest:** a pullback into **63.00–63.51** that HOLDS —
   two consecutive 5-min closes above the pullback low, participation ≥0.40 of
   the 9:30–10:00 mean. Enter on the second close, not the touch.
4. If XLE never pulls back into that zone, **there is no trade today.** A
   setup that does not offer its entry is not a setup.

## Size

**2 shares** at the entry price (≈ $126–127 at 63.25). Leaves ~$61 cash.
Never more than 2 shares on this ticket regardless of conviction.

## Stop and invalidation

- **Resting stop-limit at 62.70**, placed in the same action as the entry
  (`SWING_STRATEGY` §5b; rule adopted 8/17). Below Friday's high 62.74 and
  below the round 63.
- Risk at a 63.25 entry: **$0.55/share × 2 = $1.10** (0.6% of account).
- **Never widen the stop. Never add. Never average down.**
- **Time invalidation:** if XLE is below 62.74 at noon, the gap has fully faded
  and the thesis is dead for today — out regardless of the stop
  (brief §9 whipsaw rule: the noon test wins).

## Management — the mechanics being practiced

Risk unit **R = $0.55/share**.

- **+1R (63.80):** move the stop to breakeven. This is the shares version of the
  give-back rule — *a trade that has been up 1R may not become a loser.*
- **+2R (64.35):** first target zone, just under the 64.46 upside flip. Sell
  1 share, let 1 run with the stop at breakeven.
- **Trail:** the remaining share exits on the first 5-min close below the prior
  candle's low.
- **30-minute rule:** if the position is red 30 minutes after entry and has not
  stopped out, **close it.** (16 trades in that bucket = 12% win rate = ~80% of
  all losses in this account.)
- **Overnight:** shares carry no theta, so an overnight hold is permitted **only**
  if the position is green and above 63.51 at 3:50 PM. Otherwise flat by the close.

## Session limits (SWING_STRATEGY §6)

Two losing trades ends the day · one position at a time · no direction flips ·
15-minute cooldown after any loss · max 2 entries.

## Pre-registered expectation (§9)

**I expect the entry condition not to print more often than it prints.** The
brief's own counter-case is strong and verified: every 2026 Hormuz headline has
been faded within days, and July's precedent was gap-then-fade. VIX at 15.4 says
the market does not believe this either.

- **If right:** XLE pulls back into 63.00–63.51 after 10:00, holds on two closes,
  and works toward 64.46 over today and tomorrow.
- **If wrong:** the gap fades straight through 62.74 without offering a retest,
  and the correct outcome is **no trade taken**.
- **The grade is the condition discipline, not the P&L.** Buying the open,
  buying without the two closes, or entering before 10:00 is a **C** even if it
  makes money.
