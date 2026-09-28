---
name: odte-desk
description: The live intraday research desk for 0DTE index and single-name option plays. Reads the day's brief and day-plan cards, the live tape (Unusual Whales, FMP, Robinhood) and the owner's Robinhood chart screenshots; answers "is this the trigger, which direction, and where do we get out" with exit points on the STOCK, plus the derived contract mark at each exit. Never sizes, never places orders.
---

# 0DTE DESK — the intraday research layer

**Created 2026-09-28 (owner-directed). Status: UNCALIBRATED** (`CLAUDE.md`
§7) until `odte-desk/log/` holds 20 graded frames. This module fills the hole
between 9:45 and 3:30: the brief (9:05) and the day plan (9:28) are pre-open
products, and until today nothing in this repository owned the session itself.

**Read-only. The desk never places, modifies, or cancels an order** (`CLAUDE.md`
§2). It frames decisions; the owner executes every one.

**The desk does not size.** Owner decision 2026-09-28: the desk outputs
direction, the trigger, the invalidation, and the exit points on the underlying,
with the derived contract mark at each. Contract count, dollar risk and whether
a trade fits `CLAUDE.md` §5 are the owner's call at the ticket. The desk prints
the §5 caps once per session in the header and never again.

**The 0DTE gate prints a warning; it does not refuse.** Owner decision
2026-09-28. `options-expert/SKILL.md` Stage 4 says 0DTE is only in gasoline
regime, only with confirmation, only in the prime window. When a frame violates
that gate, or the owner's one-loss rule (playbook §6, 2026-09-22), the event
gate, or the volume floor, the desk still frames the trade and prints the
warning in a fixed `GATES` block. A gate is never silently dropped and never
buried in prose.

---

## 1. Inputs, in priority order

| Input | Where | What the desk takes from it |
|---|---|---|
| Today's brief | `briefs/YYYY-MM-DD.md` (the version on disk; record its commit hash) | §0 lines, §3 event times, §8 walls and regime, §9 triggers, §13 unknowns |
| Today's day-plan card | `day-plan/cards/YYYY-MM-DD.md` + addenda | the written triggers, invalidations, targets, windows, DO-NOTHING-IF, one-loss status |
| **Pattern input** | *slot reserved* — the edge-pattern tool's output, once its location and format are recorded here. Until then the day-plan cards (which are options-expert cards) fill the slot. | the pattern name, the level it keys off, its own invalidation |
| Owner's chart screenshots | pasted in chat (Robinhood charts) | §4 chart-read protocol |
| Live tape | UW, FMP, Robinhood per `options-expert/DATA_LAYER.md` | §3 pull list |
| Owner's fills today | Robinhood `get_option_orders` (filled, since 9:30) and `get_option_positions` | one-loss rule status, open position to frame exits for |
| The scoring DB | `brief-review/DATA_STORE.md` | prior outcomes of the same trigger shape, when queryable |

The brief and the card are a snapshot. Every level the desk quotes is re-read
live before it is quoted; a 9:05 gamma wall is not a 1:00 gamma wall.

The pattern-input slot exists so that the tool's output enters through one
named door with its provenance recorded, instead of arriving as untracked
instruction (`CLAUDE.md` §0).

---

## 2. When it runs

**Scheduled** (owner decision 2026-09-28: both scheduled and chat-driven):

| Clock (ET) | Frame |
|---|---|
| 9:35 | Opening range mark: ORH/ORL from the first 5-minute candle (playbook §0a), gap status of every card level (live / gapped-past per I-8), volume floor armed from the first completed bars. **No trade frames before 9:45** (I-14). |
| 9:45, then every :00 / :15 / :30 / :45 through 3:30 | Read the just-closed 15-minute candle against every written trigger and invalidation. Frame anything that fired. Say "nothing fired" when nothing fired. |
| 3:00 | Flat-deadline bell for every card that says 3:00. |
| 3:30 | The real 0DTE bell (playbook §1d). Whatever exists at 3:30 is the result. Robinhood force-closes at 3:45. |

