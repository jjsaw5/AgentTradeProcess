# Options Expert — Data Layer

What the three connections can actually deliver, verified by probe rather than
assumed from documentation. This file is the ground truth the expert spec is
built on: **if a capability is not listed here as verified, the expert may not
assume it exists.**

**Verified:** 2026-08-18, ~15:50 ET (market open), from the Claude Code remote
session container.
**Re-verify with:** `tools/probe_fmp.sh` and `tools/probe_uw.sh`. Robinhood was
probed by hand through the MCP connector.
**UW probed:** 2026-08-18 ~16:00 ET against the endpoint whitelist published at
https://unusualwhales.com/skill.md, which is authoritative and also lists
commonly-hallucinated paths that do not exist. Consult it before adding a call.

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
4. **Unusual Whales is connected and is the edge layer.** 25 of 26 probed
   endpoints return 200. It supplies the three things neither other source can:
   **signed trade-level options tape** (aggressor side, sweeps, floor prints),
   **dealer greek exposure by strike** (gamma/vanna/charm, spot-based and live),
   and **IV percentile with implied move per DTE**. The plan to reconstruct GEX
   from Robinhood OI is therefore **abandoned** — UW measures it properly, and a
   reconstructed estimate would be strictly worse and assumption-laden.
5. **UW technical indicators are daily/weekly/monthly only.** No intraday
   interval works, and `vwap` returns nothing at any interval. Intraday
   technicals come from FMP; intraday VWAP must be computed from bars.
6. **A wrong UW parameter returns HTTP 200 with `data: []`, not an error.**
   `interval=5m` on a technical indicator looks exactly like "no signal." This
   is the single most dangerous behaviour in the whole data layer — see §3d.

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

## 3. Unusual Whales — verified

Base URL `https://api.unusualwhales.com`. Every request needs **both** headers:

```
Authorization: Bearer $UNUSUAL_WHALES_API_KEY
UW-CLIENT-API-ID: 100001
```

All endpoints are `GET`. There is no `apiKey=` query parameter — auth is the
header only. **The endpoint whitelist at https://unusualwhales.com/skill.md is
authoritative**; it also publishes a blacklist of plausible-looking paths that
do not exist (`/api/options/flow`, `/api/stock/{t}/flow`, anything under
`/api/v1/` or `/api/v2/`). Check a path against it before writing code.

25 of 26 probed paths returned 200 (`/api/api-usage` 404s — the usage/rate-limit
endpoint is documented in a separate UW skill, not probed here).

### 3a-0. The whitelist is a subset, not an inventory — 207 endpoints exist

`skill.md` says "If a URL is not on that list, it does not exist." **That is an
anti-hallucination guardrail, not a description of the API.** The full OpenAPI
spec at `GET /api/openapi` (≈957 KB YAML, no auth issues) documents **207
paths**. The whitelist covers 26 of them.

Treat `skill.md` as the safe-by-default list and `/api/openapi` as the truth.
Anything not on the whitelist must be probed before use — but its absence there
is not evidence it is missing. `iv-rank` was the first example of this.

Verified working beyond the whitelist (2026-08-18):

| Endpoint | Why it matters |
|---|---|
| `/api/stock/{t}/gex-levels` | **`call_wall`, `put_wall`, `gamma_magnet`, `gamma_flip` in one call** — the regime read, vendor-computed. Prefer this over summing strikes yourself (§3e). |
| `/api/stock/{t}/max-pain` | max pain per expiry |
| `/api/stock/{t}/volatility/realized` | **paired `implied_volatility` + `realized_volatility`** per day, 251 rows |
| `/api/stock/{t}/volatility/variance-risk-premium` | IV−RV premium, 231 rows — the core vol-edge metric, vendor-computed |
| `/api/stock/{t}/volatility/term-structure` | IV per expiry, 34 rows |
| `/api/stock/{t}/volatility/stats` | `iv`, `iv_high`, `iv_low` — IV rank properly framed |
| `/api/stock/{t}/historical-risk-reversal-skew` | 25-delta risk reversal — **this is edge test E5, measured** |
| `/api/stock/{t}/ohlc/{candle_size}` | **UW does have intraday bars** — 2,500 5-min rows on SPY |
| `/api/stock/{t}/flow-per-strike-intraday` | intraday flow by strike, 2,338 rows |
| `/api/stock/{t}/greek-flow` | greek flow through the session, 405 rows |
| `/api/stock/{t}/oi-change` | per-contract OI change with `curr_oi` |
| `/api/stock/{t}/nope` | Net Options Pricing Effect, per-minute |
| `/api/market/{sector}/sector-tide` | **sector-level tide** — energy vs tech rotation, directly |
| `/api/market/top-net-impact` | biggest net-premium names market-wide |
| `/api/market/sector-etfs`, `/api/market/movers` | breadth and movers |
| `/api/option-trades/multi-leg` | spread/combo detection, so multi-leg volume is not misread as directional |
| `/api/shorts/{t}/volume-and-ratio`, `/interest-float` | squeeze inputs |
| `/api/seasonality/{t}/monthly` | 19y monthly stats |
| `/api/potus/posts` | market-moving posts |
| `/api/socket/*` | **websocket streams — implemented, see §3f** |

