# TSLA positioning into 2026-08-24 (Monday, a 0DTE day)

Written **pre-open, 09:10 ET**, before the session traded. Recorded per
`CLAUDE.md` §9 so today's outcome can be read against it rather than
reconstructed afterwards.

**Source of the book:** open interest as it settled Friday **2026-08-21**. OI is
T-1 by construction — this is exactly the right data for "positioning going into
today" and already one session stale the moment today trades.

**Everything here is `UNCALIBRATED`.** No TSLA read in this repository has been
graded against an outcome.

---

## 1. The book is call-heavy, and the headline P/C hides how much

| Expiry | DTE | Call OI | Put OI | Headline P/C | **In-band P/C** |
|---|---|---|---|---|---|
| 2026-08-24 | 0 | 47,024 | 21,724 | 0.46 | **0.27** |
| 2026-08-26 | 2 | 13,123 | 5,357 | 0.41 | **0.31** |
| 2026-08-28 | 4 | 89,261 | 70,053 | 0.78 | **0.25** |
| 2026-09-04 | 11 | 22,676 | 12,973 | 0.57 | **0.21** |

"In-band" = strikes within ±10% of spot (327–399).

**8/28 reads near-balanced at 0.78 and is not.** 76% of its put OI sits outside
the band: 9,992 contracts at strike 200, 6,502 at 150, 5,439 at 255, 4,687 at
280 — on a **four-day** expiry with spot at 362.86. Nobody buys a four-day
150-strike put on a $363 stock as a directional view. The Friday aggressor split
confirms it is structure: the 200P was **bought** (100% ask-side) while 150P
(20%), 230P (15%) and 280P (3%) were **sold**. That is spread/box construction
or margin machinery, not a bearish position.

**Reading the headline P/C as balanced-to-bearish would be a straightforward
error.** Strip the structural legs and the tradeable book is 0.21–0.31 P/C —
heavily call-side at every near expiry.

## 2. The calls sit below spot and are already in the money

0DTE call OI by strike: **360 → 8,956**, 350 → 6,848, 400 → 4,653,
342.5 → 2,383, 355 → 2,204, 370 → 2,083.

TSLA closed **362.86 after running +5.14% from 345.13** on Friday. Those
342.5–360 strikes were OTM while they were accumulated and the gap ran through
them. `days_of_oi_increases` shows **9 consecutive sessions** on the 0DTE 350C
and 355C, 8 on the 342.5C, 7 on 8/28's 360C.

So this is persistent multi-day call accumulation that is **now ITM**. Near
expiry that is realized profit sitting in the book — a source of supply as
holders take it or roll it, not evidence of fresh demand.

## 3. Friday's marginal flow was spreads, not conviction

| Contract | ΔOI | Ask-side | Read | days+ |
|---|---|---|---|---|
| 8/28 360C | +2,681 | 70% | **bought** | 7 |
| 8/28 350C | +3,146 | 46% | mixed | 6 |
| 8/24 360C | +1,921 | 58% | mixed | 5 |
| 8/28 355C | +1,115 | 17% | **sold** | 6 |
| 8/28 382.5C | +942 | 21% | **sold** | 1 |
| 8/24 355C | +882 | 36% | **sold** | 9 |
| 8/28 347.5C | +3 | 14% | **sold** | 2 |

Buying 360 while selling 382.5 above and 355/347.5 below is vertical
construction and overwriting. Someone is expressing **bounded** upside. This
materially caps the bullish reading of §1.

## 4. Dealer gamma: a cushion to ~342, an accelerant below it

Summing `greek-exposure/strike` (OI-based) over ±40 of spot: **net +452,932**.

Concentrations: 350 **+125,635** · 360 +68,773 · 345 +54,263 · 355 +52,192 ·
352.5 +47,886 · 357.5 +40,097.
Turns negative below ~342: 340 **−32,823** · 330 −24,974 · 335 −9,266.

Positive gamma 345–360 dampens moves inside that band. Below roughly 342 dealers
amplify instead.

## 5. Two signals disagree, and both are reported

- **`gamma_magnet` 362.5** — essentially at spot.
- **Max pain 340** (today), **332.5** (8/28), 340 (8/31) — 23 to 30 points below.

`options-expert/SKILL.md` Stage 1: a magnet and a max pain that agree is a
genuine pin read; when they disagree, say so rather than picking the one that
suits the thesis. **They disagree.** The only shared implication is that pin
pressure, to the extent it operates at all, points down rather than up.

## 6. The regime is contested — see `DATA_LAYER-TSLA.md` §7a

`gex-levels` gives opposite answers depending on the `source` parameter,
discovered today:

| source | gamma_flip | call_wall | regime at 362.86 |
|---|---|---|---|
| `oi` | 342.30 | 365.0 | above flip → **GLUE** |
| `vol` | 364.14 | 377.5 | below flip → **GASOLINE** |

`nearby_flips` (vol): 357.99, 360.58, 364.14, 372.20, 373.09 — four within $6 of
spot. **The flip is a band, not a line, and spot is sitting inside it.** For
gating purposes the regime is `NA_unresolved`; the conservative branch applies
(full retest confirmation demanded on any break).

## 7. What this cannot tell us

- **OI never reveals who is long.** The ask/bid split infers what the
  *initiator* did. It is evidence, not proof, and a bought call can be a closing
  trade.
- **Same-day volume swamps the standing book.** 341,016 calls traded on the 8/24
  expiry against 47,024 open. By mid-morning this description is weak.
- **Friday was OPEX.** The book was largely rebuilt; the 8/21 contracts are gone.
- **Deep-OTM put OI is structure, not view** (§1).
- Friday's +5.14% has **no confirmed driver** recorded here. A Nevada clearance
  for up to 5,000 autonomous vehicles crossed at 13:20 ET, which is
  time-consistent with the afternoon leg, but this is a **candidate, not an
  established cause** — `NO CLEAR DRIVER CONFIRMED`. Note also that a recall of
  **2,740,642 vehicles** crossed at 06:42 ET the same morning and the stock rose
  anyway: do not assume bad news sinks it.
- Several UW headlines in the feed are **auto-generated technical blurbs**
  ("Stochastics overbought", "MACD suggests possible stall"). They are not news
  and inform nothing here.

---

## 8. Summary

A call-heavy book whose calls are **already ITM** from Friday's gap, with
Friday's marginal flow structured as **spreads rather than outright longs**,
positive dealer gamma **cushioning 345–360**, pin signals pointing **lower**
while the magnet sits at spot, and a **regime read that is genuinely
unresolved** with spot inside the flip band.

That is a book positioned for *having been* right, not for more upside. It is a
description of where risk sits — **not a directional forecast**, and not a
trigger. Entries come from price action at mapped levels per
`playbook/PLAYBOOK.md`, with flow as a confirmation and veto layer only.