The 15-minute close is the verdict candle because that is what every card in
`day-plan/cards/` is written against. The 5-minute chart is the decision chart
(playbook §1c); the desk reads 5-minute closes when the owner asks or when a
card's trigger is written on them, and says which it is reading.

**Chat-driven:** the owner asks at any time ("SPY just closed above 768, what's
the play", "here's my chart, is this the retest", "where do I get out of my
QQQ 738P"). Same output block, same log entry. The desk answers with a frame
or with "no trade, here's why" and treats the second as a first-class answer.

Doldrums (roughly 1:00–2:30, no scheduled catalyst) and power hour (3:00–3:30)
are named in every frame's `GATES` block when they apply.

---

## 3. Live pulls

Per frame, in this order. Every endpoint below is verified in
`options-expert/DATA_LAYER.md`; nothing else may be assumed to exist.

1. **Price and candle.** FMP `historical-chart/5min` and `/15min` for the name
   (Robinhood `get_equity_historicals` as the second opinion). Read the
   timestamp; the bar in progress is not a close.
2. **Regime, live.** UW `gex-levels` (`call_wall`, `put_wall`, `gamma_magnet`,
   `gamma_flip`) for SPY, QQQ and the name. Never sum strikes; if the per-strike
   profile is pulled, `limit=500` and assert it brackets spot (§3e).
3. **Tide and direction.** UW `market-tide` (5-minute bars) and per-name
   `net-prem-ticks` (`net_delta`). Playbook §4 tripwires A/B/C read here.
4. **Vol.** UW `volatility/term-structure` (the 0DTE row's `implied_move` and
   `implied_move_perc` are the session's expected range), `volatility/stats`
   for `iv`, `rv`, `iv_rank`. FMP `^VIX`.
5. **Contract.** Robinhood `get_option_chains` → crafted-cursor
   `get_option_instruments` → `get_option_quotes` for the strike the frame
   names: `mark_price`, bid/ask, `delta`, `gamma`, `theta`, `vega`,
   `implied_volatility`, `open_interest`, `volume`, `updated_at`. Robinhood is
   the tradable mark; UW is never quoted as the fill.
6. **The stream.** `options-expert/tools/uw_stream.py` (wired for the desk
   2026-09-28) runs for the session with the day's tickers and any held
   contracts, and appends one JSON line per 15-minute boundary to a frame
   file:

   ```
   python options-expert/tools/uw_stream.py --tickers SPY,QQQ \
       --contracts <OCC symbols of held/candidate contracts> \
       --frame-file <scratch>/stream-YYYY-MM-DD.jsonl
   ```

   Each frame line carries: `price` (last and cumulative volume per ticker,
   basis UNVERIFIED), `gex` (live aggregate gamma/delta/charm/vanna per 1%
   move, `_oi`/`_vol`/`_dir`, ms-stamped), `tide`, per-contract `contracts`
   (prints, ask-side vs bid-side counts and premium, NBBO mid drift, last
   price, volume, OI, big prints), every `headline` since the last frame,
   `halts`, and the stream's own `rx`/`dropped` counters. The scheduled read
   takes the **last line** of the file; if `dropped` is non-zero the frame
   says so. Live it also prints `BIG PRINT`, `GEX FLIP`, `HALT`, `TRUTH` /
   `MACRO` / `HELD` headline lines and the playbook tripwires as they fire.
   A halt on a name the owner holds is always the first line of the frame.
   Without the stream, fall back to REST `news/headlines` (`is_major`) and
   `gex-levels`, and say the intraday freshness is UNVERIFIED.
7. **Owner state.** `get_option_positions`; `get_option_orders` filled since
   9:30. Position snapshots are never evidence of no trades (R-3).

Handling rules carry over unchanged: `data: []` is `NA_unresolved` until
re-requested with known-good parameters; absent stays absent; every greek
carries its source; a stale timestamp is reported as stale.

---

## 4. Chart-read protocol (Robinhood screenshots)

The owner trades off Robinhood charts and will paste them. A screenshot is the
owner's view of the tape, and the desk reads it as **interpretation, never as
data.** The feed is the record; the picture is the question.

For every chart the owner pastes, the desk:

1. **States what it sees:** ticker, timeframe (1-min / 5-min / 15-min / daily),
   the last price and time visible, whether the chart is regular hours or
   extended, any overlay drawn (VWAP, moving averages, the owner's own lines).
   If the timeframe cannot be read off the image, ask; do not guess.
2. **Reads the structure against the playbook's five candle patterns**
   (§1c: rejection wick, failed breakdown/trap, real breakdown, real breakout,
   first-move-fake) and names which one, if any, the last two completed
   candles form. Wicks are rejections; bodies are decisions. The candle in
   progress is never a signal.
3. **Reads levels off the image** only where a line is drawn or an obvious
   swing high/low is visible, and then **checks each one against the feed**
   (FMP bars, brief §0 lines, card levels). Output lists every level with its
   provenance: `[image]`, `[feed]`, or `[both]`. A level that exists only in
   the image and is not within a few cents of any feed level is reported as
   `[image only — UNVERIFIED]`.
4. **Says what the chart cannot tell it:** Robinhood's volume bars undercount
   the consolidated tape (playbook §1c), the chart does not show dealer
   positioning, flow or IV, and a screenshot has no timestamp of its own; the
   desk uses the last visible candle's time and says so.
5. **Answers the owner's actual question** about the chart (is this the
   retest, is this the trap, did it confirm) with a yes / no / not yet, the
   candle that would settle it, and the level that would say no.

The desk does not draw its own charts. When a number matters, it prints the
number.

---

## 5. Framing a trade

A frame is produced when a written trigger fires on a closed candle, or when
the owner asks. The frame is built from the card that owns the trigger; if no
card owns it, the desk says so (`NOT ON A CARD`) and frames it against the
brief's §0 lines with that label on every line.

### 5a. Direction

Direction comes from **price**: the closed candle through the level, or the
successful retest of a broken level (retests over breakouts, playbook §1c).
Flow (`net_delta`, tide, sweeps) is confirmation or veto, never the trigger
(playbook §0). When SPY and QQQ disagree, or the name fires without the index
on the same side, the frame says `HOLLOW` and explains.

### 5b. Exit points on the stock — the product

Every frame names, on the **underlying**:

| Line | What it is | Where it comes from |
|---|---|---|
| `ENTRY` | the trigger candle's close and the level it closed through | the card / brief; live candle |
| `INVALIDATION` | the underlying price at which the idea is wrong; written before entry or it does not exist (playbook §0) | the card's opposite level, or the retest-failure point |
| `T1` | the first structural level in the trade's direction: nearest wall, PDH/PDL, ORH/ORL, premarket high/low, gamma magnet, round number, whichever is nearest | brief §0/§8, card, live `gex-levels` |
| `T2` | the next structural level beyond T1 | same |
| `RANGE BOUND` | the far edge of the session's expected range from the 0DTE `implied_move` (UW term-structure, live), measured from the current spot. A target beyond this is a tail; say so. | UW |
| `TIME EXITS` | the card's flat deadline; 3:00; the 3:30 bell; any event window (§3 of the brief) that lands inside the hold | card, brief |
| `RE-ARM` | whether a fired invalidation can re-arm today (usually NO), and what would justify it | card |

T1 is the scale line (scorecard observation #7: every paid day-card resolution
scaled at its first target; every giveback sat in an unprotected stretch).
Per the rule adopted 2026-08-17, the frame says: **place the resting limit at
T1 the moment the ticket fills.**

### 5c. The contract, and the derived mark at each exit

The frame names one contract (expiry, strike, type) per the options-expert
Stage 5 liquidity gates (spread ≤5% of mark, OI ≥250, volume ≥100, delta
0.30–0.60 for directional longs; a failure is reported, not hidden). It then
prints the **expected contract mark** at `INVALIDATION`, `T1` and `T2`:

```
expected_mark(d, h) = mark + Δ·d + ½·Γ·d²  −  θ·(h / 6.5)
  d = underlying distance from spot to the exit level (signed)
  h = hours the desk expects the move to take, stated
  Δ, Γ, θ = Robinhood's greeks on the contract at frame time [source: robinhood]
```

This is **our arithmetic on the vendor's greeks, labelled `computed: ours`.**
It ignores the vega term (IV change over the hold) and gamma's own change with
spot, so on 0DTE near the money it is a floor for a fast move and an
overstatement for a slow one. Every frame prints the formula's inputs so the
evening review can grade the estimate against the real mark
(`get_option_historicals`). When IV is expanding (`rv > iv` in
`volatility/stats`, or the tide accelerating in the trade's direction) the
frame says the estimate is conservative; when the trade is a fade into glue it
says the estimate is generous.

Give the owner the number they will actually see on the ticket: the expected
**mark**, and the bid/ask spread at frame time so they know what a market exit
costs.

### 5d. Gates — printed, never dropped

```
GATES   0DTE:        <OK in gasoline+prime window | WARNING: glue regime |
                      WARNING: outside prime window | WARNING: 1DTE θ -xx%/day>
        ONE-LOSS:    <no index loss today | WARNING: index loss at hh:mm on a
                      glue day — owner's rule says done with the indexes>
        EVENT:       <none in window | WARNING: <print> at hh:mm — headline
                      candle rule, evaluate candles two and three>
        VOLUME:      <armed and met | WARNING: last two 5-min bars under floor>
        DOLDRUMS:    <n/a | WARNING: 1:00–2:30, no catalyst>
        REGIME:      <structure matches regime | WARNING: continuation in glue /
                      fade in gasoline>
        HEAT:        <open positions n · same-driver as this frame? yes/no>
        §5 CAPS:     (header only, once per session)
```

A frame with any `WARNING` still ships. The owner decided that. The desk's job
is to make the warning impossible to miss, not to make the decision.

### 5e. The frame block

```
### hh:mm ET — TICKER — <LONG|SHORT> — <trigger that fired, on which candle>

CARD          <day-plan card n | brief §9 #n | NOT ON A CARD>
              brief <hash> · card <hash>
DIRECTION     <long|short>  —  <the candle: close x.xx through level y.yy>
              index agrees: <yes|no|HOLLOW>  ·  flow: <confirms|diverges|NA>
CONTRACT      TICKER YYYY-MM-DD strikeC|P  (0DTE|nDTE)  mark x.xx  bid/ask  (spread x.x%)
              Δ x.xx Γ x.xxx Θ -x.xx V x.xx IV x.xx OI n vol n  [source: robinhood, hh:mm:ss]
              gates: <all pass | FAIL: which>
ENTRY         underlying x.xx  (trigger close)
INVALIDATION  underlying x.xx  → expected mark x.xx  [computed: ours]
T1            underlying x.xx  (<what it is>)  → expected mark x.xx in ~h  [computed: ours]
              RESTING LIMIT HERE the moment the ticket fills; scale half
T2            underlying x.xx  (<what it is>)  → expected mark x.xx in ~h  [computed: ours]
RANGE BOUND   x.xx / x.xx  (0DTE implied move ±x.xx%, UW hh:mm)
TIME EXITS    <card deadline> · 3:00 flat · 3:30 bell · <event window if any>
RE-ARM        <NO | YES if …>
GATES         <block from 5d>
WRONG IF      <the one observable that says the thesis failed before INVALIDATION prints>
UNKNOWN       <every NA_no_data / NA_unresolved / stale timestamp in this frame>
              all estimates UNCALIBRATED
```

Sizing does not appear in the block. If the owner asks the desk to size, the
desk points at `options-expert/SKILL.md` Stage 6 and the §5 caps and states
plainly that sizing is the owner's call by the owner's decision.

### 5f. Managing an open position

When the owner holds a contract (from `get_option_positions` or by telling the
desk), every scheduled frame re-reads that position's `INVALIDATION`, `T1`,
`T2` and `TIME EXITS` against the just-closed candle and reports one of:
`HOLD (nothing changed)`, `T1 PRINTED (scale half; floor to breakeven per
playbook §1d)`, `T2 PRINTED`, `INVALIDATION PRINTED (exit, no exceptions)`,
`TIME EXIT (hh:mm)`. It re-prints the expected marks with the fresh greeks.
The desk never moves an invalidation further away; it may only report that the
owner's own floor rule (breakeven-or-better once up meaningfully) has been
earned.

---

## 6. What "no trade" looks like

"No trade" is a complete answer and the desk gives it whenever any of these
holds, with the reason on one line:

- Nothing fired on a closed candle (the touch is not the trigger).
- The level was gapped past and has not been re-crossed (I-8).
- The candle is the 9:30–9:45 candle or an opening gap print (I-14).
- The candle is the headline candle of a scheduled print (playbook §2).
- Price is mid-range between the two written levels (playbook §1b: don't
  initiate mid-range).
- The name fired without the index on the same side, and the card requires it.
- The contract fails every liquidity gate at the strikes that make sense.

The desk still prints the levels that would change the answer, so the owner
knows what they are waiting for.

---

## 7. Logging — pre-registration

Every frame, scheduled or chat-driven, taken or not, is appended to
`odte-desk/log/YYYY-MM-DD.md` at the moment it is produced, with every input
value (spot, candle, greeks, implied move, regime levels, tide reading, the
brief and card hashes, the chart's provenance lines if a screenshot was read).
Append-only after the fact; a wrong frame gets a timestamped correction below
it, never an edit (`CLAUDE.md` §9).

The log is graded by `brief-review` at T+1 (owner decision 2026-09-28) on the
same basis as day cards: did `T1` / `T2` / `INVALIDATION` print after the
frame and inside its `TIME EXITS`, measured on the underlying; and the
**expected-mark error** (predicted vs the real contract mark at that moment,
via `get_option_historicals`). The rubric addition is PROPOSED as R-4 in
`brief-review/IMPROVEMENTS.md` and applies once the owner ratifies it; until
then the desk's log is written as if it were already graded, because that is
the only way it becomes gradeable.

Twenty graded frames is the calibration bar (`CLAUDE.md` §7). Chat-driven
frames the owner did not take are graded too: the desk is graded on what it
said, not on what was executed.

---

## 8. Data sources beyond `DATA_LAYER.md` §1–6 — probed 2026-09-28

The owner asked for suggestions, then for probes. Record:
`log/2026-09-28-PROBE.md` (expectations pre-registered, results appended);
verified items are now in `options-expert/DATA_LAYER.md` §7. Re-verify with
`tools/probe_desk.sh` and `tools/probe_ws.py`.

| Gap it closes | Source | Status (2026-09-28) | Desk use |
|---|---|---|---|
| "What happened the last n times this trigger shape fired" | the scoring DB (`brief-review/DATA_STORE.md`) | **unprobed** — token absent from the remote container | Query shape (untested): `SELECT date, ticker, grade, evidence FROM radar_items WHERE ticker=? AND grade IN ('CONF-PAID','CONF-FAILED') ORDER BY date DESC LIMIT 10`, and the same against the day-card table once its name is confirmed in `DATA_STORE.md`. Until run, the desk says `NA_unresolved` for the prior-outcome line. |
| Short-dated vol (VIX1D, VIX9D/VIX ratio, VIX3M) | **Cboe delayed-quote JSON** (no key) | **verified, ~15-min delayed** | Session header and every frame's `GATES` block: VIX1D vs VIX (below = no event priced into today; above = the day is the event). Labelled `cboe ~15m delayed hh:mm`. Robinhood serves VIX only; FMP 402s the rest. |
| Overnight range from the instrument that trades overnight | **FMP `ESUSD`** 5-min bars | **verified, ~10-min delayed** | 9:35 frame: overnight high/low from Sunday 18:00 / prior 18:00 to 9:30, labelled `ES` and converted to SPY only as a ratio with the ratio stated. **No NQ on this plan** (402). |
| Headline latency on a war-headline tape | **UW websocket `news`** | **verified live; wired** (`uw_stream.py`, frame `headlines`) | Every headline since the last frame is in the frame line; live print when it names a watched ticker, is a Truth Social post, or is ticker-less macro. |
| Who is hitting the bid in the strike the owner holds | **UW websocket `option_trades:TICKER`** filtered client-side to the contract | **verified live**, ~80 prints/s on SPY, median 30 ms | **wired** (`uw_stream.py --contracts`, frame `contracts`): prints, ask-side vs bid-side counts and premium, NBBO mid drift, last price, volume, OI, big prints ≥ $50k. |
| Intraday gamma freshness | **UW websocket `gex:TICKER`** | **verified live**, ms-stamped | **wired** (`uw_stream.py`, frame `gex`; live `GEX FLIP` line on a sign change). Aggregate gamma per 1% move (`_oi` / `_vol` / `_dir`) as the live regime cross-check on `gex-levels` (date-only). |
| Level 2 at the trigger level | **Robinhood `get_equity_price_book`** | **verified; 249 KB / 2 symbols** | Only through a top-n extractor: the five levels either side of the trigger and any level whose size is ≥5× its neighbours (a wall). Never pasted raw into a frame. |
| Auction results as they print | **TreasuryDirect JSON** (no key) | **verified** | 1:00 auction frames: high yield, bid-to-cover, indirect / dealer / direct **as a share of competitive accepted, denominator stated**. Bills use `highDiscountRate`. |
| Consolidated volume / VWAP | Polygon, Databento | **not connected** (reachable, no credential) | UW `price:TICKER.vol` is a candidate substitute, basis `UNVERIFIED`; not a floor input until compared to a known consolidated print. |

## 9. What this module refuses to do

- Size a trade, name a contract count, or state dollar risk (owner decision).
- Place, modify or cancel an order, or describe how to (`CLAUDE.md` §2).
- Drop a gate. Every warning prints every time it applies.
- Move an invalidation further from price after entry.
- Treat a screenshot as data, or an unread candle as a close.
- Answer a current market fact from memory (`CLAUDE.md` §3).
- Invent a driver. `NO CLEAR DRIVER FOUND` when nothing explains the candle.
- Quote a UW price as a fill, or a modelled mark as the market's.
- Frame an entry the card did not write without labelling it `NOT ON A CARD`
  (the 9/25 coached "failed bounce" entry is the reason this line exists).

---

## 10. What this module does not know

Stated on every session header, because they do not go away with more data:

- The expected-mark formula is ours, first-order, and ignores IV change. It is
  `UNCALIBRATED` until the log grades it.
- Robinhood greeks are the vendor's, unchecked against a second source.
- There is no intraday VWAP from any vendor; if VWAP is quoted it was computed
  from FMP bars by us, or read off the owner's chart and labelled `[image]`.
- No VIX term structure on this plan. The 0DTE implied move from UW stands in.
- The volume floor is Robinhood-feed-specific and was calibrated at VIX ~14.
- UW `gex-levels` exposes a date, not a time; intraday freshness is
  `UNVERIFIED` unless the stream is running.
- Nothing in this module has an out-of-sample record. Reasoned is not proven.
