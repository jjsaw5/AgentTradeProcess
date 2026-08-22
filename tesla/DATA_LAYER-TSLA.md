# TSLA Data Layer — verified inventory

What the three connections deliver **for TSLA specifically**, verified by probe.
`options-expert/DATA_LAYER.md` remains the general inventory and is not
superseded; this file records what is different, what is measured, and what is
currently unavailable. **If a capability is not listed here as verified for
TSLA, this module may not assume it exists.**

**Verified:** 2026-08-22, ~20:10 UTC (Robinhood + FMP) and ~20:40 UTC
(Unusual Whales, added later the same session) — **Saturday, market CLOSED.**
FMP `exchange-market-hours?exchange=NASDAQ` returned `isMarketOpen: false`.

**What that means for every number below:** all quote-derived figures are the
**2026-08-21 16:00 ET closing snapshot** (`updated_at
2026-08-21T19:59:59Z`), not live readings. Closing spreads are systematically
wider than intraday spreads. Every liquidity figure here therefore carries a
standing caveat and **must be re-probed during regular trading hours before any
threshold derived from it is trusted.**

**Re-verify with:** `tesla/tools/probe_tsla.sh` (FMP + UW), and the Robinhood
MCP calls listed in §2.

---

## 0. Connection status

| Source | Status | Role for TSLA |
|---|---|---|
| **Robinhood** (MCP) | ✅ working, read-only | the contract layer — chain, strikes, greeks, IV, OI, marks, account |
| **FMP** (`stable/*`) | ✅ working, key present | the context layer — bars, quotes, daily OHLC, calendars, earnings |
| **Unusual Whales** | ✅ working, key added 2026-08-22 | the edge layer — dealer gamma, signed flow, tide, IV rank |

**All three legs are connected.** UW was added mid-session; §7 is its
TSLA-specific inventory. 20 of 20 probed endpoints returned `200` with data.

**Rate limits are not a constraint.** UW returns them as response headers —
there is no usage endpoint (`/api-usage` 404s; the vendored
`options-expert/reference/uw-api-usage-skill.md` reads `x-uw-*` headers off any
response, which is the correct method). Measured 2026-08-22:

```
x-uw-daily-req-count: 67          x-uw-req-per-minute-remaining: 1000000
x-uw-token-req-limit: 100000000   x-uw-req-per-minute-reset: 60000
```

A fan-out scan on one ticker is nowhere near any ceiling. This closes the
"rate limits unmeasured" gap carried in `options-expert/DATA_LAYER.md` §5.

---

## 1. The chain — the findings that shape the whole process

Source: Robinhood `get_option_chains(underlying_symbol="TSLA")`, 2026-08-22.

```
chain_id                     9ee49197-7b3c-46c2-8d83-5d5ad1ed9eaa
trade_value_multiplier       100
settle_on_open               false          (PM settled)
extended_hours_state         disabled       (no extended-hours options trading)
late_close_state             disabled
sellout_time_to_expiration   1800 seconds   -> 15:30 ET force-close
min_ticks                    below $3.00: $0.01  |  at/above $3.00: $0.05
```

### 1a. Expirations: Monday / Wednesday / Friday — **not daily**

```
2026-08-24, 08-26, 08-28, 08-31, 09-02, 09-04,
09-11, 09-18, 09-25, 10-02, 10-16, 11-20, 12-18, 2027-01-15 ... 2028-12-15
```

The near-dated cycle is Mon/Wed/Fri; from 09-11 onward it is weekly (Fridays).
The DTE map this produces is in CHARTER §2 and is the first thing `/tsla-open`
reports. **Re-read the chain each session** — holidays move it.

### 1b. Force-close at 15:30 ET, confirmed per contract

`get_option_instruments` on the 2026-08-24 expiry returns
`sellout_datetime: "2026-08-24T19:30:00+00:00"` on every contract = **15:30 ET**.
This is the broker acting, not a warning. CHARTER §2a sets the decision bell at
15:00 and the hard exit at 15:25 as a result.

### 1c. Strike spacing is $2.50 near the money

Verified present: 355.0, 365.0, 372.5. TSLA strikes step $2.50 in the near-money
band, against SPY's $1.00. Consequences:

- Roughly 2.5× fewer strikes to choose from, so a delta target of 0.30–0.60 maps
  to **one or two strikes**, not five. Strike selection is coarse; do not model
  it as continuous.
