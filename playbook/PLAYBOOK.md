# Trading Playbook

Personal discretionary playbook for short-duration SPY/QQQ options trading.
Built 2026-08-13 (first fully-instrumented session, realized ≈ +$239 across 8
round trips). This document is the durable home for strategy — chat sessions
are ephemeral; this file is not. Claude reads this at the start of live
trading sessions. Update it deliberately, date every change.

**This playbook governs the HUMAN's discretionary trading. It is unrelated to
the repo's automated scoring system and changes nothing inside the capture
window. Claude never executes trades; brokerage access is read-only.**

---

## 0. Core philosophy

- **Money is the byproduct of execution.** Grade sessions on execution
  quality, not P&L.
- **React, don't predict.** Every clean win on day one came from entering
  after confirmation at a level; both pre-positioned entries went ~breakeven.
  No edge exists on what a binary event will say — only on reacting to it
  fast and structured.
- **Selective participation is the retail edge.** No trade is a position.
  Most days need 0–2 trades.
- **Price action overrules flow when they disagree.** Flow (UW) is a
  confirmation/veto layer, never the trigger. (Proven 2026-08-13: tide at
  day-highs while SPY broke down at 1:35 PM.)
- **Let a level decide, not your stomach.** Write invalidation down before
  entry. A rule-following loss is a good loss (cost of doing business); a
  rule-bending win is a bad win (trains the habit that blows the account).

## 0a. Daily pre-market routine (~20 minutes, 9:05–9:25 ET)

1. **Read the brief** (arrives ~9:05–9:10). Note: mood, gamma regime,
   watchlist flags, and every event time for the day.
2. **Draw the lines** on SPY and QQQ (and any flagged watchlist name).
   The brief's §0 table gives exact numbers each morning:
   - **Previous day high / low / close (PDH/PDL/PDC)** — yesterday's
     auction extremes. These are memory levels: trapped traders and
     unfilled orders cluster there, which is why they act as
     support/resistance and why breaks of them mean something.
   - Premarket high/low (the overnight range).
   - Gamma walls (from the brief) + record/52-wk high if nearby.
   - Nearest round numbers. VWAP plots itself once trading starts.
3. **Read the open's location** — this sets the day script:
   - Open INSIDE yesterday's range → range-day bias; PDH/PDL are the
     walls; fade edges / trade breaks of them per §1c.
   - Open ABOVE PDH (gap up) → PDH flips to first support; gap-and-go vs
     gap-fill is the day's first question; don't short strength blindly —
     watch the first retest of PDH.
   - Open BELOW PDL (gap down) → mirror image.
4. **Write the two triggers before 9:30** — bullish level, bearish level,
   and the invalidation for each. If they aren't written down, they don't
   exist.
5. **Re-read the time & loss rules** (§1d) and decide size before the open.
6. **First 10–15 minutes: watch, don't trade.** Let the opening range
   form; entries need confirmation (§1c) and the volume floor is armed
   from the first completed bars.
7. **At 9:35, mark the opening range (adopted 2026-08-13):** the first
   5-minute candle's high (ORH) and low (ORL) — two intraday trigger
   lines to pair with PDH/PDL. Confluence ladder: above PDH *and* ORH =
   strongest bullish alignment (mirror for bearish); inside both ranges =
   hands off. The opening range only exists after the open — the brief
   can't pre-compute it; drawing it is a 9:35 habit.

## 1. The four-step hierarchy (environment → location → confirmation → execution)

### 1a. Environment (before the open — the brief does this at 9:05)

- **Gamma regime (GEX):** positive = GLUE (dealers fade every move: dampened,
  pinny, breakouts need extra proof, level breaks often whipsaw, favor
  fading edges and taking profits at walls). Negative = GASOLINE (dealers
  amplify every move: respect breaks instantly, momentum runs, tighten
  stops). Note the walls (biggest per-strike GEX near spot = pin magnets,
  strongest on expiration days) and the approximate flip zone.
  - GEX is meaningful on SPY/QQQ/index complex and mega-chain names
    (TSLA/NVDA class) near expirations. Ignore on thin chains. Always
    compare a ticker to its own history, never across tickers.
