# Ticket 4 — TSLA dip-and-reclaim, week of 9/1  [SHADOW — NOT TRADED]

**Written 2026-08-31, 14:35 ET, TSLA 367.58 (+5.89% from the open), session still
open, outcome unknown (§9). Supersedes Ticket 3, which was a continuation thesis —
the base-rate study below argues against continuation and for its opposite.**

Hypothetical account per `SWING_STRATEGY.md` §7. Real account $205 — TSLA cannot
be traded live at this size. See §Sizing, which is itself the finding.

---

## 1. The base-rate study (new evidence — this is why the ticket exists)

**Question asked before designing anything:** what does TSLA actually do after a
day like today? **Method:** every TSLA session since 2024-01-01 closing ≥ +5.0%
off its own open. **n = 30.**

| Measure | Result |
|---|---|
| Next-day close vs today's close | median **+0.24%** · positive **16/30 (53%)** |
| Next-day HIGH | median **+2.30%** (p25 +0.62%, p75 +5.15%) |
| Next-day LOW | median **−2.21%** (worst −12.08%) |
| Two days out | median +0.77% · positive 18/30 (60%) |

**A coin flip with a median move of a quarter of one percent.** Long premium
loses to theta on that outcome. Continuation, as a thesis, is not supported.

### 1a. The two splits that decide the trade

**Does the next-day open predict the day?**

| Next-day open | n | Close vs prior | **Open → close (what a day trader captures)** |
|---|---|---|---|
| Gap UP >+0.5% | 16 | median +1.93%, **75% up** | median **−0.55%, only 44% up** |
| Flat ±0.5% | 5 | median −1.38%, 20% up | median −1.25%, 20% up |
| Gap DOWN <−0.5% | 9 | median −2.60%, 33% up | median −0.33%, 44% up |

**The continuation is delivered overnight, in the gap — not during the session.**
A gap up looks bullish (75%) and is worthless to anyone buying at 9:30 (44%,
median −0.55%). This kills "buy the open tomorrow" outright.

**Does the size of today's move matter?**

| Today's move | n | Next close | Next open→close |
|---|---|---|---|
| **Moderate +5 to +7%** ← today is +5.89% | 20 | median **−0.51%**, 45% up | median **−1.27%**, **35% up** |
| Big +7%+ | 10 | median +0.61%, 70% up | median +0.35%, 50% up |

**Today lands in the worse bucket.** Moderate up-days are followed by a 35%
intraday win rate. Counter-intuitive and worth remembering: the *bigger* the
day, the better the follow-through.

### 1b. The one setup the data does support

Of the 30 cases, **17 dipped ≥2% below the prior close the next day.** From a
−2% entry:

| | |
|---|---|
| Bounce to that day's high | median **+2.66%**, mean +3.03% |
| Bounce ≥ +1.0% off entry | **14/17 (82%)** |
| Worst case (never bounced) | −1.57% |
| Two-day window | median +2.95% |

**82% for a ≥1% bounce is the only edge in the whole study.** But it comes with
a warning: the dip ran *past* −2% — median low **−2.70%**, 7/17 reached −4%,
2/17 reached −6% or worse. **A resting limit order at −2% gets run over roughly
half the time.** This is precisely why the entry below is a *confirmed reclaim*
and not a price.

---

## 2. Thesis

Not "TSLA continues." **"TSLA gives back part of an oil-driven spike, and the
giveback gets bought."** Driver is sourced: WTI ~$86 on the US–Iran strikes →
gasoline → EV substitution (headlines 10:48, 11:30, 12:30 today). Supporting
structure: net call premium **+$106.7M** today (vs +$65M on the 8/21 squeeze
day), call volume 2.2M = 1.6× the 30-day average, puts net sold, IV rank **17.1**
(cheap after a 6% day), gamma flip **357.83**, magnet **367.50**, put wall 350,
no call wall until 780.

**Convergence worth noting — three independent methods point at the same zone:**
the gamma flip (357.83), the base-rate median next-day low (−2.21% = **359.5**),
and the structural shelf from today's 09:50 consolidation. Entry zone **357.8–360.2.**

## 3. Entry — confirmed reclaim only

1. **No entry before 10:00 ET.** ISM Manufacturing + JOLTS print at 10:00 —
   skip the headline candle, read candles 2 and 3 (10:05, 10:10 closes).
2. **Never buy the open.** §1a: 44% / −0.55% after a gap up; 35% / −1.27% for a
   moderate prior day. This is the single most evidence-backed prohibition here.
3. **Wait for the dip into 357.80–360.20.** If it does not come, **there is no
   trade.** 13/30 historical cases never dipped −2% — a no-trade is the correct
   outcome 43% of the time.