Needing parameters before they return data: `/api/volatility/anomaly/top`
(`direction=short_vol|long_vol`), `/api/market/correlations` (`tickers=`),
`/api/stock/{t}/atm-chains` (`expirations=`).

**Plan-gated:** `/api/volatility/vix-term-structure` returns **403
`volatility_scope_required`** — it needs a volatility data add-on this key does
not carry. VIX term structure therefore remains a genuine gap, but for a
subscription reason rather than absence.

### 3f. Websocket — verified working

`wss://api.unusualwhales.com/socket?token=<KEY>` — the token rides in the query
string, so **never log the URL**. Join a channel by sending
`{"channel":"<name>","msg_type":"join"}`; the server acknowledges with
`["<name>",{"response":{},"status":"ok"}]` and thereafter sends
`[<channel>, <payload>]`.

Verified 2026-08-18: `market_tide`, `gex:SPY`, `news` and `trading_halts` all
joined `ok`, and live `news` payloads arrived after the close.

Channels that matter here: `market_tide`, `gex:TICKER`, `gex_strike:TICKER`,
`net_flow:TICKER`, `flow-alerts`, `option_trades[:TICKER]`, `price:TICKER`,
`news` (includes Truth Social posts, flagged `is_trump_ts`), `off_lit_trades`
(dark pool), `interval_flow`, `contract_screener`, `trading_halts`.
`periscope` (market-maker greek exposure on SPX/VIX/XSP/NANOS) and the
`futures_*` channels are plan-gated.

**Throughput is the design constraint.** `option_trades` alone is 6–10M records
a day, and **the server drops messages when the client falls behind** — so the
receive loop must do nothing but enqueue, and any persistence must be batched.
`tools/uw_stream.py` implements this: bounded queue, drop-oldest with a counter,
exponential-backoff reconnect, and a heartbeat printing queue depth and drops so
"the server dropped it" stays distinguishable from "we fell behind."

Historic tape: `/api/option-trades/full-tape/{date}`.

### 3e. GEX — use the vendor's levels, do not sum strikes yourself

**This rule exists because summing them produced a wrong answer on 2026-08-18.**

