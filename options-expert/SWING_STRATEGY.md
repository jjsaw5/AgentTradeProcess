# Swing Strategy — 2–5 DTE, single names, brief-driven

**Created 2026-08-31 by owner decision: "no more 0DTE unless we have data that
shows it's worth it."**

Status: **SHADOW MODE.** No live capital until §7's funding gate is met. Every
rule below is either **[EVIDENCE]** — derived from 106 reconstructed round trips
in this account, 2026-08-21 → 08-28 — or **[REASONED]** — plausible, untested,
and `UNCALIBRATED` per CLAUDE.md §7. The labels are not decoration. Do not
promote a `[REASONED]` rule to a hard rule without graded outcomes in
`options-expert/log/`.

Claude never executes. CLAUDE.md §2 stands unamended: the human places every
order.

---

## 1. Why this document exists — the evidence

Realized P&L, account ••••4971, 2026-08-19 → 08-28: **−$1,436 over 119 trades.**

| Date | P&L | Trades |
|---|---|---|
| 08-19 | −$15 | 11 |
| 08-20 | −$151 | 6 |
| 08-21 | +$184 | 20 |
| 08-24 | +$20 | 21 |
| 08-25 | −$280 | 10 |
| 08-26 | +$102 | 13 |
| 08-27 | **−$666** | 24 |
| 08-28 | **−$630** | 14 |

**Holding time vs outcome** (106 FIFO-matched round trips; reconstruction ties
to broker totals within ~8%, so treat the *relative* pattern as the finding,
not the exact dollars):

| Hold | Trades | P&L | Win rate |
|---|---|---|---|
| 0–5 min | 38 | −$661 | 47% |
| 5–15 min | 34 | +$200 | 50% |
| **15–30 min** | 14 | **+$305** | **64%** |
| **30–60 min** | 16 | **−$1,143** | **12%** |
| 1–3 hr | 4 | −$73 | 25% |

**One bucket — 16 trades held 30–60 minutes — is ~80% of the total loss, at a
12% win rate.** That is not a strategy underperforming. That is the signature of
holding losers: nobody deliberately sits in winners at a 12% hit rate.

**By DTE at entry:** 0DTE 85 trades −$1,019 (46% win) · 1DTE 21 trades −$353
(38% win) · **2DTE+ : zero trades.** The 0DTE exit is evidence-backed. What
replaces it is not — hence shadow mode.

**By symbol:** QQQ 6 trades −$555 (**17% win**) · SPY 17 trades −$443 (41%) ·
TSLA 77 trades −$178 (49%) · NVDA 3 −$65 (0%) · MRNA 3 −$131 (33%).
**Index ETFs: 23 trades, −$998.** TSLA at 77 trades for −$178 is churn — a 49%
win rate paying the spread 77 times.

---

## 2. Universe

**Trade:** TSLA, plus at most **one** additional single name that receives the
full daily research stack (gex-levels, net-prem-ticks, oi-change roll,
participation vs the 9:30–10:00 mean).

**Do not trade:** SPY, QQQ, or any index ETF. **[EVIDENCE — 23 trades, −$998,
17–41% win rates.]** This is the highest-confidence rule in the document.
Reinstating index trading requires a written case and owner ratification.

**Rationale, stated as interpretation:** the names that make money are the ones
that get prepared. Index trades were taken on feel, in products that whipsaw
inside a two-dollar range.

---

## 3. Structure

| Parameter | Rule | Basis |
|---|---|---|
| DTE at entry | **2–5** | [REASONED] — 0DTE/1DTE both negative; 2–5 untested |
| Delta | **0.45–0.60 (slightly ITM)** | [EVIDENCE] — 8/19 journal: winners were slightly-ITM carried by intrinsic; far-OTM weeklies lost 5+ times |
| Spread width | ≤ 2% of contract mid | [REASONED] |
| IV rank | Prefer < 30 for long premium | [REASONED] |
| Legs | Single leg (Level 2 constraint) | Account fact |

**Never buy a far-OTM weekly because it is affordable.** Affordability is not a
reason; it is the trap that produced the losing structure five times. If the
correct contract costs more than the account can carry, **the trade does not
exist** — see §7.

---

## 4. Entry — the brief sets environment, UW/FMP set the trigger

**Pre-open (from the 9:05 brief):** gamma regime, walls and magnets, event
times, previous day H/L/C, relative-strength read. Write the day's two levels
and their invalidations **before 9:30**. If they are not written, they do not exist.