- Vertical spread widths come in $2.50 increments.

### 1d. Tick size interacts with the stop buffer

`min_ticks.above_tick = 0.05` for contracts at or above $3.00. The playbook's
15-cent stop-limit buffer is therefore **exactly 3 ticks** on a $3+ TSLA
contract — coherent, and the buffer transfers. Below $3.00 the tick is $0.01 and
15 cents is 15 ticks, which is loose enough to give away real money on a fill.
**Use a tick-aware buffer: 3 ticks, whichever regime the contract is in.**

---

## 2. Contract snapshot — 2026-08-24 expiry, spot 362.86

Robinhood `get_option_quotes`, `updated_at 2026-08-21T19:59:59Z`
(**closing snapshot, market shut**). Greeks are `source: robinhood` — vendor
supplied, not modeled by us.

| Contract | bid | ask | mark | spread % | Δ | Γ | Θ | Θ %/day | IV | OI | volume |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 355 C | 8.80 | 10.25 | 9.525 | **15.2%** | 0.766 | 0.027 | −0.901 | −9.5% | 0.423 | 2,204 | 25,143 |
| 355 P | 1.23 | 1.29 | 1.260 | 4.8% | −0.213 | 0.028 | −0.741 | **−58.8%** | 0.383 | 138 | 25,351 |
| 365 C | 3.05 | 3.20 | 3.125 | 4.8% | 0.426 | 0.039 | −1.017 | **−32.6%** | 0.380 | 1,062 | 41,489 |
| 365 P | 5.10 | 5.45 | 5.275 | **6.6%** | −0.572 | 0.038 | −1.007 | −19.1% | 0.389 | 63 | 22,541 |
| 372.5 C | 1.06 | 1.13 | 1.095 | **6.4%** | 0.191 | 0.026 | −0.731 | **−66.8%** | 0.395 | 805 | 10,569 |
| 372.5 P | 10.25 | 11.55 | 10.900 | **11.9%** | −0.790 | 0.025 | −0.805 | −7.4% | 0.429 | 26 | 708 |

Bolded figures fail or nearly fail a gate.

### 2a. Three things this table establishes

**1. The 5% spread gate is near-binding on TSLA, not generous.**
At the close only **two of six** near-money contracts passed it (355P and 365C,
both at 4.8%). ITM strikes were 11–15% wide. SPY near-money runs ~0.6%, so a
threshold that never bites on SPY is the *primary* kill reason on TSLA.
**Caveat: these are closing spreads.** Intraday spreads on 41,000-volume
contracts are materially tighter. Re-probe during RTH before concluding the gate
is too tight or too loose — do not adjust it off this snapshot.

**2. Theta is severe and asymmetric across the strike ladder.**
The ATM 365C bleeds **32.6% of its mark per day**; the 372.5C bleeds **66.8%**.
`options-expert/SKILL.md` Stage 4 records SPY 1DTE at ~55%/day as brutal — TSLA
OTM at 2DTE is worse. A TSLA 0DTE thesis that needs two hours to be right is
losing money the whole time it is being right.

**3. Volume runs far above open interest on the near-dated chain.**
365C: volume 41,489 against OI 1,062. 365P: 22,541 against OI 63. Same-day
positioning dominates; **yesterday's OI describes almost nothing about today's
book.** Any OI-based reasoning on this chain is close to meaningless, and the
`< 250 OI` liquidity gate would have rejected the 365P (OI 63) despite 22,541
contracts trading. **The OI gate does not transfer to TSLA near-dated
contracts.** Use same-day volume as the liquidity test; treat OI as context.

---

## 3. Account — read live, 2026-08-22

Robinhood `get_accounts` + `get_portfolio`.

| Field | Value |
|---|---|
| Sizing account | `••••4971` — individual, **margin** |
| Option level | **`option_level_3`** — verticals and calendars permitted |
| Total value | **$1,269.86** |
| Cash / buying power | **$1,252.65** |
| Equity positions | $17.21 |
| Options positions | $0.00 |

`option_level_3` matters: debit verticals are available as a structure, which is
the only way to cap loss below one contract's premium on a name this expensive.
The Roth and the agentic-enabled cash account are both level 2 and are **not**
the sizing account.

**Never hardcode any of the above.** Re-read on every run. These figures are a
snapshot for calibration, not a stored value.

---

## 4. Underlying behaviour — FMP, 10 sessions

