# 0DTE candidate screen

Written 2026-09-10, 08:35 ET (premarket). Owner request: *"identify stocks that are good
candidates to 0dte trade."*

Screened mechanically, on the instrument only. **This file does not argue that 0DTE is a
good idea for this account** — it answers which instruments are least hostile to it, which
is a different question. The owner's 8/31 rule stands: *no more 0DTE unless we have data
that shows it's worth it.* Nothing below discharges that. `UNCALIBRATED` per §7.

---

## 1. First filter: most stocks do not have a 0DTE at all

UW expiry-breakdown, cross-checked, 28 liquid names:

| cadence | tickers |
|---|---|
| **Daily** (0DTE every session) | **SPY, QQQ, IWM, GLD** |
| **Mon / Wed / Fri** | TSLA, NVDA, AAPL, MSFT, AMZN, META, GOOGL, AMD, INTC, TLT, XLE |
| **Friday only** | PLTR, SOFI, F, BAC, COIN, MSTR, MARA, RIOT, NIO, SMCI, HOOD, AAL, T |

**On today — a Thursday — exactly four of twenty-eight names have a 0DTE, and not one is a
single stock.** Every single name runs Mon/Wed/Fri at best.

The structural consequence is unavoidable: **0DTE as a daily activity is an index-ETF
activity.** A single-name 0DTE plan is really a three-days-a-week plan, and for most names
a Friday-only plan.

## 2. Second filter: the spread at the money

ATM contracts (delta 0.42–0.58) on each name's nearest 0DTE-capable expiry. §3a gate is
**≤2% of mid**.

**Timestamp, and it matters: tape `2026-09-09T21:31Z` — these are LAST CLOSE marks, pulled
premarket.** Spreads at 10:00 will differ. For SPY/QQQ the margin is wide enough that the
verdict is safe; for the 2–4% names it is not, and those must be re-measured live.

| ticker | ATM cost | median spread | gate |
|---|---|---|---|
| **SPY** | $209 | **0.7%** | **PASS** |
| **QQQ** | $281 | **0.9%** | **PASS** |
| NVDA | $308 | 1.6% | pass (Mon/Wed/Fri only) |
| PLTR | $267 | 1.7% | pass (Friday only) |
| TSLA | $532 | 2.1% | FAIL |
| INTC | $228 | 2.2% | FAIL |
| IWM | $118 | 2.6% | FAIL |
| META | $895 | 2.9% | FAIL + unaffordable |
| AAPL / AMD | $344 / $871 | 3.6% | FAIL |
| AMZN / COIN / GLD / GOOGL | — | 5.6–8.7% | FAIL badly |
| F | $17 | **20.2%** | FAIL — cheap is not affordable |

## 3. The test that actually decides it

Everything above is friction. This is the question: **buy an ATM 0DTE at the open, hold to
the close — how often did that finish in the money?** Measured on ~130 sessions of real
opens and closes (2026-03-01 → 2026-09-09), against the actual premium being charged.

| ticker | premium | breakeven as % of the day's range | call wins | put wins | **EITHER** |
|---|---|---|---|---|---|
| **QQQ** | $2.81 | **30%** | 38% | 28% | **66%** |
| **SPY** | $2.09 | **32%** | 33% | 26% | **59%** |
| IWM | $1.18 | 31% | 29% | 31% | 59% |
| AMZN | $2.42 | 42% | 29% | 26% | 54% |
| TSLA | $5.32 | 42% | 29% | 24% | 53% |
| AMD | $8.71 | 44% | 31% | 20% | 50% |
| COIN | $3.86 | 41% | 26% | 24% | 50% |
| GOOGL | $3.26 | 45% | 28% | 20% | 48% |
| PLTR | $2.67 | 47% | 24% | 23% | 47% |
| INTC | $2.28 | 46% | 22% | 22% | 44% |
| NVDA | $3.08 | 53% | 20% | 21% | 41% |
| GLD | $2.58 | 52% | 20% | 21% | 41% |
| META | $8.95 | 58% | 16% | 17% | 33% |
| AAPL | $3.44 | 58% | 19% | 12% | **31%** |

**EITHER** = the share of days on which *somebody* holding an ATM 0DTE to expiry made
money. **It is the ceiling for a trader who calls direction correctly every single day.**

**The median is 49%.** On more than half of all sessions, across most of these names,
*neither* the call nor the put buyer profited. The premium is priced at roughly the value
of the day's whole expected move — the market maker has sold you the range at fair value
and kept the spread.

Note what the breakeven column is saying: on **META and AAPL you need the stock to close
58% of its entire typical daily range in your chosen direction**, from the open, to break
even. On QQQ you need 30%. That single number explains most of the ranking.

## 4. The answer, and the collision

**On the mechanics, two names qualify and they are QQQ and SPY.** QQQ is first on every
axis: tightest spread relative to movement (0.9%), lowest breakeven as a share of range
(30%), highest either-side hit rate (66%), affordable at 2 contracts, daily expiries.

**And those are precisely the two instruments this account loses money in.**

From `SWING_STRATEGY.md` §1, 106 reconstructed round trips:

| | trades | P&L | win rate |
|---|---|---|---|
| **QQQ** | 6 | **−$555** | **17%** |
| **SPY** | 17 | **−$443** | 41% |
| **Index ETFs combined** | **23** | **−$998** | |

§2 of the strategy bars index ETFs outright, on that evidence.

**The screen and the account record point at the same two tickers with opposite signs, and
that is the finding.** It is not resolvable by picking a different stock: the names that
avoid the §2 problem (TSLA, NVDA, PLTR, META) are worse on every mechanical axis —
breakevens of 42–58% of daily range, hit rates of 33–53%, and no daily expiry.

There is no ticker on this board that is both mechanically good for 0DTE and outside the
category this account has lost money in. That is a genuine constraint, not a failure of
searching.

## 5. What this screen does not establish

- **That 0DTE is worth doing.** It ranks instruments; it says nothing about whether the
  activity has positive expectancy for this trader. Standing evidence says it does not:
  **85 0DTE trades, −$1,019, 46% win.**
- **That the 2026-09-02 counter-evidence generalises.** SPY was that day's best instrument
  (+$88 on 4 trades) against a −$376 week. One green day.
- **Anything about intraday exits.** Every number here is open-to-close held to expiry. A
  trader who exits at +50% or cuts at 30 minutes has a different distribution that this
  file does not measure. **This is the single largest gap** — the §5a 30-minute rule and
  §6b give-back rule are exactly such exits, and their effect on these odds is unmeasured.
- **Live spreads.** All quotes are 2026-09-09 closing marks. The 10:00 window is
  `NA_no_data`.
- **Any edge.** Nothing here identifies a reason to be directionally right, which is the
  only thing that turns a 30%-of-range breakeven into money.

## 6. If the owner proceeds anyway

Recorded so the decision is written before the fact, not reconstructed after (§9):

- **QQQ, not a single name.** The mechanics are not close.
- **Re-measure the spread at 10:00.** A 0.9% close mark is not a 10:00 quote.
- **One contract.** $281 is 48% of a $590 account; that is the position, not a unit of one.
- **The premium is the risk.** No stop protects a 0DTE from a gap in the last hour.
- **§6a two-loss stop, §5a 30-minute rule, §6b give-back all apply unchanged**, and a
  0DTE gives less room for all three, not more.
- **Grade it as a shadow ticket first.** §7 needs 10 graded tickets; five exist. Three
  0DTE shadow tickets on QQQ would answer the expectancy question at zero cost, and would
  measure the one thing this file could not — what intraday exits do to the odds.