**No entry before 10:00 ET.** The opening range must complete and the
participation floor arms off completed bars. **[EVIDENCE — the 8/25 whipsaw:
every loss came before 12:24; every trade after 12:30 netted +$234.]**

**Trigger, all four required:**
1. Price at a **mapped level** — never mid-range. (Playbook §1b.)
2. **Two consecutive 5-min closes** through the level, each with
   **participation ≥ 0.40** of that day's 9:30–10:00 mean.
3. **Retest over breakout** — enter on the first higher low (or lower high)
   after the level breaks, not on the breakout candle. (Playbook §1c, validated.)
4. **Flow gate (veto):** UW net-premium ticks must be flat-to-favourable at
   entry. Persistent adverse ticks = stand down regardless of price.

**Gamma-map hygiene:** re-pull `gex-levels` immediately before any entry, and
treat any pull before **~10:30 ET** as provisional. **[EVIDENCE — 8/25: TSLA's
call wall read 387.5 at 10:14 and 352.5 at 10:33; a "nothing overhead" call had
to be retracted mid-session.]**

**Flow-alert hygiene:** never size a decision on a single alert. Check the
strike's aggregate ask/bid split first. **[EVIDENCE — 8/25: a TSLA 8/26 352.5P
alert read "32× OI, 100% ask"; the full chain was 48–53% ask across every
strike — even churn, no signal.]**

---

## 5. Holding period and exits

The clock rule that governs 0DTE is replaced by a **thesis deadline**. But one
time-based rule survives, and it is the most important line in this document.

**5a. The 30-minute rule — HARD. [EVIDENCE]**
If a position is red **30 minutes after entry** and has not hit its stop,
**close it.** That is the 12%-win-rate zone; it produced ~80% of all losses in
the sample. There is no version of this trade that is "about to come back."

**5b. Written invalidation, resting order. [EVIDENCE — 8/17 rule]**
A stop-limit with a 15-cent buffer is placed **in the same action as the entry**,
at the level that invalidates the idea — not at a dollar figure that feels
tolerable. Never widen a stop. Never average down.

**5c. Overnight. [REASONED]**
2–5 DTE buys **one** overnight, not three. If the thesis has not begun working
by the **next session's open**, exit — regardless of P&L. Flat-lining is a loss
on long premium.

**5d. Profit-taking. [REASONED]**
Scale **half** at the first structural target (next wall, magnet, or prior day's
extreme). Trail the remainder on 5-min closes: out on the first close below the
prior candle's low. Winners in this account historically resolve inside 15–30
minutes — do not confuse a fast gain with a reason to add.

**5e. Event blackout. [EVIDENCE — playbook §2]**
Never hold through a scheduled binary the thesis did not sign up for (earnings,
FOMC, CPI). Never trade the headline candle; read candles 2 and 3.

---

## 6. Frequency and loss limits — the circuit breakers

These exist because willpower is weakest immediately after a loss, which is
exactly when it is needed. **These rules stop the session so the trader does
not have to.** They are not guidance; they are switches.

### 6a. The two-loss session stop — HARD. [EVIDENCE]

**Two losing trades in a session and the day is over.** No "one more," no
recovery trade, no exceptions. Close the platform.

Applied retroactively to the two worst sessions in this account:

| | Actual | With 2-loss stop | Saved |
|---|---|---|---|
| 2026-08-27 | −$666 (27 trades) | **−$112** (stop after 09:49) | **$554** |
| 2026-08-28 | −$582 (15 trades) | **−$193** (stop after 10:18) | **$389** |

**One rule recovers $943 of the $1,248 those two days cost.** Both sessions were
decided inside the first 40 minutes; everything after was the recovery loop.

### 6b. The give-back rule — HARD. [EVIDENCE]

**A position that has been up 50% or more on premium may never be closed red.**
Once +50% prints, the stop moves to entry — permanently, and it never moves
back down. At **+50%, half the position comes off**, no discretion.

Origin: 2026-08-28, SPY 8/28 771C ×2, in $1.87 at 10:34, peaked near $3.90
(≈ +$400 open), exited $2.88 at 11:39 on a trailing stop for **+$202** — roughly
half the peak surrendered. The owner's own read, recorded in his words:
*"was showing signs of slowing down. I should have cashed out there and been
done for the day."* He was right.

### 6c. The best-trade stop. [REASONED]

**Any single trade closing at +$150 or better ends the session.** On 2026-08-28
that trade (+$202, 11:39) was the best of the week and the last winner of the
day; nine trades followed for −$393. Take the win and leave.

