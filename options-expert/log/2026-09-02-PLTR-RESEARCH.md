# PLTR — instrument research

Written 2026-09-02, 15:45 ET (market open, 15 minutes to the close). Prompted by
the owner's observation that *"PLTR seems to be a stock that has big moves each
day."*

**Verdict up front: the observation is correct and PLTR is the most volatile name
we have measured. It is also, on today's snapshot, the wrong options instrument
for a $475 account — for a reason that has nothing to do with volatility.**

All figures below are measured, sourced and dated. Nothing here is calibrated
(`CLAUDE.md` §7); this is instrument characterisation, not an edge claim.

---

## 1. The observation is right — PLTR moves more than anything else on our board

FMP EOD, **65 sessions, 2026-06-01 → 2026-09-01**:

| | avg daily range | median daily range | median $ range | ann. vol | days moving >3% |
|---|---|---|---|---|---|
| **PLTR** | **4.75%** | **4.35%** | $5.78 | **79.3%** | **28%** |
| TSLA | 4.08% | 3.81% | $13.60 | 56.3% | 33% |
| NVDA | 3.22% | 3.02% | $6.11 | 42.2% | 23% |
| XLE | 1.81% | 1.71% | $0.98 | 22.3% | 5% |
| PG | 1.87% | 1.66% | $2.45 | 20.5% | 2% |
| SPY | 0.98% | 0.87% | $6.43 | 13.5% | 0% |

PLTR has the widest percentage range and the highest annualised volatility of
the six. **On percentage terms it moves more than TSLA.** In dollars it moves
less ($5.78 vs $13.60) because the share price is half of TSLA's.

Today is a textbook example: PLTR opened **176.99**, traded down to **165.72**,
and sits at **169.32** at 15:39 — a **7.15% range** and **−4.33% from the open**.

## 2. But "big moves" is not the same as "trends cleanly"

The measurement that matters for a rules-based entry is how much of the range is
directional rather than chop. Same 65 sessions:

| | body ÷ range (median) | open was the day's high or low | up-closes |
|---|---|---|---|
| TSLA | 50% | 15% | 49% |
| NVDA | 47% | 12% | 46% |
| **PLTR** | **45%** | **12%** | 51% |
| PG | 37% | 9% | 52% |

*(body ÷ range = median |close − open| as a share of the high−low range. 100% is
a clean one-way trend day; 0% is a round trip.)*

**PLTR is not more trend-like than TSLA — it is marginally less so.** It is a
wider chop, not a cleaner trend. The extra volatility shows up as a bigger range
around the same amount of net direction. That is worth stating plainly, because
"it moves a lot" and "it moves somewhere" are different properties and only the
second one pays.

**Gap risk is the highest of the four.** PLTR gapped more than 1% on **34 of 64**
sessions (53%) and those gaps traded back to the prior close only **47%** of the
time. TSLA: 24/64 gapping, 58% filled. This bears directly on
`SWING_STRATEGY.md` §5c (one overnight hold): PLTR gaps against you roughly every
other session, and a stop does not protect through a gap.

## 3. The move is front-loaded, and §4 is timed to miss it

Median 5-minute bar range by hour (FMP 5-min, n=84 bars per hour):

| hour (ET) | PLTR | TSLA |
|---|---|---|
| 09:30 | **0.88%** | 0.72% |
| 10:00 | 0.46% | 0.36% |
| 11:00 | 0.31% | 0.29% |
| 12:00 | 0.22% | 0.21% |
| 13:00 | 0.23% | 0.19% |
| 14:00 | **0.19%** | 0.18% |
| 15:00 | 0.22% | 0.25% |

PLTR's opening hour moves **4.6× as much per bar as its 2 PM hour**. Roughly
three-quarters of the day's range is set before 11:00.

**This is a genuine conflict between the instrument and our own rules.**
`SWING_STRATEGY.md` §4 bars any entry before 10:00 ET — a rule written because
this account's 0–5-minute and pre-10:00 trades lost money. Applied to PLTR, that
rule systematically hands over the part of the day where PLTR actually moves. It
is not obvious which side should give. **Do not resolve this by relaxing §4 on a
hunch** — §4 rests on 119 graded trades and this observation rests on a range
profile, which is not the same evidence.

## 4. The disqualifier: PLTR's options chain fails our liquidity gate

`SWING_STRATEGY.md` §3a rejects any contract whose bid-ask spread exceeds 2% of
mid. UW `/stock/{t}/option-contracts`, live NBBO, tape timestamps
**19:39–19:41Z (15:39–15:41 ET)**. Contracts with mid ≥ $1.00:

