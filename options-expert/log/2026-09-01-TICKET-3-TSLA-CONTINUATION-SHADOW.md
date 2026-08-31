# Ticket 3 — TSLA continuation  [SHADOW — NOT TRADED]

**Written 2026-08-31, 14:30 ET, with TSLA at 367.6 — the session still open and
tomorrow's outcome unknown (§9). Gated on a test that resolves at 09:30 tomorrow.**

**Hypothetical account: $1,500** (`SWING_STRATEGY.md` §7 gate). Real account
$205 — TSLA shares ($367) exceed the whole account and any TSLA option breaks
every sizing rule, so **this cannot be live**. It is a calibration ticket.

---

## What happened today (facts, 09:30–14:25)

TSLA **open 347.13 → 367.58, +5.89%**, high 368.52 at 13:55, low 347.13 at the open.

**Driver — sourced, not inferred.** Oil at ~$86 on the US–Iran strikes →
gasoline prices → EV substitution. Three headlines say it directly: 10:48
*"Tesla Jumps 4% as Oil Climbs to $86: Is the Gas-Price Trade Back?"*; 11:30
*"Why Tesla Stock Stepped on the Gas Monday Morning"*; 12:30 *"TSLA Hits Gas in
EVs."* Same catalyst as the XLE ticket, different transmission channel.

**Flow — the strongest reading measured in this account's history:**

| | Today | Comparison |
|---|---|---|
| Net call premium | **+$106.7M** | 8/21 OPEX squeeze +$65M · 8/25 +$1.6M |
| Net put premium | −$15.9M (sold) | |
| Call volume | 2,200,336 | 30-day avg 1,384,797 = **1.6×** |
| Bull vs bear premium | $626M vs $503M | |
| IV / rank / RV | 41.6% / **17.1** / 39.9% | vol still cheap after a 6% day |

Buying clustered 09:45–09:48, then 10:17 (+$5.13M), 10:35, 11:50. Today's
busiest strike is **365 (378k calls, $105.2M)**, then 360 and 362.5.

**Tape — the contradiction.** The entire move finished by 09:50 (347→360.40 on
participation 1.22 / 1.34 / 1.21). Since 11:00 participation has run
**0.55, 0.45, 0.49, 0.36, 0.33, 0.27 … 0.24, 0.26, 0.23, 0.32** — three hours
mostly *below* the 0.40 floor. The last $7 came on air.

**Structure.** Gamma flip **357.83** (price well above = dampening), magnet
**367.50**, put wall 350, no call wall until 780. Price has oscillated 363–368.5
since 11:50 because **it is sitting on the magnet.** Magnets pin; they do not propel.

---

## The gate — this ticket does not exist until the OI roll answers

**At ~09:30 Tuesday, pull `oi-change` for TSLA.** The window rolls to
08-31 → 09-01 and reveals whether today's $106.7M of call buying was **opened and
held** or **day-traded and closed**. This is the same T+1 test that confirmed the
held-overnight positions on 8/21 and exposed the stale-window error the same day.

| Result | Meaning | Action |
|---|---|---|
| Material OI **growth** at 360/365/370 (9/4 or later), ask-side lean | Real positioning; continuation thesis alive | Proceed to §Entry |
| OI **flat or lower** despite 2.2M call volume | Today was a rental, not a position | **No trade. Ticket dead.** |
| Mixed | Treat as flat | **No trade.** |

