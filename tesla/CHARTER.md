# TSLA 0–5DTE Options Process — Charter

Established 2026-08-22 by the account owner. This is the scope document for a
single-name options process: **TSLA only, 0–5 days to expiration, 0DTE
primary.** It runs inside Claude Code as a set of session commands. It is not
an application and it never places an order.

Read this before `tesla/DATA_LAYER-TSLA.md`, and read both before running any
`/tsla-*` command.

---

## 1. Scope, and what it deliberately excludes

| In scope | Out of scope |
|---|---|
| TSLA options, 0–5 DTE | every other underlying |
| Intraday holds, 0DTE primary | swing, overnight, LEAPS |
| Long premium and debit verticals | naked short premium, undefined risk |
| Framing, sizing, monitoring, grading | order placement — the human executes |

The existing modules are **unchanged and still run**:

- `daily-market-brief/SKILL.md` stays market-wide. Macro, regime and catalysts
  are inputs to a TSLA trade, not noise to be filtered out. `/tsla-open` reads
  the day's brief from `briefs/YYYY-MM-DD.md`.
- `options-expert/` stays as-is. Its edge tests E1–E5 are the parent of this
  module's tests; nothing there is retargeted or retired.
- `playbook/PLAYBOOK.md` still governs entries, stops, timing and grading. Its
  dated validated behaviours were validated **on SPY and QQQ**. §4 below records
  which of them transfer to TSLA and which do not.

This module never writes outside `tesla/` and `.claude/skills/tsla-*/`.

---

## 2. The expiration calendar is the first constraint

**TSLA does not have daily expirations.** Verified from the live Robinhood chain
on 2026-08-22:

```
2026-08-24 (Mon)  08-26 (Wed)  08-28 (Fri)  08-31 (Mon)  09-02 (Wed)  09-04 (Fri)
then weeklies: 09-11, 09-18, 09-25, 10-02, 10-16, ...
```

Monday / Wednesday / Friday. So:

| Trading day | 0DTE available? | Shortest DTE | 0–5DTE expiries in range |
|---|---|---|---|
| Monday | **yes** | 0 | Mon(0), Wed(2), Fri(4) |
| Tuesday | no | 1 | Wed(1), Fri(3) |
| Wednesday | **yes** | 0 | Wed(0), Fri(2), Mon(5) |
| Thursday | no | 1 | Fri(1), Mon(4) |
| Friday | **yes** | 0 | Fri(0), Mon(3), Wed(5) |

Consequences the process must respect rather than discover each week:

- **0DTE is a three-day-a-week strategy on TSLA.** Tuesday and Thursday are
  1DTE days. A process built on "0DTE every morning" would silently trade 1DTE
  twice a week and mislabel its own log.
- **`/tsla-open` states the day's DTE map before anything else.** Which expiry
  is 0DTE today is a fact to be read off the chain, never assumed.
- Holidays shift this. Re-read the chain; do not carry last week's map forward.

## 2a. The bell is 3:30 PM ET, not 3:45

The TSLA chain reports `sellout_time_to_expiration: 1800` (seconds), confirmed
per-contract as `sellout_datetime: 2026-08-24T19:30:00Z` — **15:30 ET**.

The playbook's 0DTE section was written against SPY, where Robinhood force-closes
at 3:45 and 3:30 is the human's decision bell. **On TSLA those two moments
collapse into one.** 3:30 is not the last chance to decide; it is the moment the
broker acts.

Therefore, for TSLA 0DTE:

- **3:00 PM ET is the decision bell.** Whatever P&L exists then is effectively
  the result.
- **3:25 is the hard exit.** Past that you are racing the broker's own
  liquidation, at market, into whatever the book looks like.
- Power hour as the playbook describes it does not exist here. The window
  closes half an hour earlier than the SPY habit expects.

---

## 3. Risk configuration

**Ratified 2026-08-22 by the account owner.** See `CLAUDE.md` §5 for the
repository-level record and the number this replaced.

```
MAX_TRADE_RISK_USD    = 450    # max LOSS on the one open bet. A DOLLAR figure.
MAX_TRADE_PREMIUM_USD = 400    # unchanged — spend cap, not a loss cap
MAX_OPEN_HEAT_USD     = 450    # equals per-trade risk: there is only one bet
MAX_CONCURRENT        = 1      # derived, not chosen — see §3b
```

