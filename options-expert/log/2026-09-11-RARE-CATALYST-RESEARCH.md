# RARE (Ultragenyx) — verification of a r/Shortsqueeze post

Written 2026-09-11 after the close. Owner forwarded a Reddit post ("could be the play of
the year") and asked for independent research. Every claim checked against primary sources.
`UNCALIBRATED` per §7 — this is verification, not a recommendation.

**Company:** Ultragenyx Pharmaceutical (RARE). **Close 9/11: $14.29** (−0.73%), on
**2.21M shares against a 2.7M average** — below average volume, three hours after the post.

---

## Claim-by-claim

| # | Claim | Verdict |
|---|---|---|
| 1 | PDUFA date September 19, 2026 | **TRUE** |
| 2 | Stock crashed on another drug's failed endpoints | **TRUE** |
| 3 | "$28 ten days ago, now $14" | **Misleading** (see §3) |
| 4 | 18% short interest | **Overstated — 16.1%, and stale** |
| 5 | "CRL last year based solely on the manufacturing plant" | **`UNVERIFIED`** |
| 6 | "extremely high probability of approval" | **`UNVERIFIED` — no source given or found** |

### 1. PDUFA — CONFIRMED
UW FDA calendar: *"Ultragenyx Pharmaceutical announced that The FDA set a Prescription Drug
User Fee Act (PDUFA) action date of September 19, 2026."* Source: company press release.

- **Drug: UX111** (rebisufligene etisparvovec), AAV9 gene therapy
- **Indication: Sanfilippo syndrome Type A (MPS IIIA)**, a fatal neurodegenerative
  lysosomal storage disorder
- Seeking **accelerated approval**
- BLA resubmitted **2026-01-30**; FDA accepted for review **2026-04-02**

### 2. The crash — CONFIRMED
**2026-09-02, 16:01 ET (after the close):** Phase 3 **"Aspire"** trial in **Angelman
Syndrome** missed its endpoints. 9/3: opened 14.00 from a 26.53 close, **−47% on 27.2M
shares** vs a 2.7M average. Company reported as cutting costs.

### 3. "$28 ten days ago" — technically true, materially misleading
$28.50 was the **intraday high on 2026-08-20**. That day opened 28.39 and **closed 25.32**.
The $28 print existed for part of one morning. More on why that morning matters in §7.

### 4. Short interest — overstated and stale
UW `shorts/interest-float/v2`:

| field | value |
|---|---|
| short interest | 15,887,767 |
| total float | 98,588,873 |
| **SI as % of float** | **16.1%** (not 18%) |
| days to cover | **7.78** |
| **market_date** | **2026-08-14** |

**The reading predates the 9/3 crash by three weeks.** Post-crash short interest is
`NA_unresolved` and will not be known until the next exchange report.

### 5–6. The CRL characterisation — UNVERIFIED, and it is the whole thesis
A BLA **resubmission** on 2026-01-30 is confirmed, which implies a prior Complete Response
Letter. **Nothing in our sources confirms the CRL was "solely" about the manufacturing
plant**, and that distinction carries the entire argument: a facility-only CRL has a very
different re-approval profile from one citing efficacy or safety. The post asserts it
without a source. So does its "extremely high probability of approval."

**Not disproven — unsourced.** Per §3 that is `UNVERIFIED`, and a thesis resting on an
unverified premise is not a thesis.

---

## 7. The finding that outranks everything above

**This exact trade already ran three weeks ago, and it lost.**

On **2026-08-19 at 17:21 ET**, Ultragenyx announced **FDA approval of GENGLYCOS gene
therapy — "the First-Ever FDA-Approved Treatment"** for its indication. That is precisely
the event this post is betting on.

What the stock did the next session:

| 2026-08-20 | |
|---|---|
| open | 28.39 (gapped up on the approval) |
| high | **28.50** |
| **close** | **25.32** |
| vs prior close (26.24) | **−3.5%** |
| **vs the open** | **−10.8%** |

**The approval was sold within hours.** And the $28.50 the post cites as evidence of a
"50% discount" **is that spike top** — the high tick of a failed approval-day gap.

CLAUDE.md §3: *do not assume good news lifts a stock — check the actual reaction.* The
actual reaction, at this company, three weeks ago, to an FDA approval, was a red close.

## 8. The squeeze thesis fails on the borrow data

`SKILL.md` §5 thresholds: SI >20% of float, days-to-cover >3, **fee >5%**, **availability
<100k shares**.

| metric | RARE | §5 threshold | verdict |
|---|---|---|---|
| SI % of float | 16.1% | >20% | below |
| days to cover | **7.78** | >3 | **supportive** |
| **borrow fee** | **0.40%** | >5% | **fails badly** |
| **shares available** | **3,500,000** (live 9/11 15:24) | <100k | **fails badly** |

**A squeeze requires forced covering, and forced covering requires an expensive or
unavailable borrow.** RARE's borrow costs 0.40% a year and there are 3.5 million shares
sitting there to lend. Shorts are under no pressure whatsoever and can hold indefinitely.

High days-to-cover with a cheap, plentiful borrow is not a squeeze setup — it is simply a
stock that is heavily and comfortably shorted.

## 9. The options trap — the expiry named in the post cannot pay

**The 9/18 contracts expire the day BEFORE the September 19 PDUFA.**

The post says the FDA "would most likely make the announcement next Friday the 18th. Maybe
even sooner." That is a guess about **timing**, not outcome. Buy the 9/18 expiry and you are
betting the agency acts early; if it acts on the 19th — its actual deadline — the option
expires worthless **no matter how good the decision is.**

| RARE expiry | covers the PDUFA? |
|---|---|
| **2026-09-18** | **NO — expires first** |
| 2026-10-16 | yes |

Spreads on the first expiry that does cover it (10/16 calls), against the §3a 2% gate:

| strike | bid × ask | spread | delta | IV | cost | breakeven |
|---|---|---|---|---|---|---|
| 12.5 | 2.15 × 2.45 | **13.0%** | 0.78 | 80% | $230 | 14.80 |
| 15.0 | 0.75 × 0.90 | **18.2%** | 0.44 | 65% | $82 | 15.82 |
| 17.5 | 0.30 × 0.40 | **28.6%** | 0.21 | 70% | $35 | 17.85 |
| 20.0 | 0.15 × 0.20 | **28.6%** | 0.11 | 79% | $18 | 20.18 |
| 25.0 | 0.05 × 0.10 | **66.7%** | 0.05 | 91% | $8 | 25.07 |

**Every contract fails the 2% gate by 6–33×.** The cheap ones are the worst: the $8
lottery ticket loses two-thirds of its value the instant you cross the spread.

## 10. The move is already priced

ATM straddle, 10/16 $15 strike: call $0.82 + put $1.50 = **$2.33** on a $14.29 stock.

**The market is pricing roughly ±16% by 10/16.** The post's "100–200%+" requires an outcome
far outside what is already in the price — which is possible on a binary, but it is not a
discovery. IV of 65–91% is the market charging in advance for exactly the event being
described as an edge.

## 11. What the post omits

- **Securities litigation.** Pomerantz opened an investigation on 2026-09-08 over the
  Angelman disclosure.
- **The GENGLYCOS approval and its rejection by the tape** (§7).
- **That its own 9/18 expiry cannot cover the event** (§9).
- **That the borrow is free and plentiful** (§8).

## 12. Source quality, stated once and factually

The author writes: *"ChateGPT is forecasting over 100% - 200%+ gain. Yes, I always use AI
for calculations"* and *"I use ChatGPT for my research."* No primary source is cited for the
approval-probability claim, which is the load-bearing one. *"I'm not planning on posting
this anywhere else. You guys are the first and only ones to hear about this thing"* is an
exclusivity claim made in a public subreddit.

None of that makes the verifiable facts wrong — the PDUFA date and the crash both check out.
It does mean the **interpretive** claims carry no evidentiary weight and must be treated as
`UNVERIFIED` rather than inherited.

## 13. Bottom line

**What is real:** a genuine, dated, binary catalyst on 2026-09-19 for UX111 in Sanfilippo A,
on a stock that has already been cut in half by an unrelated trial failure.

**What is not established:** that approval is likely, that the prior CRL was
manufacturing-only, that a squeeze mechanism exists, or that the upside is not already
priced.

**What is disqualifying for this account, independent of the thesis:**

1. The **9/18 expiry does not cover the event.**
2. Every 10/16 contract fails the liquidity gate by 6–33×.
3. IV 65–91% means buying the event at the market's own price, with no edge.
4. A **binary FDA event is uncappable risk on long premium** — there is no stop, because
   the outcome arrives as a gap.
5. **The most relevant base rate available — this company's own FDA approval three weeks
   ago — produced a red close.**

**Not proposed. Not a ticket. Recorded so that if the owner watches it through the 19th,
the analysis was written before the outcome was known (§9).**

**Pre-registered, so this file can be graded:** I expect no tradeable setup to emerge here
for this account. If UX111 is approved and RARE rallies hard, this file was still correct
about the *instruments* (expiry mismatch, spreads, priced-in IV) and wrong about nothing it
actually claimed — but that distinction should be judged against this text, not rewritten.