Re-pull `gex-levels` at the same time and treat any read before ~10:30 as
provisional (8/25 evidence: TSLA's wall read 387.5 then 352.5 within 19 minutes).

## Entry condition — must print; no condition, no trade

1. **No entry before 10:00 ET.**
2. **Do not buy the open**, and do not chase a gap up. Today's move is already
   made; buying strength on day two after a +5.9% day is the "stack top" error
   logged on 8/13 and repeated on 8/19.
3. **Preferred entry — the flip retest (A-grade):** pullback toward
   **357.83–360.00**, two consecutive 5-min closes back above the pullback low,
   participation ≥ 0.40. Cheapest entry, tightest stop, and the flip is the line
   that defines the regime.
4. **Alternative — magnet hold (B-grade):** two consecutive 5-min closes above
   **367.50** with **participation ≥ 0.40 returning**. Volume is the missing
   ingredient today; without it this alternative does not qualify.
5. **Flow gate (veto):** net-call ticks flat-to-positive at entry. Persistent
   negative ticks stand the trade down whatever price does.
6. Neither condition prints → **no trade**, and that is the correct outcome.

## Instrument

**TSLA 2026-09-04 365C** (4 DTE Tuesday). Priced today 14:28: **8.90 × 9.00**,
volume 18,194, OI 5,788, IV 50%.

Delta ≈ 0.55 — inside the §3 band. Chosen over 370C/375C deliberately: today's
$105.2M of call premium concentrated at the 365 strike, and slightly-ITM is the
moneyness the 8/19 evidence supports. **Do not substitute a cheaper OTM strike.**

Re-price at entry — this quote will be stale by tomorrow, and IV at 50% on the
weekly (vs 41.6% 30-day) is already carrying event premium.

## Size (hypothetical $1,500)

```
R_underlying = entry − stop_level
R_option     = R_underlying × 0.55 × 100
contracts    = floor( 1500 × 0.04 / R_option )
```

Worked for the flip-retest entry at 360, stop 357.00:
`R_underlying 3.00 → R_option ≈ $165 → 60/165 = 0 contracts.`

**At $1,500 this trade does not size.** One contract of the 365C is ~$900 —
60% of the hypothetical account — and its stop distance alone exceeds the 4%
risk limit. **Recorded as a finding, not worked around:** TSLA at $367 with 50%
IV is too large an underlying for a $1,500 account under these rules. The
honest options expression of this thesis needs either a much larger account or a
defined-risk spread (Level 3, unavailable).

**A cheaper strike is not the fix** — that is the far-OTM structure that has lost
five-plus times. The correct conclusion is that **this thesis is not tradeable
as a long call at this account size**, and saying so is the point of a shadow
ticket.

## Invalidation (written before entry)

- **Price:** 5-min close below **357.83** — the gamma flip. Below it the regime
  turns amplifying and a +5.9% day unwinds fast. Out, no renegotiation.
- **Time:** if the thesis has not begun working by **Wednesday's open**, exit.
  4 DTE buys one overnight, not three (`SWING_STRATEGY` §5c).
- **Catalyst death:** if crude gives back the Iran gap, the EV-substitution
  thesis dies with it. Check USO/XLE before any entry — **if oil is red, this
  ticket is void** regardless of what TSLA does.
- **Hard exit before Thursday's close** — the 9/4 expiry sits on Friday's jobs
  report. This is an oil-substitution trade, not a payrolls bet.
- **30-minute rule**, **give-back rule at +50%**, resting stop at entry, all per
  `SWING_STRATEGY` §5–§6.

## Event risk tomorrow

**10:00 AM — ISM Manufacturing (est 55.2) + JOLTS (est 7.3M)**, both ⚠️ per the
brief. This lands *inside* the entry window. §2 protocol: never trade the
headline candle; read candles 2 and 3 (10:05, 10:10 closes).

## Pre-registered expectation (§9)

**I expect the OI gate to fail.** Reasoning stated before the result: 2.2M call
contracts traded on a day whose entire price move finished in twenty minutes,
followed by three hours below the participation floor, is the signature of
intraday rental rather than accumulation. If OI at 360/365/370 does not grow
materially overnight, that is the tell.

**I also expect this thesis to be right in direction and untradeable in
practice** — TSLA is simply too large an underlying for the sizing rules, and I
want that recorded before we find out, because if it proves true it is an
argument for trading the *catalyst* through a cheaper vehicle (XLE at $63) rather
than the highest-profile name expressing it.

- **If the gate passes and the flip retest prints:** the map is open — no call
  wall until 780, price above the flip, vol rank 17.1 still cheap.
- **If the gate fails:** no trade, ticket closed, and today's +$106.7M is logged
  as an example of large flow that did not translate.
- **Grading:** the gate decision first, then condition discipline, then the
  counterfactual P&L. A "no trade" outcome that follows the gate is an **A**.

## Status

`SHADOW — NOT TRADED. Gated on the 09:30 OI roll, 2026-09-01.`