`historical-price-eod/full?symbol=TSLA`, 2026-08-06 → 2026-08-21.

| Date | Open | High | Low | Close | Range | Range % |
|---|---|---|---|---|---|---|
| 2026-08-21 | 349.88 | 366.50 | 346.90 | 362.86 | 19.60 | 5.40% |
| 2026-08-20 | 346.20 | 347.50 | 338.96 | 345.13 | 8.54 | 2.47% |
| 2026-08-19 | 338.89 | 351.62 | 335.70 | 351.12 | 15.92 | 4.53% |
| 2026-08-18 | 333.22 | 340.53 | 331.12 | 336.87 | 9.41 | 2.79% |
| 2026-08-17 | 340.69 | 345.45 | 337.48 | 339.30 | 7.97 | 2.35% |
| 2026-08-14 | 342.33 | 351.26 | 335.33 | 342.27 | 15.93 | 4.65% |
| 2026-08-13 | 327.20 | 341.64 | 325.24 | 339.96 | 16.40 | 4.82% |
| 2026-08-12 | 335.00 | 335.50 | 323.64 | 327.51 | 11.86 | 3.62% |
| 2026-08-11 | 332.80 | 336.20 | 329.53 | 332.81 | 6.67 | 2.00% |
| 2026-08-10 | 326.60 | 332.05 | 326.15 | 330.88 | 5.90 | 1.78% |

**Mean daily range: $11.82 = 3.26% of spot.** Range spanned $5.90 to $19.60 —
a **3.3× spread** across ten sessions.

Why this is the number that governs stop placement: a stop must sit outside
normal movement. At Δ 0.426, $3 of TSLA ≈ $1.29 of option ≈ $129 of risk per
contract, which is CHARTER §3d's operative trade. A stop tighter than roughly
$2 of TSLA is inside the noise on most sessions and inside a single 5-minute bar
on the busy ones.

**FMP `quote?symbol=TSLA`** confirmed working: price, day H/L, year H/L,
50/200-day averages, volume, previous close, timestamp. This feeds PDH/PDL/PDC.
50-day avg 365.86, 200-day avg 403.32, year range 297.38–498.83 at last close.

### 4a. Earnings — the E4 gate is dormant until late October

FMP `earnings?symbol=TSLA`:

- **Next: 2026-10-28** (est. EPS 0.47, est. revenue $27.66B).
- Last: 2026-07-22 (actual 0.33 vs 0.50 est. — a miss; revenue beat).

2026-10-28 is far outside any 0–5DTE window from today. **Edge test E4
(event-in-life) does not apply to earnings** and re-arms in the week of
2026-10-19, when a 5DTE contract first spans the print. Scheduled macro events
still apply every day and are `/tsla-open`'s job.

---

## 5. Volume calibration — measured, provisional

FMP `historical-chart/5min?symbol=TSLA`, 780 bars over 10 sessions
(2026-08-10 → 2026-08-21).

| Window | n | median | p25 | p10 | mean |
|---|---|---|---|---|---|
| All 5-min bars | 780 | **237,484** | 160,245 | 110,708 | 299,809 |
| 09:30–10:00 | 60 | 547,392 | 172,701 | 114,487 | 485,361 |
| 13:00–14:30 (doldrums) | 180 | 175,324 | 126,278 | 97,033 | 193,506 |

Per-session opening-30-minute mean ranged **181,359 (08-14) to 760,310
(08-19)** — a 4.2× spread. Median opening 5-min bar: 126,714.

### 5a. Two consequences

**The playbook's portable form does not work well on TSLA.** Its "dead tape ≈
bar volume under ~40% of that day's 9:30–10:00 average" gives a floor ranging
from **72,544 to 304,124** depending on the day — a 4× swing in the threshold
itself. On 2026-08-14 the opening half hour was quieter than the session that
followed, so the anchor pointed the wrong way.

**Provisional TSLA volume floor** — derived by applying the same
floor-to-session-median ratio the playbook used on SPY (~0.77):

```
No new entry when the last two completed 5-min bars are both under ~185,000.
Re-arm after a bar prints back above ~237,000 (the pooled session median).
```

**Status: measured from price data, NOT validated by trading.** It is arithmetic
on ten sessions, not evidence that trading on it works. It is `UNCALIBRATED` and
must be revisited once `tesla/log/` holds graded sessions.