4. **Enter on the reclaim, not the touch:** two consecutive 5-min closes back
   above the dip low, participation ≥ 0.40 of that day's 9:30–10:00 mean.
   The confirmation is what protects against the 7/17 cases that ran to −4%.
5. **Flow gate (veto):** net-call ticks flat-to-positive at entry.
6. **Catalyst gate — HARD:** check USO/XLE first. **If crude is red, this ticket
   is void** regardless of what TSLA does. The trade is the oil story; without
   oil there is no thesis.
7. **Structural veto:** a 5-min close below **357.83** before entry cancels the
   ticket for the day — that is the regime line, not a dip.

## 4. Instrument

**Expiry 2026-09-04** (4 DTE Tuesday, 3 DTE Wednesday). Chosen over 9/2 because
the median bounce plays out over one-to-two days and 9/2 leaves no room; **must
be closed before Thursday's close** — the 9/4 expiry sits on Friday's 8:30 jobs
report, which this thesis never signed up for.

**Strike chosen at entry by delta 0.45–0.60**, not fixed now. With entry near
359–360 that is likely the **357.5C or 360C**, not today's 365C — the ticket
follows the moneyness rule, not today's price. Today's marks for reference
(stale by tomorrow): 9/4 357.5C 13.65 × 13.80 · 360C 11.85 × 12.00 (OI 14,200,
the deepest book) · 365C 8.90 × 9.00. Weekly IV ~50% vs 30-day 41.6% — the
weekly already carries event premium; that is a cost, not a discount.

**Reject the trade if** the spread exceeds 2% of mid at entry, or if the flow
gate is adverse. **Do not substitute a cheaper OTM strike.**

## 5. Sizing — and the finding

```
R_underlying = entry − (confirmed dip low − 0.50)
R_option     = R_underlying × delta × 100
contracts    = floor( account × 0.04 / R_option )
```

Worked at entry 359.50, stop 356.50, delta 0.55:
`R_underlying $3.00 → R_option ≈ $165/contract.`

| Account | 4% risk budget | Contracts |
|---|---|---|
| $1,500 (§7 gate) | $60 | **0** |
| $3,000 | $120 | **0** |
| $5,000 | $200 | **1** |

**Recorded as a finding, not engineered around: TSLA at $367 with ~50% weekly IV
does not size for an account under ~$5,000 at a 4% risk limit.** The cheap-strike
"solution" is the far-OTM structure that has lost five-plus times in this account.

**Therefore the tradeable expression of this catalyst at a small account is not
TSLA.** It is **XLE at ~$63** — same oil driver, an underlying that sizes. That
conclusion is the most useful output of this ticket.

## 6. Exits

- **Target 1:** +1.0% from entry — take half. (82% of dip cases reached this.)
- **Target 2:** the base-rate median, **+2.66% from entry** — trail the rest on
  5-min closes, out on the first close below the prior candle's low.
- **Stop:** resting stop-limit at the confirmed dip low **−$0.50**, placed in the
  same action as entry. Never widened.
- **Give-back rule (HARD):** at +50% on premium, half off and the stop moves to
  entry, permanently.
- **30-minute rule:** red at 30 minutes and not stopped → close.
- **Time stop:** not working by Wednesday's open → exit. Closed before Thursday's
  close regardless.

## 7. Pre-registered expectation (§9)

**I expect no trade.** The dip must come (57%), the reclaim must confirm, oil
must stay bid, and the flow gate must hold — and today's +5.89% sits in the
weaker of the two historical buckets. A "no trade" outcome grades **A**.

**If the dip and reclaim do print, I expect a +1% bounce rather than a trend
day** — 82% hit +1%, only 35% of moderate-day cases closed green intraday. This
is a scalp with a good hit rate, not a swing.

**And I expect the sizing conclusion to hold:** that the right way to trade this
week's oil story with a small account is XLE, not TSLA. If TSLA runs another
$20 and XLE goes nowhere, that expectation was wrong and should be recorded as
such.

**Grading:** catalyst gate → entry discipline → the sizing conclusion → P&L, in
that order.

## 8. Status

`SHADOW — NOT TRADED.` Marked up at Tuesday's close whether or not it triggered.

## 9. What this study does not know

- n=30 is a small sample, drawn from one regime-heavy stretch (2024–2026)
  including the April 2025 tariff crash, which supplies both catastrophic
  outliers (−7.52%, −12.08%).
- Base rates describe a distribution, not tomorrow. The 82% figure is
  conditional on a dip that may not come.
- Today's +$106.7M call premium is unprecedented in this account's records and
  has **no historical counterpart in the study** — the sample is price-based
  only. Ticket 3's OI gate (09:30 roll) is still the live test of whether that
  flow was opened or rented, and a strong result there is an argument the base
  rate understates the case.