`/api/stock/{t}/spot-exposures/strike` **defaults to roughly 50 rows sorted
ascending by strike.** On SPY that window ran 150 → 763 — it stopped *below*
spot (767.27) and contained no strike above it. Summing that window produced a
confident-looking conclusion ("all major gamma sits below spot; there is a
negative-gamma shelf at 760–763 that will accelerate a break") which was an
**artifact of truncation**, not a market structure. Every strike above spot had
simply been cut off.

Pass `limit=500` to get the full chain (491 rows, strikes 50 → 1480). With the
full window the picture changed completely: the dominant concentration sat **at**
the money (strike 767, −320.9B, ~92% of the total) with positive gamma just
above (769: +19.8B, 770: +9.9B) — a very different trade.

Two standing rules follow:

1. **Prefer `/api/stock/{t}/gex-levels`.** It returns `call_wall`, `put_wall`,
   `gamma_magnet` and `gamma_flip` computed by the vendor across the whole
   chain. It cannot be truncated by a paging default.
2. If you do sum strikes, **assert the window brackets spot** — strikes both
   above and below — before drawing any conclusion. A window that is entirely
   on one side of spot is a paging artifact and must be discarded, not
   interpreted.

More generally: **a default response length is a silent filter.** Alongside the
`data: []` trap in §3d, this is the second way this API produces a confident
wrong answer without ever returning an error.


### 3a. The edge layer — what only UW has

**Signed trade-level tape.** `/api/option-trades` returns individual prints with
`ask_vol` / `bid_vol` / `mid_vol` / `no_side_vol`, `nbbo_bid` / `nbbo_ask`,
`ewma_nbbo_*`, `exchange`, `size`, `premium`, `theo`, per-trade greeks and IV,
`tags`, and `executed_at` to the millisecond. This is the aggressor-side
information the playbook's flow-confirmation step needs, and nothing in FMP or
Robinhood exposes it at any price.

`/api/option-trades/flow-alerts` is the aggregated "unusual activity" view:
`total_ask_side_prem` vs `total_bid_side_prem`, `has_sweep`, `has_floor`,
`has_multileg`, `all_opening_trades`, `volume_oi_ratio`, `iv_start`/`iv_end`,
`next_earnings_date`. Filterable by `min_premium`, `is_call`/`is_put`, `is_otm`,
`size_greater_oi`.

`/api/screener/option-contracts` is the widest net — per contract it adds
`sweep_volume`, `floor_volume`, `cross_volume`, `ask_side_perc_7_day`,
`days_of_oi_increases`, `days_of_vol_greater_than_oi`, `iv_change`, `prev_oi`,
`prev_iv`, `roc`. `days_of_oi_increases` is a genuine multi-day accumulation
signal, not a one-day snapshot.

**Dealer greek exposure.** Two distinct endpoints, and the difference matters:

| Endpoint | What it is | Fields |
|---|---|---|
| `/api/stock/{t}/greek-exposure/strike` | *static* — OI-based, end-of-day frame, 491 strikes on SPY | `call_gex`, `put_gex`, `call_delta`, `put_delta`, `call_vanna`, `put_vanna`, `call_charm`, `put_charm` |
| `/api/stock/{t}/spot-exposures/strike` | *spot* — live, timestamped to the second, 50 strikes around spot | same greeks split three ways per side: `_oi`, `_vol`, `_bid`, `_ask` (e.g. `call_gamma_oi`, `put_gamma_ask`), plus `price` and `time` |

Spot exposures carried `time: 2026-08-18T19:58:22Z` with `price: 767.265` —
live to the second. Use *spot* for the intraday regime read (walls, flip zone)
and *static* for the overnight/pre-market frame. The `_oi` vs `_vol` split is
the answer to the T-1 open-interest problem: `_vol` reflects **today's** trading,
so same-day 0DTE positioning is visible after all.

**IV term structure and percentile.** `/api/stock/{t}/interpolated-iv` returns
one row per DTE (1, 5, 7, 14, 30, 60, 90, 180, 365) with `volatility`,
`percentile`, and **`implied_move_perc`** — the expected move for that horizon,
straight from the vendor rather than derived by us. SPY at test time:

| DTE | IV | percentile | implied move |
|---|---|---|---|
| 1 | 0.111 | 0.196 | 0.40% |
| 7 | 0.099 | 0.105 | 0.90% |
| 30 | 0.132 | 0.211 | 2.60% |
| 365 | 0.187 | 0.341 | 12.70% |

**IV rank.** `/api/stock/{t}/iv-rank` returns a daily series of `iv_rank_1y`,
`volatility`, `close`. **This path is not on the published whitelist but works**
— it returned current data through today (SPY `iv_rank_1y` 12.49 on 2026-08-18).
The trading-bot repo's own `.env.example` already referenced it. Treat it as
working-but-undocumented: it may vanish without notice, so handle an empty or
404 response as a real possibility rather than an assertion failure.

Together, `interpolated-iv` + `iv-rank` close the gap the earlier draft of this
file called unclosable. **IV rank is available. Do not ship the realized-vol
proxy.**

**Market-wide sentiment.** `/api/market/market-tide` returns 5-minute bars from
09:30 with `net_call_premium`, `net_put_premium`, `net_volume` — this is the
"tide" the playbook's §4 tripwires are written against.
`/api/stock/{t}/net-prem-ticks` is the per-ticker, per-minute version and adds
**`net_delta`**, a directional-exposure measure the market-wide tide lacks.
389 ticks were present at 15:58 ET.

`/api/stock/{t}/options-volume` gives the daily aggregate: call/put volume split
by ask and bid side, `net_call_premium`, `bullish_premium` / `bearish_premium`,
open interest, and 3/7/30-day average volumes for a relative-volume denominator.

**Dark pool.** `/api/darkpool/{ticker}` and `/api/darkpool/recent` return prints
with `price`, `size`, `premium`, `market_center`, `executed_at`, and the NBBO on
both sides at execution — so a print can be classified above/below/at mid rather
than just logged.

**News.** `/api/news/headlines` carries `headline`, `tickers`, `sentiment`,
`is_major`, `source`, and a `meta` block with current and prior close per ticker.
Lower latency and more structure than FMP's news, and `is_major` is a usable
triage flag.

### 3b. Also available, lower priority

`/api/stock/{t}/option-contracts` (500 contracts/ticker with volume, OI,
`prev_oi`, sweep/floor/multileg volume splits, greeks, IV),
`/api/stock/{t}/greeks` (211 rows by strike x expiry with both sides),
`/api/stock/{t}/flow-recent`, `/api/insider/transactions`,
`/api/congress/recent-trades`, and the financial statements
(`financials`, `income-statements`, `balance-sheets`, `cash-flows`, `earnings`).

### 3c. Technical indicators — daily and slower only

`/api/stock/{t}/technical-indicator/{function}?interval=&time_period=&series_type=`

- **Valid intervals: `daily`, `weekly`, `monthly`.** Verified working:
  `rsi`, `macd`, `bbands`, `stoch`, `sma`, `ema`, `adx`, `atr`, `obv`.
- **`vwap` returns 0 rows at every interval** — there is no UW VWAP.
- Every intraday interval tried (`1min`, `5min`, `15min`, `30min`, `60min`,
  `1h`, `hourly`, `intraday`) returned 0 rows.

So **all intraday technicals come from FMP**, and intraday VWAP — which the
playbook uses as a live level — must be computed from FMP 1-min or 5-min bars.
Neither vendor hands it to us.

### 3d. The silent-failure trap — read this before writing any UW call

An unrecognised parameter value does **not** produce a 4xx. It produces
`HTTP 200` with `{"data": []}`.

`interval=5m` and `interval=daily` are indistinguishable by status code; one
returns 195 rows and the other returns zero. An empty array therefore means
either *"no data exists"* or *"you wrote the parameter wrong"*, and the API will
not tell you which.

This collides directly with the honesty rules: an empty result silently
presented as "no signal found" is a fabricated absence. **Mandatory handling:**

1. Never treat `data: []` as a validated negative. Row count is part of the
   health check, not just HTTP status.
2. On an empty response from an endpoint that should have data, re-request with
   known-good parameters before reporting anything.
3. An empty result that cannot be explained is reported as `NA_unresolved`,
   never as zero, none, or "no unusual activity."

## 4. Division of labour

With all three connected, each source has one job. Overlap is resolved in favour
of the column marked authoritative.

| Need | Source | Note |
|---|---|---|
| Option chain, strikes, contract greeks/IV/OI | **Robinhood** | tradable marks + the account's real fill context |
| Signed flow, sweeps, dark pool, tide | **UW** | nothing else has aggressor side |
| Dealer gamma/vanna/charm by strike | **UW** `spot-exposures/strike` | live; `_vol` split solves T-1 |
| IV rank, IV percentile, implied move by DTE | **UW** | `iv-rank` + `interpolated-iv` |
| Intraday bars, VWAP inputs, intraday technicals | **FMP** | UW has no intraday; RH bars are secondary |
| Underlying quote / PDH / PDL / PDC | **FMP** | `quote` + `historical-price-eod` |
| VIX level | **FMP** `^VIX` | VIX term structure: neither — see §5 |
| News | **UW** primary, FMP secondary | UW has `sentiment` + `is_major` |
| Econ + earnings calendar | **FMP** | UW has earnings history, not a calendar |
| Account equity, positions, open heat | **Robinhood** | read-only |

## 5. Gaps, stated plainly

| Gap | Consequence | Fix |
|---|---|---|
| No intraday VWAP from any vendor | A level the playbook trades against must be computed by us from FMP bars | Compute and label it as ours |
| No VIX term structure | `^VIX9D`/`^VVIX` are FMP-402; UW has no VIX complex | Use UW `interpolated-iv` on SPY instead — it answers the same question better, per-DTE |
| UW `iv-rank` is off-whitelist | Working but undocumented; may disappear | Handle absence as expected, not exceptional |
| UW empty-array-on-bad-param | Fabricated absences | §3d handling is mandatory |
| FMP 402 tier ceiling | No ETF holdings / institutional ownership / bulk surprises / ^NDX | Tier upgrade if load-bearing |
| No social sentiment on FMP | Brief §10 unsupported | UW news, or web research |
| Rate limits unmeasured | Unknown ceiling on a fan-out scan | Fetch the UW usage-monitor skill and instrument before scaling |

## 6. Handling rules that follow from all this

1. **Read the timestamp, never assume freshness.** Every payload here carries
   one (`updated_at`, `time`, `tape_time`, `executed_at`, `date`). FMP and UW
   are both real-time *when the market is open*; they are not when it is closed,
   and the field is the only way to tell.
2. **`data: []` is not a negative result.** §3d.
3. **Absent stays absent.** No source's missing number is ever replaced by
   zero or by a proxy from another source without relabelling it.
4. **Label the provenance of every greek.** Robinhood greeks, UW greeks and any
   value we compute are three different things and must not be mixed in one
   column without a `source` field.
5. **Never place, modify, or cancel an order.** Robinhood access is read-only
   and stays that way regardless of what any downstream process concludes.