**Feed caveat:** these are **FMP** bar volumes. The playbook's SPY/QQQ numbers
are **Robinhood** chart-feed units, which undercount the consolidated tape. The
two are not comparable, and this floor may only be applied to FMP 5-min bars.

---

## 6. What is unavailable, and the honest consequence

| Gap | Consequence | Fix |
|---|---|---|
| **`historical-risk-reversal-skew` printed an anomaly on 2026-08-21** | E5's level is untrustworthy on that date — see §7f. Trajectory only, and verify before use. | Confirm against a second session before reading any level |
| `volatility/realized` returns `realized_volatility: null` for recent TSLA rows | The paired IV/RV series is unusable at the short end | Take IV-vs-RV from `volatility/stats`, which does carry `rv` |
| `variance-risk-premium` lags ~28 days on TSLA | Never a live reading — a statement about the recent regime | Use `volatility/stats` for today |
| No intraday VWAP from any vendor | Must be computed from FMP bars and labelled as ours | Compute, label |
| Liquidity figures are a **closing** snapshot | Spread gate untested against live intraday quotes | Re-probe during RTH; §2 caveat stands until then |
| OI gate does not transfer | Near-dated TSLA OI is tiny against same-day volume | Use volume as the liquidity test |
| Volume floor unvalidated | A threshold measured, not proven | `tesla/log/` |
| TSLA GEX is measurable but its *behaviour* is unproven here | `gex-levels` works; no TSLA regime read in this repository has ever been checked against an outcome | Log the read and the outcome, every session |

---

## 7. Unusual Whales — TSLA inventory, verified 2026-08-22

Base `https://api.unusualwhales.com`. **Both** headers required on every call:
`Authorization: Bearer $UNUSUAL_WHALES_API_KEY` and `UW-CLIENT-API-ID: 100001`.
All GET. No `apiKey=` query parameter exists.

The key reaches code through the environment only, from the gitignored `.env`
(`CLAUDE.md` §6). `.env.example` documents the variable names.

**Read `options-expert/reference/README.md` before trusting the vendored
`uw-api-skill.md`.** Its "if a URL is not on this list it does not exist" line
is an anti-hallucination guardrail, not an inventory — it covers 26 endpoints
against the API's 207. Six of the endpoints this module depends on
(`gex-levels`, `volatility/stats`, `iv-rank`, `term-structure`, `max-pain`,
`historical-risk-reversal-skew`) are absent from that whitelist and all work.
The authority is `GET /api/openapi`.

**20 of 20 probed endpoints returned 200 with data for TSLA:**

| Purpose | Endpoint | Rows | Note |
|---|---|---|---|
| Regime | `/stock/TSLA/gex-levels` | obj | the regime read — one call |
| Regime | `/stock/TSLA/max-pain` | 23 | per expiry |
| Regime | `/stock/TSLA/spot-exposures/strike?limit=500` | 202 | live, timestamped |
| E1 | `/stock/TSLA/volatility/stats` | obj | `iv`, `rv`, `iv_rank` together |
| E1 | `/stock/TSLA/iv-rank` | 5 | daily `iv_rank_1y` series |
| E1 | `/stock/TSLA/interpolated-iv` | 9 | per horizon — **field is `days`** |
| E1 | `/stock/TSLA/volatility/term-structure` | 23 | **per real expiry** — prefer this |
| E1 | `/stock/TSLA/volatility/variance-risk-premium` | 231 | ~28-day lag, see §7e |
| E2 | `/stock/TSLA/net-prem-ticks` | 391 | per-minute, carries `net_delta` |
| E2 | `/stock/TSLA/options-volume` | 1 | daily aggregate + 3/7/30d averages |
| E2 | `/option-trades/flow-alerts?ticker_symbol=TSLA` | 20 | aggregated unusual activity |
| E2 | `/screener/option-contracts?ticker_symbol=TSLA` | 20 | per-contract, widest net |
| E2 | `/stock/TSLA/flow-recent` | 50 | recent tape |
| E5 | `/stock/TSLA/historical-risk-reversal-skew` | 250 | **anomaly present — §7f** |
| Env | `/market/market-tide` | 81 | 5-min market-wide bars |
| Ctx | `/news/headlines?ticker=TSLA` | 5 | `sentiment`, `is_major` |
| Ctx | `/stock/TSLA/ohlc/5m` | 2,500 | UW does have intraday bars |
| Ctx | `/darkpool/TSLA` | 500 | prints with NBBO at execution |
| Ctx | `/stock/TSLA/greek-flow` | 391 | greek flow through the session |
| Ctx | `/stock/TSLA/oi-change` | 50 | per-contract OI change |

