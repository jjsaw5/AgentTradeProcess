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

---

# Addendum — "PLTR seems better suited for a 0DTE setup"

Owner's proposal, 2026-09-02 ~15:45 ET. Tested rather than answered from the
existing rule. **The reasoning behind it is sound and one of its predictions is
confirmed. It still does not clear the bar the owner himself set on 8/31.**

## A. The fact that decides it first: PLTR has no 0DTE except on Fridays

UW `/stock/{t}/expiry-breakdown`, cross-checked against the full
`/stock/{t}/option-chains` symbol list (2,212 PLTR symbols parsed independently;
the two sources agree):

| ticker | next expiries | 0DTE today (Wed 9/2)? | 1DTE (Thu 9/3)? |
|---|---|---|---|
| **PLTR** | **9/4, 9/11, 9/18** | **NO** | **NO** |
| TSLA | 9/2, 9/4, 9/9, 9/11, 9/14, 9/16 | YES | NO |
| NVDA | 9/2, 9/4, 9/9, 9/11, 9/14, 9/16 | YES | NO |
| SPY | 9/2, 9/3, 9/4, 9/8, 9/9, 9/10 | YES | YES |
| PG | 9/4, 9/11, 9/18 | NO | NO |

**PLTR lists Friday weeklies only.** TSLA and NVDA carry Mon/Wed/Fri; SPY is
daily. So "a PLTR 0DTE setup" is not a setup — it is **one trading day a week**,
and only on the Fridays whose setup happens to be worth taking. Call it two or
three real opportunities a month.

> **Recorded against myself (§3, "a 200 is not a success"):** the first pull of
> this table keyed on `expiry` when the field is `expires`. It returned
> `HTTP 200` with an empty list for **every ticker**, which read as "no near
> expiries anywhere" — a conclusion that would have been spectacularly wrong and
> was caused entirely by my own bad key. Caught before anything was written,
> because six empty lists in a row is not a market fact. This is the exact
> failure mode §3 names, arriving from a direction the rule did not anticipate:
> not a bad parameter value, but a bad field name on the way out.

## B. What is right about the idea, stated first

**1. The front-loading argument is correct** (§3 above): PLTR's opening hour
moves 4.6× its 2 PM hour, and ~three-quarters of the day's range is set before
11:00. An instrument that does its work early is, in principle, better matched to
a contract that expires the same day than to one carrying overnight risk it never
uses.

**2. 0DTE is the only thing that makes PLTR affordable, and that is a real
point.** The blocking finding in §5 above was that the qualifying 2-DTE contract
costs $260 — 55% of the account. Applying the measured theta to Friday:

| PLTR 9/4 170C | value |
|---|---|
| Mid now (2 DTE, 15:55 ET) | **$2.50** ($250) |
| Theta | **−$0.727/day = 29% of premium per day** |
| Rough value at Friday's open, spot unchanged | **≈ $1.05–1.50** (**$105–150**) |

*(Estimate, not a quote. Theta accelerates into expiry and this ignores any IV
move — treat the range as indicative and re-price on the morning.)*

**$105–150 is affordable on a $475 account where $260 is not.** The owner
identified the one structural change that fixes the sizing problem. That is a
genuine observation, not a rationalisation.

**3. PLTR Fridays really are its cleanest trend days.** FMP EOD, 2026-03-01 →
2026-09-01:

| PLTR weekday | n | median range | **median body ÷ range** |
|---|---|---|---|
| Mon | 26 | 3.61% | 45% |
| Tue | 27 | 4.08% | 42% |
| Wed | 26 | 4.08% | 45% |
| Thu | 26 | 4.33% | 45% |
| **Fri** | **23** | 3.67% | **60%** |

Fridays are narrower but far more directional — 60% against 45% for the rest of
the week. On the one day PLTR's 0DTE exists, PLTR trends best. That is a real
coincidence in the proposal's favour and it was worth finding.

**And here is why it should not yet be believed.** The identical test on the
other two names:

| | Mon | Tue | Wed | Thu | Fri |
|---|---|---|---|---|---|
| TSLA body/range | **65%** | 39% | 40% | 42% | 44% |
| NVDA body/range | **65%** | 44% | 52% | 42% | **61%** |

