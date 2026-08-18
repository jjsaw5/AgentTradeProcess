# Options Expert — Data Layer

What the three connections can actually deliver, verified by probe rather than
assumed from documentation. This file is the ground truth the expert spec is
built on: **if a capability is not listed here as verified, the expert may not
assume it exists.**

**Verified:** 2026-08-18, ~15:50 ET (market open), from the Claude Code remote
session container.
**Re-verify with:** `tools/probe_fmp.sh` (FMP). Robinhood was probed by hand
through the MCP connector; UW is unprobed — see §3.

A capability's presence here is a claim about *this key on this date*. Plans
change and endpoints get deprecated mid-flight; the FMP legacy API died on
2025-08-31 and that is exactly how a spec silently rots. Re-run the probe
before trusting this file after a plan change.

---

## 0. The headline findings

Four things change how the expert has to be designed. They are here rather than
buried below because each one invalidates an obvious-looking design.

1. **FMP serves no options data whatsoever.** `options-chain` and
   `options/quote` both 404. Every strike, greek, IV and open-interest number
   must come from Robinhood. FMP is the *context* layer (price, news, macro,
   calendars), never the *contract* layer.
2. **FMP's legacy `/api/v3/*` API is dead for this key** — HTTP 403,
   "Legacy Endpoint … only available for legacy users … prior August 31, 2025."
   Only `https://financialmodelingprep.com/stable/*` works. Most FMP examples
   on the internet are v3 and will fail. Write `stable` paths only.
3. **Robinhood supplies real greeks, IV, OI and volume per contract.** This is
   a vendor-supplied greek, not one we model — so it is labeled
   `greeks_source: robinhood`, and it is *not* subject to the "modeled is
   labeled" caveat that applies to a Black-Scholes value we compute ourselves.
4. **Unusual Whales is not connected.** No key in this environment. Everything
   the daily brief attributes to UW — flow, net premium tide, GEX, dark pool,
   IV rank — is currently **unavailable to the expert**. §3 covers what that
   costs and what can be reconstructed without it.

---

## 1. FMP — verified `stable` endpoints

54 of 60 probed paths returned 200. Base URL: `https://financialmodelingprep.com/stable/`.
Auth: `?apikey=$FMP_API_KEY` (env var; never inline a key in a file or a log).

### 1a. Freshness — this is a real-time plan

Confirmed live during market hours, not delayed:

- `historical-chart/5min?symbol=SPY` returned a bar stamped `2026-08-18 15:45:00`
  at 15:50 ET — i.e. the bar in progress.
- `aftermarket-quote?symbol=SPY` returned a two-sided quote (`bidPrice` 767.75 /
  `askPrice` 767.77) with a millisecond timestamp seconds old.

This matters: intraday bars are usable as a live decision feed, not just for
post-hoc study. It also means **a stale timestamp is a signal, not noise** —
always read `timestamp`/`date` off the payload rather than assuming freshness.

### 1b. Price and bars

| Endpoint | Returns | Use |
|---|---|---|
| `quote?symbol=` | price, change%, day H/L, year H/L, 50/200-day avg, volume, open, prevClose, timestamp | one-shot underlying snapshot; prevClose + day H/L feed the PDH/PDL/PDC lines |
| `batch-quote?symbols=` | same, comma-separated list | whole watchlist in one call — prefer this over N single quotes |
| `quote-short?symbol=` | price/change/volume only | cheap polling |
| `aftermarket-quote?symbol=` | bid/ask + sizes + ms timestamp | **the only bid/ask FMP gives**; spread and quote-imbalance reads; works pre/post market |
| `aftermarket-trade?symbol=` | last price, trade size, ms timestamp | last-print tape |
| `batch-aftermarket-quote?symbols=` | batched bid/ask | premarket range building across the watchlist |
| `historical-chart/{1min,5min,15min,1hour}?symbol=` | OHLCV bars | 5-min is the playbook's decision chart; 1-min is execution timing; volume drives the participation floor |
| `historical-price-eod/{full,light}?symbol=` | daily OHLCV (+ VWAP/change in `full`) | PDH/PDL/PDC, ATR, realized vol, gap statistics |

### 1b-2. Index symbols — partly gated

Index quotes go through the same `quote?symbol=` path with a URL-encoded caret
(`%5EVIX`). Verified 2026-08-18:

| Symbol | Result |
|---|---|
| `^VIX` | 200 — CBOE Volatility Index, full quote (15.79 at test time) |
| `^GSPC` | 200 — S&P 500 cash index, with index volume |
| `^NDX` | **402** — not on this plan |
| `^VIX9D` | **402** — not on this plan |
| `^VVIX` | **402** — not on this plan |

Consequence: **VIX term structure is unavailable from FMP.** VIX9D/VIX (the
short-dated-vol-vs-30-day read that tells you whether the market is pricing an
event into *this week* specifically) needs Robinhood's index tools or UW. NDX
likewise comes from Robinhood `get_indexes`/`get_index_quotes`, not FMP.

Note `^VIX` returns `volume: 0` — the index itself does not trade. Never use
that field as a participation signal.