Equity is read live from Robinhood `get_portfolio` on every run. Never
hardcoded, never carried from a prior session. If it cannot be read, nothing
gets sized.

### 3a. This is a dollar figure and it does not scale

`MAX_TRADE_RISK_USD` replaces `options-expert`'s `MAX_TRADE_RISK_PCT = 0.04`
for TSLA trades only. Unlike a percentage it does not move with the account, and
the direction of that failure is the dangerous one: **as equity falls, a fixed
dollar risk becomes a larger fraction of what is left.**

At the equity read on 2026-08-22 (`$1,269.86`):

| Equity | $450 as a fraction |
|---|---|
| $1,269.86 (today) | **35.4%** |
| $1,000 | 45.0% |
| $900 | 50.0% |

Three consecutive maximum losses exceed the account as it stands today. That is
a statement of arithmetic, not an objection — the number is ratified. But the
process must **print the live percentage on every card**, so the figure is
never invisible at the moment it matters.

**Review trigger:** if equity drops below $1,000, `/tsla-scan` stops sizing and
says so. Re-ratification is the owner's, not the process's.

### 3b. `MAX_CONCURRENT` is 1, and it is derived

`CLAUDE.md` §5: *"Correlated positions are one bet."* In a single-name process
every position shares one underlying, so the correlation rule collapses the
concurrency limit to one. A second TSLA contract is **adding to a position**,
not opening a new trade, and it is sized as one combined risk against
`MAX_TRADE_RISK_USD`.

This is not a conservative choice layered on top. It is what §5 already says,
applied to a one-name universe.

### 3c. The stop requirement is now an independent rule

`CLAUDE.md` §5 makes the premium cap conditional on a resting stop, and it
enforces that through arithmetic: unstopped premium counts as full risk, which
then breaks the 4%-of-equity cap.

**At `MAX_TRADE_RISK_USD = 450` that mechanism no longer bites.** Any contract
inside the $400 premium cap also sits inside a $450 risk cap even with no stop
at all, so the arithmetic stops forcing anything.

The rule is therefore restated here as a hard rule in its own right:

> **No TSLA card ships without a resting stop.** Not "planned", not
> "I'll watch it" — resting, placed by the human at entry. A card whose stop is
> not resting is not a live card, regardless of what the sizing arithmetic
> permits.

This is not a new restriction. It preserves what §5 intended once the number
that used to enforce it stopped doing so.

### 3d. What actually binds, in practice

Measured against the 2026-08-24 chain at Friday's close (spot 362.86, ATM 365C
mark $3.125, Δ 0.426):

- A structurally honest stop — beyond a mapped 5-min level, roughly $3 of TSLA
  movement — is about **$1.29 on the option = $129 risk per contract.**
- $450 / $129 → 3 contracts by risk.
- 3 × $312.50 = $937.50, which **breaks the $400 premium cap**, and also the
  $1,252.65 buying power.
- **So the operative trade is 1 contract: ~$312 premium, ~$129 risk (10.2% of
  equity).** The premium cap and buying power bind first; the risk cap has
  slack.

Write this out on every card rather than reasoning it again each morning.

---

## 4. What transfers from the playbook, and what does not

The playbook's dated behaviours were validated on SPY and QQQ. Transfer is a
claim requiring evidence, so each is marked.

**Transfers — structural, not instrument-specific:**

- The four-step hierarchy (environment → location → confirmation → execution).
- The five candle patterns; wicks are rejections, bodies are decisions.
- Retest-over-breakout.
- Write the invalidation before entry.
- Grade execution, not P&L.
- Price action overrules flow when they disagree.
- Skip the headline candle on events.

**Transfers with a TSLA-specific number that must be re-measured — provisional
until live sessions confirm it:**

- **Volume participation floor.** SPY's ~100K / QQQ's ~60K are feed-specific
  and meaningless on TSLA. `DATA_LAYER-TSLA.md` §5 carries a measured TSLA
  distribution and a provisional floor. It is measured, **not validated**.