- **Tide (UW market-tide):** net call vs put premium, 5-min bars. Rising
  calls + dormant puts = healthy. The reversal signature = calls draining
  WHILE puts wake up (see §4 tripwires).
- **IV rank:** cheap IV (rank <20) = long premium reasonable, protection
  cheap; high IV = event premium, crush risk after.
- **Scheduled catalysts:** know every 8:30/10:00/1:00 event and the
  scenario tree before the open.

### 1b. Location (where business is done)

- Map levels BEFORE the open: yesterday H/L/C, today's premarket range,
  round numbers, record highs, gamma walls, VWAP once trading.
- **Don't initiate mid-range.** Entries happen at edges: reclaim/break of a
  mapped level, or a pullback into a prior breakout zone ("discount"), never
  in the middle where odds are worst in both directions.
- Buying at the top of a resistance stack = "buying premium." The one losing
  round-trip on day one was exactly this (1:06 PM entry at the
  776.40–777.05 stack top).

### 1c. Confirmation (the trigger)

- **Timeframes:** 5-minute = decision chart (all triggers are 5-min CLOSES
  through levels). 1-minute = execution timing only, after the signal.
  15-minute = the verdict/honesty check at :15/:30/:45.
- **The five candle patterns** (drawn 2026-08-13; core principle: wicks are
  rejections, bodies are decisions):
  1. *Rejection wick at resistance* — long wick above the level, close back
     below → fade signal.
  2. *Failed breakdown (trap)* — wick pierces support, close back above,
     next candle up → bullish trap of sellers; the pattern that punishes
     early put buyers. Wait for the CLOSE below a level, never the touch.
  3. *Real breakdown* — full body CLOSES below support, next candle
     continues, volume rising → bearish entry.
  4. *Real breakout* — full body closes above resistance AND next candle
     holds above → bullish entry.
  5. *First move fake, second move real* — post-event whipsaw: never trade
     the headline candle; entries live on candle two or three (~1:05–1:15
     after a 1:00 event). Mirror applies both directions.
- **Retest entries beat breakout entries (adopted 2026-08-13):** prefer
  entering on the successful RETEST of a broken level (break → pull back
  to the level → defenders step in) over chasing the initial break.
  Cheaper entry, tighter stop (just beyond the retest failure point), and
  structurally immune to first-move fakes — the fake IS a failed retest.
- **Relative strength filter for single names (adopted 2026-08-13):**
  confirm index direction first, then trade the ticker LEADING the index,
  never the laggard "because it hasn't moved yet."
- **Regime gate for continuation setups (adopted 2026-08-13 — the
  synthesis):** ORB/PDH continuation is a gasoline-regime strategy.
  Negative or weak-positive GEX → trust breaks, continuation is the
  A-setup. Strong positive GEX (glue) → expect failed breaks; demand the
  full retest confirmation, favor fading edges, take profits at walls.
- **Volume participation floor (adopted 2026-08-13):** no NEW entries when
  the last two completed 5-min bars are both under **~100K shares on SPY /
  ~60K on QQQ** (Robinhood chart feed units — this feed undercounts the
  consolidated tape; thresholds are feed-specific). Re-arm after a bar
  prints back above the session median (~130K SPY / ~105K QQQ). Portable
  form: dead tape ≈ bar volume under ~40% of that day's 9:30–10:00 average.
  Calibrated at VIX ~14; recalibrate on regime change. Entry filter only —
  stops/exits always stay active. Events re-open the tape (they bring
  volume), so this permits event-driven afternoon entries while forbidding
  doldrums drift-chasing.