### 1c. Movers, breadth and sector rotation

`biggest-gainers`, `biggest-losers`, `most-actives`,
`sector-performance-snapshot?date=`, `industry-performance-snapshot?date=`,
`sector-pe-snapshot?date=`, `historical-sector-performance?sector=`.

Sector snapshot returns `{date, sector, exchange, averageChange}` across 11
sectors — enough to answer the playbook's "broad or narrow?" breadth question
without scraping anything.

### 1d. Calendars and macro

`economic-calendar?from=&to=`, `earnings-calendar?from=&to=`,
`earnings?symbol=`, `treasury-rates?from=&to=`, `economic-indicators?name=`,
`exchange-market-hours?exchange=`, `dividends-calendar`, `splits-calendar`,
`ipos-calendar`.

- `treasury-rates` returns the full curve (1M→30Y) per date — real yield-curve
  context and a genuine 2s10s slope, not a proxy.
- `exchange-market-hours` returns `isMarketOpen` — use it as the session gate
  instead of hand-rolling a holiday calendar.

### 1e. News and narrative

`news/stock?symbols=`, `news/stock-latest`, `news/general-latest`,
`news/press-releases?symbols=`, `fmp-articles`.

`historical-social-sentiment` **404s** — there is no social-sentiment feed on
this plan. The brief's §10 "internet is talking about" section cannot be sourced
from FMP; it needs web research or UW.

### 1f. Analyst and estimates

`price-target-news?symbol=`, `price-target-summary?symbol=`,
`grades-latest-news`, `grades-consensus?symbol=`, `ratings-snapshot?symbol=`,
`analyst-estimates?symbol=&period=`.

### 1g. Fundamentals and context

`profile?symbol=`, `key-metrics-ttm?symbol=`, `ratios-ttm?symbol=`,
`shares-float?symbol=`, `sp500-constituent`,
`company-screener?<filters>`.

`shares-float` is the float number the squeeze-radar math needs.

### 1h. Technical indicators (server-side)

`technical-indicators/{rsi,ema,sma,standarddeviation,adx}?symbol=&periodLength=&timeframe=`

`timeframe` accepts intraday values (`5min` confirmed). `standarddeviation` is
the useful one here — it is the realized-vol input for an IV-vs-RV comparison,
which is the closest available substitute for a real IV rank (§3).

### 1i. Positioning

`insider-trading/latest`, `commitment-of-traders-report?symbol=`,
`commitment-of-traders-analysis?symbol=`, `etf/sector-weightings?symbol=`.

COT works on futures symbols (`ES` confirmed) — weekly, lagged, positioning
context only. Not an intraday input.

### 1j. Blocked on this plan — do not design against these

| Path | Code | Meaning |
|---|---|---|
| `options-chain`, `options/quote` | 404 | FMP serves no options data at all |
| `historical-social-sentiment` | 404 | no social feed |
| `quote?symbol=^NDX` / `^VIX9D` / `^VVIX` | 402 | index symbols gated; no VIX term structure |
| `etf/holdings` | 402 | payment required — higher tier |
| `institutional-ownership/symbol-positions-summary` | 402 | higher tier |
| `earnings-surprises-bulk` | 402 | higher tier (per-symbol `earnings` works) |

402 is a plan ceiling, not an outage. If any of these become load-bearing the
answer is a tier upgrade, not a workaround that fabricates the number.

---

## 2. Robinhood — verified via MCP connector

**Access is read-only. The expert never places, modifies, or cancels an order.**

### 2a. Options — the contract layer

- `get_option_chains(underlying_symbol)` → chain id + every expiration.
  SPY confirmed carrying **0DTE plus daily expirations** (2026-08-18, 08-19,
  08-20, 08-21, 08-24 …) out to 2028. Also returns `settle_on_open` (AM/PM
  settlement) and `sellout_time_to_expiration`.
- `get_option_instruments(chain_symbol, expiration_dates, strike_price, type)`
  → contract UUIDs.
- `get_option_quotes(instrument_ids[])` → **the payload that makes this whole
  project possible.** Per contract: `bid_price`/`ask_price` + sizes,
  `mark_price`, `adjusted_mark_price`, `implied_volatility`, `delta`, `gamma`,
  `theta`, `vega`, `rho`, `open_interest`, `volume`, `break_even_price`,
  `chance_of_profit_long`/`_short`, `previous_close_price`, and `updated_at`.
  Paired with the official prior-session `close`.
- `get_option_historicals(instrument_ids[], start_time, interval)` → OHLC bars
  on the *contract itself*. This is what makes a recommendation checkable after
  the fact against the real mark, rather than against a modeled price.

Sample, SPY 768C exp 2026-08-19, taken 15:51 ET with SPY at 767.78:
`bid 1.64 / ask 1.65`, `IV 0.1090`, `delta 0.4806`, `gamma 0.0902`,
`theta -0.9038`, `vega 0.1614`, `OI 229`, `volume 51,164`.