All readings below are the **2026-08-21 close** (Saturday probe). Re-pull
pre-open; a regime read is never carried overnight.

### 7a. Regime — the first TSLA GEX read in this repository

`/stock/TSLA/gex-levels`, spot 362.86:

```
call_wall     400        put_wall      350
gamma_magnet  350        gamma_flip    351.08
```

Spot sat **above `gamma_flip`** → positive gamma, **GLUE**, as of Friday's
close. The magnet (350) is $12.86 *below* spot and coincides with the put wall.

**Cross-check disagrees, and that is reportable rather than resolvable.**
`max-pain` for the near expiries reads **337.5–340**, not 350:

| Expiry | max pain | vs `gamma_magnet` 350 |
|---|---|---|
| 2026-08-24 | 340.0 | −10 |
| 2026-08-26 | 340.0 | −10 |
| 2026-08-28 | 332.5 | −17.5 |

`options-expert/SKILL.md` Stage 1: when the magnet and max pain agree it is a
genuine pin read; when they disagree, **say so rather than picking the one that
suits the thesis.** They disagree here. Both nonetheless sit well below spot,
so the shared signal is downward pull — the level is unsettled, the direction
of the pull is not.

**The `options-expert/DATA_LAYER.md` §3e bracket assertion — PASSES for TSLA.** `spot-exposures/strike?limit=500`
returned 202 rows spanning strikes 5 → 990, with **113 above spot and 89
below**, `time 2026-08-21T19:59:44Z`, `price 362.94`. The window brackets spot,
so the profile is interpretable rather than a paging artifact. **Run this
assertion every time** — it is the check that caught a wrong SPY regime read on
2026-08-18.

### 7b. Vol — cheap in its own range, but richer than TSLA is delivering

`/stock/TSLA/volatility/stats` (2026-08-21):

```
iv 0.408   rv 0.373046   iv_rank 14.187
iv_low 0.369  iv_high 0.648     rv_low 0.285  rv_high 0.776
```

`/stock/TSLA/iv-rank` agrees independently: `iv_rank_1y 14.187`, `volatility
0.408`. Two sources, same number — a real cross-check, worth keeping.

Read it honestly, because the two halves point opposite ways:

- **`iv_rank` 14.2 is low** — IV sits near the bottom of its own 1-year range.
  The structure matrix says low rank + directional → long premium.
- **But IV 0.408 > RV 0.373** — options are charging ~3.5 vol points *more* than
  TSLA has actually been delivering. E1b's tell ("prefer the one realizing more
  than implied") points the other way, toward spreads.

Cheap in absolute terms, still not free against recent realized. **Say both.**

### 7c. Implied move per horizon — use `term-structure`, and mind the field name

`/stock/TSLA/interpolated-iv` carries **`days`**, not `dte`, and **`volatility`**,
not `iv`. Asking for `dte` returns nothing and reads exactly like a null field.
Rows (2026-08-21):

| days | volatility | percentile | implied_move_perc |
|---|---|---|---|
| 1 | 0.315 | 0.053 | **1.7%** |
| 5 | 0.395 | 0.329 | 3.1% |
| 7 | 0.416 | 0.429 | 3.9% |
| 30 | 0.408 | 0.091 | 7.9% |
| 365 | 0.482 | 0.111 | 32.3% |

**Prefer `/stock/TSLA/volatility/term-structure`** — it keys on *real tradable
expiries*, which matters more on TSLA than on SPY because the chain is
Mon/Wed/Fri and an interpolated "1-day" horizon is frequently not a tradable
date at all:

| expiry | dte (calendar) | implied_move | implied_move_perc |
|---|---|---|---|
| 2026-08-24 | 3 | **$6.95** | **1.91%** |
| 2026-08-26 | 5 | $11.13 | 3.07% |
| 2026-08-28 | 7 | $14.09 | 3.88% |
| 2026-08-31 | 10 | $15.71 | 4.33% |

Note `dte` here is **calendar** days from the data date, and `iv` comes back
`null` — only `implied_move` and `implied_move_perc` are populated.