### 6d. Position and direction limits — HARD.

| Limit | Value | Basis |
|---|---|---|
| Entries per day | **2 maximum** | Playbook: "most days need 0–2 trades"; actual was 119 in 9 sessions |
| Concurrent positions | **1** | [EVIDENCE] — 2026-08-27 13:08–13:18: three SPY 771C plus a QQQ 720C opened at once, all closed −$186 together. One conviction expressed four times is how a normal loss becomes a large one |
| **Direction flips** | **None within the same session in the same underlying** | [EVIDENCE] — 2026-08-27 TSLA: 347.5C 10:35 → 355P 10:47 → 350C 10:58 → 345P 11:25. Five flips in one day. Flipping is not a thesis; it is chasing candles |
| Correlated names | Count as one position | CLAUDE.md §5 |

### 6e. The re-entry cooldown. [REASONED]

**After any losing trade, no new entry for 15 minutes.** The next trade after a
loss is the most dangerous one in the book — it is the one the "make it back"
impulse writes. Fifteen minutes is enough for the impulse to pass and for a
genuine setup to still be there when it does.

### 6f. Named failure modes this section fences

Recorded from the owner's own account, 2026-08-31, because a failure mode with a
name is one you can build against:

| Failure mode | Fence |
|---|---|
| "I need to make this money back" | §6a two-loss stop, §6e cooldown |
| Letting a winner round-trip (greed) | §6b give-back rule |
| Not stopping while ahead | §6c best-trade stop |
| FOMO / chasing candles | §6d direction-flip ban, §4 requires a mapped level |
| Trying to hit it big quickly | §3 structure rules, §6d size and count caps |

**None of these require the trader to feel differently in the moment.** That is
the point.

## 7. Funding gate — why this is shadow mode

Account ••••4971 stands at **$205.03** (2026-08-31).

A slightly-ITM 2–5 DTE TSLA call runs **$500–1,300**. An ATM weekly on a large
name runs $300–500. **The only contracts this account can currently afford are
the far-OTM weeklies §3 forbids.** That is a hard blocker, not a preference.

**Live trading resumes when both are true:**
1. Account funded such that **one correct contract plus its stop distance is
   ≤ the per-trade risk limit** — realistically **$1,500+**.
2. **At least 10 graded shadow tickets** exist in `options-expert/log/`,
   recorded per §8, so this framework has a calibration record rather than a
   plausible story (CLAUDE.md §7).

Until then: full process, zero capital.

---

## 8. Shadow-mode ticket format

At every signal, Claude writes a complete ticket to
`options-expert/log/YYYY-MM-DD-TICKET-N.md` **before the outcome is known**
(CLAUDE.md §9), and commits it. The owner may execute it or not; either way the
outcome is graded against the ticket.

```
# Ticket N — <TICKER> <exp> <strike><C/P>   [SHADOW]
Written: <timestamp ET>, underlying <price>. Outcome unknown at write time.

TRIGGER THAT PRINTED   (which of §4.1–4.4, with the actual closes and participation)
CONTRACT               bid x ask, delta, IV, IV rank, OI, spread
SIZE                   contracts, premium, % of equity, dollar risk to stop
ENTRY                  limit price
STOP                   stop-limit price + the LEVEL that justifies it
INVALIDATION           price level / time deadline / thesis-death condition
TARGETS                first scale level, trail rule
DEADLINES              30-min rule checkpoint; next-open review; event blackouts
EXPECTATION (§9)       what this is expected to do, stated before the result
```

**Grading (per week):** condition discipline first — was every §4 gate met? was
the 30-minute rule honored? did the stop rest? — then P&L. An entry that skipped
a gate is a **C** regardless of outcome. Results roll into
`playbook/PLAYBOOK.md` §6.

---

## 9. What this document does not know

- **2–5 DTE is untested in this account.** Zero trades beyond 1DTE exist. The
  entire premise of §3 is reasoned.
- The holding-time evidence comes from **0DTE/1DTE** trades. Whether the
  30-minute rule transfers to a 3DTE position is unknown — it is adopted anyway
  because the failure mode it prevents (holding losers) is not DTE-specific.
- One week of data, one account, one trader, an unusual tape (monthly OPEX,
  NVDA earnings, Jackson Hole). Small sample.
- The FIFO reconstruction does not perfectly tie to broker P&L. Relative
  patterns are reliable; exact bucket dollars are approximate.
- Sessions 08-26 → 08-28, which contain the two worst days, were **not** worked
  with Claude. Their trades are in the totals but their context is unrecorded.