**Access cost — a real design constraint.** `get_option_instruments` filtered by
an exact `strike_price` returns exactly 2 contracts (call + put) and is cheap.
Unfiltered, it returns **100 contracts per page starting from the lowest strike**
(SPY 2026-08-21 calls began at strike 360) and paginates by cursor. Walking a
full SPY chain that way costs enormous context for strikes nobody will trade.
**Rule: never call it unfiltered from the default cursor.** Two access patterns
work:

- *By explicit strike* — `strike_price=768.0000` returns exactly the call and
  the put. Cheap, exact, ~1 call per strike.
- *By crafted cursor (verified 2026-08-18)* — the pagination cursor is base64 of
  `p=<strike>`, and a hand-built cursor seeks straight to that strike. Passing
  `cD05MDAuMDAwMA==` (= `p=900.0000`) to SPY 2026-08-19 calls returned strikes
  905→950 and nothing below. So `base64("p=744.0000")` opens a page at the money
  and one page of 100 covers the whole tradable window.

That second pattern is the one to build on: a full near-money chain for an
expiration costs **2 calls** (one per option type), not ~90. Sequence is
`get_option_chains` → crafted-cursor `get_option_instruments` → batched
`get_option_quotes`.

### 2b. Underlying and account

Available but not individually re-probed this session (the brief already uses
them): `get_index_quotes`/`get_index_historicals` (SPX, NDX, VIX),
`get_equity_quotes`/`get_equity_historicals`, `get_equity_price_book` (level 2),
`get_equity_technical_indicators`, `get_equity_fundamentals`,
`get_earnings_calendar`/`get_earnings_results`, `get_option_positions`,
`get_equity_positions`, `get_portfolio`, `get_realized_pnl`,
`get_pnl_trade_history`, watchlists and scanners.

`get_portfolio` + `get_option_positions` are what let the expert size a
recommendation against real account equity and real existing heat, instead of
against a number someone typed into a config file.

---

## 3. Unusual Whales — NOT CONNECTED

`UNUSUAL_WHALES_API_KEY` is unset in this environment and no `.env` exists here.
**No UW endpoint has been probed. This section is a statement of absence, not a
capability list.**

### 3a. What is actually lost

The daily brief leans on UW for things nothing else here provides:

| Capability | Reconstructable? |
|---|---|
| Options flow — sweeps, blocks, ask/bid-side aggression | **No.** Needs trade-level tape with venue and aggressor side. Nothing in FMP or Robinhood exposes it. |
| Net premium tide (the §4 tripwires) | **No.** Same reason — it is an aggregation over signed trades. |
| Dark pool prints | **No.** |
| GEX / gamma walls / flip zone | **Partly — see 3b.** |
| IV rank / IV percentile | **Weak proxy only.** No IV history source. FMP `standarddeviation` gives realized vol, so IV-vs-RV is available; that answers "is IV rich vs recent movement" but *not* "where does IV sit in its own year." Not the same statistic — do not label a proxy as IV rank. |

### 3b. GEX is reconstructable, and that is worth knowing

Robinhood returns `gamma` **and** `open_interest` per contract. Dealer gamma
exposure per strike is therefore computable directly:

```
GEX(strike) ≈ gamma × open_interest × 100 × spot² × 0.01
              summed with calls positive and puts negative
```

over a spot-anchored strike window, which is exactly the cheap per-strike query
pattern §2a allows (~40–60 strike calls for a ±3% SPY window). That yields the
per-strike profile the playbook's regime gate needs: the walls, the sign, and
the approximate flip zone.

Three honesty caveats, all load-bearing:

1. The call-positive/put-negative convention is the standard *assumption* about
   dealer positioning, not a measurement. It is wrong in specific names where
   the customer base is net short calls. Label the output
   `gex_source: reconstructed_from_oi`, never as a vendor GEX print.
2. Open interest is **T-1** — it updates overnight. Same-day 0DTE positioning
   is invisible to it. On expiration day this is a serious limitation, which is
   precisely the day GEX matters most.
3. It has not been built or validated against a UW GEX print. Until it is, it is
   **UNCALIBRATED** and must display as such.

### 3c. What the expert must do meanwhile

Every flow-derived confirmation in the playbook (§1c "flow confirmation",
§4 tide tripwires) currently has **no data source**. The expert must report
those as `NA_no_data` and must not silently drop the confirmation step or
substitute a proxy for it — a setup that would have required flow confirmation
is a setup graded without it, and it says so.

---

## 4. Gaps, stated plainly

| Gap | Consequence | Fix |
|---|---|---|
| No UW key | No flow, no tide, no dark pool, no vendor GEX, no IV rank | Provide `UNUSUAL_WHALES_API_KEY`; then probe and extend this file |
| No IV history anywhere | IV rank/percentile impossible; only IV-vs-RV | UW, or persist our own daily IV snapshots going forward |
| OI is T-1 | Reconstructed GEX blind to same-day 0DTE positioning | Unavoidable without intraday OI; state it on every GEX output |
| No social sentiment | Brief §10 unsupported by any API here | Web research, or UW |
| FMP 402 tier ceiling | No ETF holdings / institutional ownership / bulk surprises | Tier upgrade if they become load-bearing |