- **The 15-cent stop-limit buffer.** TSLA options tick in **$0.05 above $3.00**
  (`min_ticks.above_tick`), so 15 cents is exactly 3 ticks — coherent. Below
  $3.00 the tick is $0.01 and 15 cents is 15 ticks, which is loose. Buffer is
  therefore tick-aware, not fixed.
- **The 5% spread liquidity gate.** SPY near-money runs ~0.6%; TSLA near-money
  ran **4.8–6.6% at Friday's close** and ITM strikes ran 11–15%. The gate is
  near-binding on TSLA rather than generous, and closing spreads are not
  intraday spreads — this needs a live RTH re-probe before it is trusted.

**Does not transfer — do not assume:**

- **GEX regime behaviour.** The playbook's glue/gasoline read is dated on SPY.
  TSLA is a mega-chain name where GEX is meaningful in principle, but no TSLA
  regime read in this repository has ever been checked against an outcome.
- **Time-of-day statistics.** "All wins entered 9:49–12:31" is a SPY sample of
  one session. TSLA's own intraday shape is unmeasured here.
- **Tide tripwires.** Thresholds (±$40M) are market-wide UW numbers, not
  per-ticker. A TSLA `net-prem-ticks` equivalent needs its own calibration, and
  currently cannot even be pulled — see §5.

---

## 5. The Unusual Whales layer is dark

**As of 2026-08-22, no UW API key is present in this environment.**
`UNUSUAL_WHALES_API_KEY` is unset; a probe returned `authentication_required`.

UW is the sole source for dealer gamma (`gex-levels`), signed aggressor-side
flow, the tide, and vendor IV rank. Without it:

- **Edge test E3 (dealer mechanics) cannot run at all.**
- **E2 (flow divergence) cannot run at all.**
- E1 (vol mispricing) runs in degraded form: Robinhood gives per-contract IV,
  but `iv_rank`, `variance-risk-premium` and the term structure are UW's.
- The regime gate has no input. It reports `NA_unresolved` — **not "neutral"**,
  which would be a fabricated reading.

`/tsla-scan` must state this at the top of every run while it holds. A process
that quietly drops two of its five edge tests and still prints a score is
exactly the failure `CLAUDE.md` §3 exists to prevent.

Restoring it is a key in the environment, nothing more. Until then this module
is running on two of three data legs.

---

## 6. Calibration status

**Everything in this module is `UNCALIBRATED`,** and it starts from further back
than `options-expert/` does, because:

1. `options-expert/`'s tests were reasoned but at least exercised once, on
   SPY/QQQ, in `log/2026-08-18-REPLAY-TEST.md`.
2. **None of them has ever been run on TSLA.** Single-name behaviour, TSLA's
   spread profile, its 3-day expiry cycle and its 3.26% average daily range are
   all different enough that the SPY exercise transfers nothing quantitative.
3. The TSLA-specific numbers in `DATA_LAYER-TSLA.md` are **measured from ten
   sessions of price data**, which makes them factual about the past and
   silent about whether trading on them works.

The path off `UNCALIBRATED` is `tesla/log/`: every card records its inputs
**before** the outcome is known, and Robinhood `get_option_historicals` returns
real OHLC on the contract, so a card can later be graded against the actual
mark. `/tsla-close` is the command that does it. Skipping it is what keeps the
process permanently uncalibrated.

Per `CLAUDE.md` §9, state what a test should show before running it. The first
live sessions are pre-registered in `tesla/log/` as they happen, not
reconstructed afterwards.

---

## 7. Session shape

| Command | When | What it does |
|---|---|---|
| `/tsla-open` | 9:05–9:25 ET | DTE map, levels, catalysts, IV read, two written triggers |
| `/tsla-scan` | after 9:45, on demand | edge tests → a sized card or a kill count |
| `/tsla-watch` | while a position is open | levels, tripwires, the 3:30 clock |
| `/tsla-close` | after 3:30 ET | outcome vs pre-recorded inputs, grade, journal |

Each is a spec in `.claude/skills/`. They read this charter and the data layer;
they do not restate them.

**No command in this module places, modifies, or cancels an order.**