**Do not compare implied move to the daily range directly.** §4's $11.82 mean
range is a high-to-low measure; `implied_move` is a ±1σ close-to-close move.
Range typically runs well above it. Comparing the two as if they were the same
statistic would kill sound trades — the same category error the E1 defect in
`options-expert/log/2026-08-18-REPLAY-TEST.md` was made of.

### 7d. Flow — TSLA was heavily call-side on 2026-08-21

`/stock/TSLA/options-volume`:

```
call_volume 3,014,679   put_volume 1,758,875
call ask-side 1,430,044 vs bid-side 1,312,835
net_call_premium +$59,556,905     net_put_premium −$9,895,095
bullish_premium $841.7M           bearish_premium $785.1M
avg_30_day_call_volume 1,330,312  -> relative volume 2.27x
```

Call volume at **2.27× its own 30-day average** on a +5.14% day. The 3/7/30-day
averages are the relative-volume denominator; use them rather than eyeballing.

`/stock/TSLA/net-prem-ticks` gives the per-minute version and **carries
`net_delta`** — the directional-exposure measure the market-wide tide lacks —
plus per-side volume splits and `tape_time`. 391 ticks for the session.

`/option-trades/flow-alerts?ticker_symbol=TSLA` returns `alert_rule`,
`has_sweep`, `has_floor`, `has_multileg`, `all_opening_trades`,
`volume_oi_ratio`, `total_ask_side_prem` vs `total_bid_side_prem`, `iv_end`.

**Market-wide tide, last bar (16:10 ET):** `net_call_premium −$17.0M`,
`net_put_premium −$130.0M`, `net_volume 614,183`. **Both negative** — the
expiration-day signature the playbook logged on 2026-08-14: premium
liquidation, not direction. 2026-08-21 was an OPEX Friday. Read it as
pin/decay, not as a directional signal.

### 7e. VRP is lagged ~28 days on TSLA — never a live reading

`/stock/TSLA/volatility/variance-risk-premium` newest row is dated
**2026-07-24** with `created_at 2026-08-21`. That is a ~28-day structural lag,
because realized vol needs its forward window to have happened.

Worse for TSLA: `/stock/TSLA/volatility/realized` returns
`realized_volatility: null` **and** `unshifted_rv_date: null` on the recent
rows, so the paired series gives nothing at the short end.

**Consequence:** the IV-vs-RV comparison comes from `volatility/stats` (§7b),
which carries `rv` directly. VRP is regime context, never today.

### 7f. The skew anomaly — do not trade this number

`/stock/TSLA/historical-risk-reversal-skew`, 250 rows, **ascending by date**
(the newest row is last — reading `[0]` gives you a year-old value).

Last six sessions of 25-delta `risk_reversal`:

| date | value |
|---|---|
| 2026-08-14 | −0.0299 |
| 2026-08-17 | −0.0283 |
| 2026-08-18 | −0.0203 |
| 2026-08-19 | −0.0244 |
| 2026-08-20 | −0.0101 |
| **2026-08-21** | **−0.6636** |

**A 60× jump in one session.** The five prior sessions sit in a −0.010 to −0.030
band, and `options-expert/DATA_LAYER.md` records SPY in the same order of
magnitude (−0.0277 on 2026-08-18). A move of that size in one day, on an OPEX
Friday, is far more likely a data artifact or an expiration-mechanics effect
than a genuine repricing of protection.

**Standing rule for E5 on TSLA:**

1. Read the **trajectory** of the stable series, never a single level — which is
   what E5 already says, and this is why.
2. Treat an order-of-magnitude single-session jump as **suspect until a second
   session confirms it.** Report it as an anomaly, not as a reading.
3. Never let one such print change a structure decision on its own.

Trajectory through 2026-08-20, ignoring the outlier: skew drifting **toward
zero** (−0.030 → −0.010 over five sessions) — puts getting *less* bid relative
to calls, consistent with the week's rally.

---

## 8. Handling rules that carry over unchanged

From `options-expert/DATA_LAYER.md` §6 — these are not TSLA-specific and are not
restated in full:

1. **Read the timestamp; never assume freshness.**
2. **`data: []` is not a negative result** (UW; applies again once a key exists).
3. **Absent stays absent** — `NA_no_data` / `NA_unresolved`, never `0.0`.
4. **Label greek provenance** — Robinhood greeks are the vendor's.
5. **Never place, modify, or cancel an order.**