- **Flow confirmation (UW):** after price triggers, flow agreeing (tide
  accelerating in trade direction; ask-side sweeps in the underlying) =
  hold with confidence; flow diverging = tighten up. Ask-side fraction ~1.0
  = aggressive buying; ~0.0 = hit the bid (likely selling); sweeps =
  urgency; short-dated ask-side call sweep clusters = the bullish-attention
  signature.

### 1d. Execution & management

- **Stops: architecture from day one that worked:**
  - Stop-limit with **15-cent trigger→limit buffer** on liquid 0DTE (10c
    proved survivable but thin; fast tape gaps through tight buffers —
    "triggered but unfilled" is the failure mode that matters).
  - **Multi-contract positions split stops** (one tight at the warning
    level, one at full invalidation) — no single decision is all-or-nothing.
  - Winning single contracts get a floor at breakeven-or-better once up
    meaningfully ("the trade can't lose"), placed just beyond a structural
    retest level so normal retests don't trigger it.
  - Stops are disaster insurance; the PLAN is selling alerts/targets into
    strength.
- **0DTE mechanics (hard constraints):**
  - Robinhood force-closes expiring options **3:45 PM ET at market**. The
    real bell is **3:30** — after that it's decay + forced-liquidation
    mechanics with zero upside. Whatever P&L exists at 3:30 IS the result.
  - Expiry breakeven ≠ mark P&L. Marks are harvestable all day; the 4 PM
    print only pays past strike+cost. ITM winners become ~pure delta
    (reversal is the enemy, not theta); ATM holds bleed extrinsic to zero
    by close even if price goes nowhere.
  - Holding through a binary event is a NEW trade decision each time.
    Gaps skip stops — overnight holds disable the entire risk toolkit.
- **Time rules:**
  - Prime window: first ~2 hours after the open. (Day-one data: all wins
    entered 9:49–12:31; the loser at 1:06 PM.)
  - CANDIDATE RULE (not yet formally adopted): no new entries after ~11:30
    ET except on scheduled-event reactions.
  - 1:00–2:30 doldrums: volume floor usually forbids entries anyway.
  - Power hour (3:00–3:30): most likely window for targets OR stops to
    finally hit; be present, not asleep.
- **Loss rules:**
  - CANDIDATE RULE (not yet formally adopted): hard stop after two
    consecutive losses — the tripwire goes one step BEFORE the personal
    tilt point, not at it.
  - Good loss = rules followed, variance happened (day one: −$171 hindsight
    on the 1:37 whipsaw exit — correct process). Bad loss = anticipation
    without confirmation, chased, sized up frustrated. Grade accordingly.

## 2. Event protocol (auctions, data prints, earnings reactions)

