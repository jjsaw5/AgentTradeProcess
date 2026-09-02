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
| 2026-08-21 | **+$184 realized** across **20 closing trades** (brokerage PnL history, gross of fees). Composition: TSLA 350C **+$546** (sold 10:13 AM at $8.30 — the week's best trade); overnight book **−$396** (SPCX 133P −$103 sold 10:07 at 1.13; a second SPCX put −$88 sold 10:14 at 1.50 — position never surfaced in session, strike `NA_unresolved`; NVDA 220C −$110 sold 10:09 at 0.10; QQQ 706P −$95 sold 10:29 at 0.42); **15 further TSLA 0DTE round trips netting +$34** (best +$185 at 11:44, worst −$113 at 11:10; includes the 362.5C +$9 reported in-session as "+$12"). Ex the 350C, the other 19 trades net **−$362**. Est. equity ≈ $1,170 (UNVERIFIED, fees pending). | **C+** | Written 4:30 PM from reconciled fills (§9: the charm prediction below was graded against its pre-registered text, not rewritten). **The 350C is the trade of the week and it was exit that made it:** bought in the 9:58 vertical (pre-confirmation — the two-close standard confirmed 360 only at 11:00, so the entry was a chase that worked), sold 10:13 at $8.30 with the stock ~358.5 — ahead of the 10:30 trap candle at 361.60, better than the written 357.50 trail would have paid. Closing discipline again outgraded opening discipline, second day running. **The C is the same C as 8/20, larger:** the session narrative said "flat, holding the playbook" from 1:05 PM; the book shows 15 TSLA round trips between 10:54 and 3:09 that the written process never saw — including three after "will hold our playbook now" (−$74 at 2:06, +$20 at 2:23, +$30 at 3:09; the "big push at 2:23" and "huge push at 3:09" messages coincided with those exits). The process graded 2 of 20 trades in real time. Nothing in the rules forbids scalping; the deviation is that the book and the stated plan were different documents all afternoon, which §8 exists to record. Churn was at least contained: max single loss −$113, no diamond-handing, several rule-shaped scratches. **The day's method result — the two-close rule went 7-for-7:** five fake pokes above 364.4/365 rejected (each closed back inside within one candle), two real breaks confirmed (360 at 11:00 → ran +$4; 365 at ~3:15 → ran to 366.45, then the closing auction took it back — confirmation tells you the break is real, not that it survives the auction). **§9 charm-prediction grade (pre-registered 1:05 PM):** direction WRONG 1:15–2:00 (price drifted down while the gauge deepened), CONFIRMING 2:00–3:30 as written (held 362+, low-volume drift up), pin verdict half-right — price glued to 365 from 3:00–3:50 but the auction faded it to a **362.78 close** (sessHi 366.45), so "pinned at 365" was true for the hour and false for the final print. First full day of `spot-exposures` data: charm_oi **−597B → −1,213B**, a clean intraday doubling into expiry; sign convention still `UNVERIFIED` — candidate reading (deepening negative + drift toward the dominant strike = decay flow feeding the pin) logged for validation next OPEX (9/18). Closes: TSLA 362.78 +4.8% (never touched 360 after 11 AM), SPCX 136.93 (escaped its 135 pin entirely — the one anti-pin datapoint), QQQ 713.36, NVDA 214.68 (the 220-pin thesis failed all day), SPY 765.60. **Lesson to carry: one trade made +$546 and nineteen made −$362 — the account is being paid for patience and charged for activity, in the same market, on the same day, by the same hands.** |
| 2026-08-24 | **+$20 realized** on 21 trades, all TSLA (brokerage PnL, gross of fees). Shape: morning (to 12:00) **−$235**, midday **−$170**, after 3:00 PM **+$425** — one +$422 two-lot at 3:01 carried the entire day. | **C** | Written 8/25 from reconciled fills; Monday's entry was not filed on the day (recorded as the gap it is). TSLA gapped down and closed **348.95, −3.8%**, sliced the 358–360 shelf in the first five minutes and never came back. **The two pre-registered cards both did their job without costing a dollar:** W1 (9/18 400C) hit its written invalidation — daily close below 355 — and died unentered; R1 (360 reclaim, written intraday at 10:50 with price ~357.5) never printed its two-close trigger and expired at its own 2:00 PM stale-cutoff. Pre-registration worked exactly as designed on both. **What the book did instead:** 21 discretionary TSLA round trips the written process never saw, netting +$20 — a full day of churn for the price of one good late trade. Same intraday shape as 8/25: lose early, recover late. Flow context was unambiguous and bearish all morning (net call premium −$24.6M cumulative by 10:30, calls 42% ask / 48% bid, bull $437M vs bear $459M) — the data said stand down and the book traded anyway. |
| 2026-08-25 | **−$280 realized** on 10 trades (brokerage PnL, gross of fees). Split: **before 12:30 ET −$514; after 12:30 ET +$234.** By instrument: TSLA **+$117**, QQQ **−$330**, SPY −$67. Week-to-date −$242 on 68 trades. | **C** | Justin's own read, given before he saw the numbers: "caught in a whipsaw where I should have stayed out as no setups were forming until later in the day, then I got in and made some of it back." The fills match to the dollar — every loss came before 12:24, four of the last six trades were green. **The accurate self-diagnosis is the day's real product; the trading was not.** **The finding that outranks today — instrument selection.** Week to date: index ETFs (QQQ+SPY) **−$760 on 10 trades**; everything else **+$518**; TSLA alone **+$833 on 50 trades**. The eight QQQ trades average **−$78.50**. Interpretation, not fact: TSLA gets a full research stack every session (gamma levels, net-premium ticks, OI roll, participation vs the opening mean); QQQ gets none of it, and today it chopped 707.46→714.04→709.23 to close $2 from its open. The 10:28 QQQ exit (−$174) landed two minutes before the 10:30 session low. **Proposed rule, NOT yet ratified:** no index-ETF options trades until QQQ/SPY carry the same pre-written card standard as single names. **Assistant error, recorded per §9:** at 10:33 the call given was that TSLA's long case had "deteriorated on every axis" (third failed test at 352.5–353.4, participation 0.60–0.64, net-call premium falling, wall confirmed overhead). TSLA rallied to **356.90 by 12:57**, and Justin's two best trades (+$100 at 12:56, +$170 at 13:20) came inside that window. The mechanical trigger — two 5-min closes above 353.43 with participation ≥0.40 — DID fire in the 11:00 hour and would have caught it. **The rule worked; the narrative laid over it did not.** Also logged: `gex-levels` drift bit again — TSLA's call wall read 387.5 at 10:14 and 352.5 at 10:33, so a "nothing overhead" call built on a thin-data snapshot had to be retracted mid-session; treat any gex read before ~10:30 as provisional. Day context: soft 10:00 data (CB Consumer Confidence 89.4 vs 90.3 est, New Home Sales −10.5% vs −1.4%, Richmond Fed 4 vs 7) and the indices sold it — SPY −0.15% from open, QQQ −0.28%, TSLA +0.57%, NVDA +0.43% into tomorrow's print. Justin flagged unusually low volume premarket and the data confirmed it: TSLA ran 0.81× its 3-day pace over the first six minutes, and NVDA's call volume sat near **half its 30-day average the day before earnings**. **Lesson to carry: the account has one instrument that pays and one that doesn't, and the difference is preparation, not luck.** |
| 2026-08-27 | **−$666 realized** on 24 trades (brokerage PnL, gross of fees). By symbol: TSLA −$339 (13 trades), QQQ −$225 (4), MRNA −$131 (3), SPY +$29 (5). | `NA_unresolved` | **Ledger-only row, filed 2026-09-02 from reconciled fills. No session record exists for this day, so no execution grade can be assigned** — the grade is `NA_unresolved` per §4, not a blank and not a guess. Recorded now because it is the primary evidence behind the `options-expert/SWING_STRATEGY.md` §6a two-loss circuit breaker: the first two losing trades closed at 9:44 (QQQ −$26) and 9:49 (QQQ −$141); a hard stop there ends the day at −$112 instead of −$666. Shape: 12 of 24 trades between 9:44 and 11:01 ET, netting −$467 before noon. The 13-trade TSLA block includes four consecutive losses of −$80/−$55/−$130/−$90 between 9:57 and 10:52. What is missing and cannot be recovered: entry reasoning, whether stops were placed, whether any card was written. That absence is the finding. |
| 2026-08-28 | **−$630 realized** on 14 closing events (brokerage PnL, gross of fees), of which **−$582 on 13 discretionary trades** plus a **−$48 GLD event at 16:00 ET priced at $0** — an expiration/assignment, not a decision. By symbol: SPY −$405 (6 trades), TSLA −$112 (4), NVDA −$65 (3), GLD −$48 (1 event). | `NA_unresolved` | **Ledger-only row, filed 2026-09-02 from reconciled fills. No session record; no execution grade can be assigned** (§4). Second data point for the §6a two-loss stop: losses at 9:45 (SPY −$99) and 10:18 (SPY −$94); stopping there ends the day at −$193 rather than −$582. Note the honest wrinkle in that test — the day's single best trade (**SPY +$202 at 11:39**) comes *after* the stop line, so the breaker gives up a real winner to avoid the −$389 that followed it. It is a net save, not a free one. The GLD −$48 is logged separately because a position that expires is not an execution and grading it as one would flatter or damn the day for something nobody chose that session. |
| 2026-08-31 | **−$45 realized** on 12 trades (brokerage PnL, gross of fees). TSLA **−$71** (10 trades), SPY **+$26** (2). Largest single loss −$92 (10:50 ET); largest win +$44 (9:38 ET). | **C** | Written 2026-09-02 from reconciled fills; the day's session record covers the research, not the book. **The day's real product was written, not traded:** the behavioural disclosure (revenge trading, no willpower to stop, chasing candles, greed, FOMO) that became `options-expert/SWING_STRATEGY.md` §6, and the two pre-registered tickets. **Ticket 1 (XLE shares, 63.00–63.51 retest after 10:00) was OFFERED and declined** — XLE sat in the zone for 158 minutes with a low of 63.15 at 11:24. Not taking an offered signal is a legitimate choice; not writing down why is the gap. **What the book did instead: 12 discretionary TSLA/SPY option round trips the tickets never covered**, on the same day a $200 account was declared a discipline-practice account. The C is for the divergence, not the −$45 — the loss is small and the tail was controlled (no single loss beyond −$92, no diamond-handing). §6d cap is 2 entries; 12 were taken. |
| 2026-09-01 | **+$98 realized** on 8 trades (brokerage PnL, gross of fees). TSLA **+$55** (4 trades: +6/−21/+50/+20), PG **+$19** (2: −15/+34), PLTR +$27, SOXL −$3. First green day since 8/26. | **B−** | Written 2026-09-02 from reconciled fills. **Every trade closed green or scratched small — max loss −$21 on eight trades.** That is the first session all week where the loss tail was actually capped, and it is the single behaviour most worth repeating: the day was won by the size of the losers, not the size of the winners. **Pre-registration went 1-for-1:** Ticket 3 (TSLA continuation) was gated on the 9:30 OI roll and **the gate FAILED exactly as pre-registered** — the 9/4 360C added +5,341 OI at 33% ask (sold, not bought), and the largest builds were deep-OTM puts. That is the log's first clean predictive success: a written expectation, an objective gate, and a refusal that cost nothing. Ticket 4 replaced it and carried the n=30 base-rate study that **refuted** the TSLA continuation thesis outright (moderate +5–7% prior days → 35% intraday win rate) and named XLE as the sizeable expression instead. **The B− and not higher:** 8 trades against a §6d cap of 2, and PLTR/SOXL are outside the §2 universe. The process said one instrument and one setup; the book said four. |
| 2026-09-02 | **+$38 realized** on **13 trades** (brokerage PnL, gross of fees; 6 wins / 7 losses, 46%). By symbol: **SPY +$88** (4 trades), GPRO +$20, PG +$1 (3), **TSLA −$29** (4), NVDA −$42. Largest win +$105 (9:40 ET), largest loss −$62 (9:59). Account value read live at 15:25 ET: **$491.48** ($475.64 cash, $15.84 legacy fractional shares, **$0 options — flat**). | **C+** | **Written 15:25 ET with 35 minutes left in the session (§9) — the numbers below are 9:30–15:25, not closes, and are labelled as such.** Marks at write time: TSLA **352.96, −2.11% from a 360.56 open that was also the day's high** (low 349.92); XLE 65.31 +1.28%; PG 147.63 +0.84%; SPY 765.36 +0.38%; QQQ 708.58 +0.21%; USO 141.32 +1.36%. **Pre-registration: Ticket 4 graded A, and it graded A by not trading.** Its written expectation was "I expect no trade"; the trigger required a 5-min close below the 351.61 gamma flip after 14:30, and there were **zero** such closes — the post-14:30 low was 351.80, twenty cents above the line. Ten consecutive 5-min closes printed 351.86–353.15: the pin held to the tick. **Ticket 1 graded, and the grade is uncomfortable:** the 8/31 XLE entry was offered and declined; XLE is now 65.31, roughly **+2R above the 63.70 stop-adjusted target** the ticket wrote. A correct signal, refused. That is a real cost and it is recorded as one. **Two rules the book broke, and today the book was right both times.** (1) §4 bars entry before 10:00 — the first trade fired at **9:40 and was the day's best at +$105**. (2) §2 bars index ETFs — **SPY was the day's best instrument at +$88 across 4 trades**, against a week-to-date SPY record of −$376. Neither result overturns its rule at n=1, and neither is being explained away: they are logged as counter-evidence so that the rules stay falsifiable. **The §6a two-loss stop would have COST money today:** losses at 9:47 (−$37) and 9:59 (−$62) trigger the breaker at 9:59 with **+$6** banked versus the actual +$38 — a **−$32** result for the rule, against the +$943 it saves across 8/27–8/28. First negative datapoint for §6a; the table in `SWING_STRATEGY.md` §6a must carry it. **Structure of the day: ten trades between 9:40 and 10:50 netted +$4; three trades after 12:30 netted +$34.** The morning was an hour of churn that paid for its own commissions and nothing else — the same shape logged on 8/24 and 8/25. **Deviations: 13 trades against a §6d cap of 2 entries; NVDA and GPRO are outside the §2 universe; trade direction per fill is `NA_unresolved` (the brokerage PnL feed returns an empty `side` field), so no direction-flip check against §6d could be run.** **What genuinely improved: the loss tail.** No single loss exceeded −$62 on an account under $500 — nothing today resembled the −$164/−$141/−$130 prints of last week. Green day, controlled downside, rules still being outvoted by the hands. **Lesson to carry: the day was won on the size of the losers again, and the two rules that got broken both paid — which is exactly when a rule is hardest to keep and most important to test properly rather than abandon on one good morning.** |