TSLA shows **no** Friday effect (44% vs 44% for Mon–Thu), and **Monday** is the
standout day for both TSLA and NVDA. Fifteen weekday-ticker cells were examined
and two or three came back high; at **n=23 Fridays** that is what
multiple-comparisons noise looks like. The finding is **suggestive and
underpowered — not evidence.** It has not been tested out of sample and must not
be traded on as it stands.

## C. What is wrong with it

**1. 0DTE makes PLTR's one real defect worse, not better.** PLTR already fails
the §3a 2% gate on 78% of 2-DTE contracts. Expiry day widens spreads rather than
tightening them. Measured on TSLA — *the liquid name* — at 15:50 ET on its own
0DTE:

| TSLA 0DTE 9/2 | bid × ask | spread | delta | volume |
|---|---|---|---|---|
| 350C | 5.55 × 5.75 | 3.5% | 0.98 | 46,503 |
| 352.5C | 2.77 × 2.87 | 3.5% | 0.92 | 161,527 |
| **355C** | **0.67 × 0.71** | **5.8%** | 0.63 | 320,367 |
| 357.5C | 0.06 × 0.07 | 15.4% | 0.10 | 165,661 |
| **360C** | **0.00 × 0.01** | **200%** | 0.01 | **159,294** |
| 352.5P | 0.03 × 0.04 | 28.6% | 0.05 | 216,665 |

**Not one contract on the board passes a 2% gate.** Every spread is 3.1% or
worse. If TSLA — which passes 81% of the time at 2 DTE — looks like this on
expiry day, PLTR at 2.6× TSLA's normal spread will be worse, on a day it is the
only expiry available and order flow has nowhere else to go.

**2. The two lines in that table worth sitting with:** **159,294** TSLA 360 calls
traded today and are now worth **zero**. **216,665** 352.5 puts are worth **three
cents**. Those are not exotic strikes — they were the obvious ones to buy this
morning, a point or two from the money.

**3. Delta goes binary and the middle disappears.** At 15:50, exactly **two**
TSLA 0DTE contracts remained in the 0.35–0.65 delta band the strategy specifies.
Everything else had resolved to 0.99 or 0.01. A 0DTE position does not drift
against you — it converts, late in the session, into either intrinsic value or
nothing. There is no wrong-then-right on expiry day.

**4. It reopens the exact door that was closed by evidence.** From §1 of this
spec, 106 reconstructed round trips: **0DTE — 85 trades, −$1,019, 46% win.**
1DTE — 21 trades, −$353, 38% win. The owner's own instruction on 8/31 was *"no
more 0DTE trades **unless we have data that shows it's worth it**."* That set the
burden of proof on the 0DTE side, and it was the right place to put it.

**Does anything above discharge that burden? No.** What was found is: the setup
exists one day a week; 0DTE solves affordability; PLTR Fridays trend better at
n=23 in a test that flags Mondays elsewhere and is probably noise; and expiry day
makes a marginal spread materially worse. That is a **hypothesis worth testing**,
which is a different object from data showing it is worth it.

## D. What to actually do — pre-registered, shadow, Friday 2026-09-04

The disciplined move is neither to trade this nor to drop it. **Test it in shadow
mode**, where being wrong is free and being right is bankable, and where it
counts toward the §7 gate of 10 graded tickets. Written up as **Ticket 5**
(`2026-09-04-TICKET-5-PLTR-0DTE-SHADOW.md`), pre-registered per §9 before the
session.

**The two things Friday must show, both of which can fail:**

1. **The 10:00 ET spread test — this is the real gate.** Every spread number in
   this file was pulled between 15:39 and 15:55, the tightest part of the
   session. **The window we would trade is still `NA_no_data`.** If PLTR's ATM
   0DTE spread at 10:00 on Friday is above 2%, the idea is finished on liquidity
   and nothing else needs deciding.
2. **The affordability estimate.** Does the ATM contract actually price at
   $105–150, or does Friday-morning IV hold it above $200?

**Prediction recorded before the fact, so it can be graded:** I expect the
spread test to **fail** — PLTR's ATM 0DTE spread at 10:00 to come in **above 2%**,
most likely 3–6%, on the reasoning that expiry day widened even TSLA to 3.5% at
the money. I expect the affordability estimate to **hold**. If the spread comes
in at or under 2%, I am wrong, that is a real finding, and the idea earns a
second ticket rather than a dismissal.

**Nothing here is ratified. §2 stands: Claude does not execute, and this is a
shadow ticket — no capital.**