| | 2 DTE — pass / total | median spread | 7–16 DTE — pass / total | median spread |
|---|---|---|---|---|
| TSLA | **26/32 (81%)** | 1.3% | **100/138 (72%)** | 1.4% |
| NVDA | 16/19 (84%) | 1.4% | 50/74 (68%) | 1.5% |
| **PLTR** | **5/23 (22%)** | **2.6%** | **6/63 (10%)** | **3.2%** |
| PG | 0/25 (0%) | 9.5% | 0/23 (0%) | 9.8% |

**PLTR sits between PG (unusable) and TSLA (clean), and closer to the middle than
is comfortable.** At the §3 structure — 2–5 DTE, delta 0.45–0.60 — the entire
PLTR chain offers **three** contracts and **one** passes:

| contract | bid × ask | spread | delta | volume | cost | gate |
|---|---|---|---|---|---|---|
| PLTR 9/4 167.5C | 3.85 × 3.95 | 2.6% | 0.60 | 11,770 | $390 | **FAIL** |
| **PLTR 9/4 170C** | **2.58 × 2.62** | **1.5%** | **0.46** | **26,563** | **$260** | **PASS** |
| PLTR 9/4 170P | 3.20 × 3.30 | 3.1% | 0.54 | 19,521 | $325 | **FAIL** |

**Every 9/11 contract at tradeable delta fails**, from 2.2% to 5.6%.

The one contract that passes is the single most-heavily-traded strike in the
chain. That is the finding: **PLTR's options are liquid at exactly one strike at
a time and illiquid one strike away.** TSLA offered six passing contracts across
both directions on the same pull.

**Two limits on this table, stated because they matter:**

1. **It is a 15:40 ET snapshot.** Spreads are tightest late in the session and
   widest at the open. The window we would actually trade — around 10:00 — is
   **not sampled**. `NA_no_data`, and it is the single most important open
   question here.
2. One pull, one day. Nothing establishes that today's spreads are typical.

## 5. The sizing math, which is where it actually ends

Account read live at 15:25 ET: **$475.64 cash.** The one qualifying contract
costs **$260 = 55% of the account.**

Adverse move on 1× PLTR 9/4 170C (delta 0.46; gamma and theta ignored, so these
are optimistic):

| PLTR moves | option loses | % of account |
|---|---|---|
| −$0.50 | −$23 | 5% |
| −$1.00 | −$46 | 10% |
| −$2.00 | −$92 | **19%** |
| −$3.00 | −$138 | **29%** |
| −$5.78 *(median daily range)* | −$266 | **56%** |

Now invert it. A 4%-of-account stop is **$19**, which is a PLTR move of
**$0.41**. PLTR's median 5-minute bar in the opening hour is **$1.49**.

> **The stop this account can afford is 3.6× smaller than one ordinary
> five-minute bar in the instrument.**

`CLAUDE.md` §5 covers this exactly: *never widen a stop to fit a budget… if the
correct stop makes the trade too large, the trade is too large — take fewer
contracts or skip it.* One contract is the floor. There is nothing to reduce.

Add the friction: crossing the 1.5% spread on the qualifying contract costs **$4
round trip** before the stock moves; on the 167.5C it is **$10**.

## 6. What PLTR is actually good for right now

**Shares.** At 169.32 two shares cost **$339** and carry the full $5.78 median
daily range — about **±$11.56 a day** on the position, with **no spread problem,
no theta, and no expiry**. Against PG shares (2 × $147.63 = $295, ±$4.90/day),
PLTR gives roughly 2.4× the daily movement for a similar outlay.

That makes PLTR a legitimate candidate to sit alongside PG in
`SWING_STRATEGY.md` §2a as a practice vehicle — **PG for reading a slow tape,
PLTR for practising exits under real movement.** It is *not* a proposal to trade
PLTR options at this account size.

**Not proposed, not ratified.** Recorded for the owner's decision.

## 7. Context and what is not known

- **No earnings until 2026-11-02** (FMP; last report 2026-08-03). PLTR's
  volatility is structural, not event-driven, and no §5e blackout applies.
- **PLTR closed below its gamma flip today** — spot 169.32 against a flip at
  **170.18**, call wall and gamma magnet both **172.5**, put wall **150** (UW
  gex-levels, 19:41Z). Below the flip is the amplifying regime: dealer hedging
  adds to moves rather than damping them. Consistent with a −4.33% day.
- **Max pain for both 9/4 and 9/11 is 180**, roughly $11 above spot. No pin
  support anywhere near the money.

**Not established by anything above:**

- Whether PLTR spreads pass the gate at 10:00 ET. **This is the question that
  decides the whole file** and it needs a morning pull.
- Any edge, in either direction. This is instrument characterisation only.
- Intraday trend persistence. FMP's 5-min history returned **7 sessions**; a
  71% persistence figure computed on n=7 is noise and is **deliberately not
  reported as a finding.**
- Whether the §4 pre-10:00 rule should bend for a front-loaded instrument.
  Flagged, not answered.