1. Pre-event: map levels, note positioning lean (tide, flow, who's hedged),
   sit on hands during the pre-event drift — a drift changes entry prices,
   not the plan.
2. Know the scorecard before the event (e.g., Treasury auctions: tail vs
   stop-through, bid-to-cover baseline ~2.3–2.4, dealer share low = strong;
   the bond market's own reaction (TLT) IS the verdict within seconds).
3. Skip the headline candle. Read candles two and three (5-min closes vs
   the mapped levels) with the flow layer as confirmation.
4. Chop/in-line outcome → no entry is the position; the market is waiting
   for the next catalyst.
5. Pre-positioning before binaries: the market prices the event fairly
   (straddle = the odds); rallying into a print raises the bar
   ("beats get sold" — 8 for 8 on 2026-08-13); flat-before-the-event is a
   position (short regret, long information).

## 3. Known market behaviors (validated, dated)

- **2026-08-13:** Priced-for-perfection names sold beats all day (CSCO,
  TPR, YETI, COHR, JD, DDS, CBRS, AMAT). Margin/guidance quality beat
  headline EPS every time.
- **2026-08-13:** Positive-GEX glue day: SPY pinned between 775/780 walls,
  closed 777.77 between them; breakout ground instead of ripped; the 1:35
  level break whipsawed back. Regime read would have predicted all three.
- **2026-08-13:** Pre-event hedging spikes (puts +$46M in one bar at 11:47)
  can complete a textbook "reversal signature" and still fully unwind into
  the event — flow signatures within an hour of a known binary are
  positioning, not prophecy.

## 4. Monitoring infrastructure (how Claude supports live sessions)

- **Tide tripwires** (scratchpad script, ~5-min polls, completed bars only):
  A = calls fall 2 straight bars while puts rise; B = net put premium >
  +$40M; C = calls > $40M below session high-water mark. B is the "sellers
  attacking" half; A/C alone = buyers stepping back.
- **Position watchdog** (~60s polls): underlying level alerts (take-gain
  targets, warning level, invalidation) + time alarms (2:00, 3:00, 3:30
  decision bell, 3:40 final call).
- Windows gotchas: scripts must set UTF-8 stdout (cp1252 kills emoji
  alerts EXACTLY when they fire); Python urllib fails on UW's cert chain —
  fetch via curl; keys read from repo .env into shell vars, never printed.
- Claude monitors, frames decisions, and pulls data; the human executes
  every order. No exceptions.

## 5. Session grading (A/B/C game — adopted concept 2026-08-13)

After each session, grade EXECUTION (not P&L): entries only at
levels-with-confirmation? Stops honored? Time rules respected? Volume floor
respected? Consistency comes from deleting C-game sessions, not adding
A-games. Log the grade + the one decision-quality note in the trading
journal section below.

## 6. Journal

| Date | Realized P&L | Grade | Note |
|---|---|---|---|
| 2026-08-13 | ≈ +$239 (8 round trips) | A− | Ding: 1:06 PM entry at stack top, pre-confirmation, in fading volume. Everything else by the book. Stops beat diamond-hands by ~$109 with a fraction of the drawdown. |
| 2026-08-14 | ≈ +$124 (4 round trips) | A | Traded the RS leader (TSLA calls), took a −$5 rule stop, re-entered on revalidation, and sold at 9:59 — one minute before UMich, which top-ticked TSLA's day. Flipped to puts post-print (+$37 SPCX), scratched RDDT. Flat by 11:00 on a max-glue OPEX Friday that drifted/pinned all afternoon — selective participation executed. Regime read went 2-for-2 (pin 775–780 called premarket; closed ~776.3). Lesson logged: expiration-day tide can go BOTH-negative (premium liquidation, not direction) — read it as "pin/decay," and single bars near the open are too small to tripwire on (first fires at 10:24 were the real one, though). |
| 2026-08-17 | net green, $ TBD (2 round trips, both SPCX) | A− | Trade 1: long into the 9:40–10:00 momentum leg; flow flipped (−$9M call-premium exit led price by minutes) and the stop fired ~2% off the high — flow-led exit saved the gasoline-regime slide that followed. Trade 2: re-entered 147C 8/21 on a defined signal (2 consecutive green call windows + hold >147), floor (146.9 → 148.4 → 148.8) honored through 4 hours of range, exited green as top-attempt #4 failed at the day high; fade trigger fired minutes later, validating the exit. Ding (the A− and the day's lesson): the plan named $6.30 as the scale line, the mark touched $6.30 for ~3 minutes, and no resting limit order was working — manual watching missed the window. RULE ADOPTED: when a plan names an exit price, place the resting limit the moment the plan is written. Context notes: RDDT morning-long invalidated exactly at the mapped flip (−4% by 10:00 on inclusion-fade selling); SPY pinned 775–780 all morning per positive-GEX regime read (4+ wall touches, zero breaks); US–Iran ceasefire expiry made oil (USO) the standing tripwire — WAR TELL line added to all intraday cards. |
| 2026-08-19 | **-$15 realized** (8 intraday round trips -$147; 3 carry closes +$132 — SLS $0, CVX +$60, USO +$72). Flat at the close: $1,239.76, all cash, zero heat. Gross of fees. | **C** | Green-then-scratch day, C-game execution. Grade and notes were written BEFORE the 2:00 PM FOMC minutes and are unchanged by the outcome (§9); only the ledger below is amended. **Nine opening orders against a "most days need 0-2 trades" guideline. Zero stop orders all session** (every fill `trigger: immediate`, `stop_price: null`), so per §5 each position's risk was its full premium. Peak open premium $894 on $1,080 equity = **82.7% vs the 12% heat cap (6.9x)**; the single TSLA 345C at $370 was 34% of equity vs the 4% per-trade cap (8.6x). Directional incoherence 10:42-10:56: long TSLA 345C and long QQQ 711P at once — call +$100, put -$134. **Moneyness, not DTE, decided every outcome:** the winners (+$100/+$21/+$16) were slightly-ITM 0DTE carried by intrinsic; the losers were far-OTM (QQQ 711P 1.48->0.14, -91%) or deep-OTM at peak vol (MRNA). Same 0DTE expiry, opposite results. **MRNA 8/21 115P: bought 11:12 at 2.85 (19% OTM, IV 278%), sold 2:59 PM at 1.13 = -$172.** The exit was correct independent of the thesis — MRNA closed **+176.97% at 174.38**, running another 12% after the sale, so every hour held would have cost more. The thesis (parabolic retrace) may yet prove right; the position expired Friday. Thesis and instrument had different deadlines. Ding on entry location: the 11:00 TSLA re-entry was at the top of an $8 run between the 345 magnet and 350 call wall, breakeven $348.70 above the then-day-high $348.56 — the same "buying premium at the stack top" error logged on day one (1:06 PM, 776.40-777.05). The 345 retest was the §1c entry and was skipped. **Repeat well:** the 10:56 TSLA scale-out (+$100), closing both 0DTE legs green before the binary rather than holding into it (§1d), and cutting MRNA before it ran further. **Closing discipline graded clearly better than opening discipline** — every good decision today was an exit. Close: SPY 769.10 (+0.21%) below settled VWAP 770.01; QQQ 716.08 (-0.20%) never participated; **TSLA 351.12 (+4.23%) closed above its 350 call wall** — the relative-strength read held from 9:05 to the bell and was the day's cleanest signal; TLT +1.65% at its high (bonds never read the minutes as hawkish); GLD +3.83%. Post-event tape gave two live bars (particip 0.58/0.59) then died back under the 0.40 floor until a genuine volume surge into the close (1.06-1.55). Lesson to carry: **a -$15 day with no stops and 6.9x heat is a variance outcome, not a process.** §5 — consistency comes from deleting C-game sessions, not adding A-games. |

### Monitoring and confirmation — REASONED, not validated (added 2026-08-19)

Four failures from one afternoon of live monitoring. **None is validated** — each rests
on a single session and must not be treated as a rule until `options-expert/log/`
carries graded outcomes (§7).

1. **A tick crossing a level is not a trigger.** The playbook evaluates 5-minute
   CLOSES (§1c). A tick-based level alert fired twice on noise as price sat on
   769.50, including one alert reversed 30 seconds later.
2. **Always drop the in-progress bar.** FMP lags ~2 minutes on bar rollover. This
   bit twice: a participation ratio computed off a partial bar read `0.06` and was
   meaningless, and a "close" reported as 769.20 settled at **768.99**.
3. **Alert text must read state live at fire time.** A 3:27 PM force-close warning
   asserted "MRNA 115P still open" 28 minutes after it had been sold — the string
   was baked in when the monitor was armed. A false position claim during a
   force-close window is the worst possible time for one.
4. **Partial confirmation is not confirmation.** §1c pattern 3 requires three
   things — a full body closing below support, **the next candle continuing**, and
   rising volume. A "breakdown confirmed" call was made on the first and third; the
   next candle closed back inside the band on collapsing volume (0.59 -> 0.36) and
   negated it. This is the same root error as the 11:00 TSLA entry: treating a
   necessary condition as sufficient.

**Proposed fix (untested):** require TWO consecutive closes in the same band AND at
least one bar clearing the 0.40 participation floor before any signal. Retro-checked
on 2026-08-19 this would have suppressed the false 2:16 PM call and stayed silent
through 30 minutes of chop, while still firing once on a real break (15:40 close
769.01 and 15:45 close 768.73, participation 0.59/1.08). One session is one session.

**Also recorded against myself:** the monitor was stood down at 15:34 on the
reasoning that a flat account had "nothing left to signal on." That conflated
position state with whether a signal would occur — the real break fired ~13 minutes
later. It cost nothing here, but the reasoning was wrong.
| 2026-08-20 | **≈ −$187 realized** (QQQ 0DTE 713C −$155 net of fills 2.16→0.61 est; NVDA/SPCX/QQQ-706P open overnight, −$108 unrealized at the close). Account $985.76 close, first sub-$1,000 close. Figures gross of fees; realized to be reconciled against fills tomorrow. | **C−** | Written 8:45 PM, before Friday's open — the overnight outcome is unknown at write time (§9). **The split verdict: the written system went ~6-for-6; the hands went ~1-for-5.** Traps the pre-registered triggers correctly refused: the 9:40 TSLA breakdown (bounced), the 10:03 TSLA VWAP-reclaim long (died next candle), the 10:05 QQQ PDL break (negated on its confirmation candle), the 11:10 TSLA retest front-run (the 11:15 bar tagged 343.22, two cents through where the stop would have been), the mid-morning chases the 15-min honesty check exposed. Every one was a losing trade that never happened because a card demanded a specific candle. **The entries actually taken bypassed the cards:** NVDA 8/21 220C bought 10:39 at the call wall (far OTM, delta 0.25 — the structure's fifth loss this week), QQQ 0DTE 713C bought 10:42 mid-box minutes after "not an entry" was stated; both stop lines fired at 11:05/11:20 and neither exit was taken ("closing within 10 minutes doesn't feel right") — the QQQ ticket then bled −74% before being sold, the auction non-event removing its last thesis. **Divergence between stated plan and executed book, three times:** the 10:39-10:42 entries against the just-written cards; holding through fired stops; and at 3:53 PM a QQQ 706P bought one minute after "we will just keep the SPCX" — the same correlated add that had just been argued down in TSLA form (§5: correlated positions are one bet). **What was genuinely good:** the SPCX 8/21 133P at 3:44 (trend ✓ flow ✓ slightly-ITM delta −0.52 ✓ cheap vol IV 72 vs RV ~102 ✓ — first entry this week ticking all four); the AMZN scanner signal correctly refuted by side-attribution (the "unusual puts" were SOLD at 3% ask — side-blind volume scanner); the five-name 8/21 positioning sweep (OPEX shape: pin the indices, insure the tails; the TSLA 342.5P 90%-ask 31×-OI block the standout print). Day context: gap-down morning, TSLA broke 345→339 and V-recovered to close 345.13; in-line 30-yr TIPS auction (non-event #4, TLT verdict-spike at 13:02 faded in 3 min) yet the market sold anyway to close at lows (SPY 762.60 −0.84%); SPCX closed 134.00 — the put's invalidation line to the penny — on a 1.5M-share/min closing-auction ramp whose final minute rejected 134.65. Overnight book: QQQ 706P +$26 / SPCX 133P −$62 / NVDA 220C −$71, ~$473 premium (48% of equity), all expiring Friday, force-close 3:30–3:45, net short ~0.5 delta into OPEX. Cards for all three written pre-close (SPCX: out on first 5-min close ≥134; QQQ: out above 712.61; NVDA: sell the first bounce). **Lesson to carry: the edge this week has been in the refusals, not the entries. The system that says no is working; the next capability to build is letting it also say when.** |
