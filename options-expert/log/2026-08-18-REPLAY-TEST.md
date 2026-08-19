# Test run — replay of 2026-08-18 from the open

**Purpose:** exercise the spec end to end against a real session and grade it
against what actually happened. This is a **replay, not a live run** — see
"Honesty about this test" before treating any result as validation.

**Note on inputs:** the 9:05 brief itself was not available in this environment
(it is written by the scheduled task on the local machine). The environment
frame below was reconstructed from FMP bars, UW tide and the econ calendar —
the same sources §3b tells the expert to re-pull anyway, because the brief's
numbers are a 9:05 snapshot. Re-running against the real brief would test the
§3a intake path, which this run does not.

---

## Environment as of 09:30 ET

| | SPY | QQQ |
|---|---|---|
| PDH / PDL / PDC (8/17) | 776.78 / 772.51 / **772.67** | 734.58 / 729.27 / **729.87** |
| Open (09:30) | 768.70 | 720.21 |
| Gap vs PDC | **−3.97 (−0.51%)** | **−9.66 (−1.32%)** |
| Opening range (ORH/ORL) | 769.46 / 767.91 | 721.77 / 718.80 |
| Session high | 769.50 @ **09:40** | 722.13 @ **09:40** |
| Session low | 766.96 @ 15:55 | 715.92 @ **11:10** |
| Close | 767.41 | 717.71 |

**Both opened below the previous day's low.** Playbook §0a step 3: a gap below
PDL flips PDL to first resistance and makes gap-and-go vs gap-fill the day's
first question. Neither ever traded back to PDL.

**Volatility** (`volatility/stats`, `volatility/term-structure`):

| | IV | IV rank | RV | 1DTE implied move |
|---|---|---|---|---|
| SPY | 0.133 | 14.4 | 0.135 | 3.09 pts (**0.40%**) |
| QQQ | 0.198 | **34.0** | **0.240** | 4.53 pts (**0.63%**) |

**QQQ was realizing 24.0% against 19.8% implied — the stock was moving more than
its options were charging for.** SPY was priced fair (IV ≈ RV).

**Market tide** — bearish from the first bar and accelerating:

| Time | net call premium | net put premium |
|---|---|---|
| 09:30 | −8.8M | +11.1M |
| 09:40 | −35.9M | +13.8M |
| **09:45** | **−82.0M** | **+41.3M** |
| 09:55 | −139.8M | +90.8M |

**Tripwire B fired at 09:45** (net put premium above the +$40M threshold).
Calls draining while puts woke up — the reversal signature, and it agreed with
price rather than contradicting it.

---

## What the process produced

**Stage 1 — regime.** Negative gamma / gasoline. *Caveat: `gex-levels` has no
historical endpoint, so the regime was read post-hoc. This is the one stage the
replay could not honestly reconstruct.*

**Stage 3 — edge tests.**

- **E2 (aggressor-side flow) — PASSED, and it was the best signal of the day.**
  The tide fired at 09:45, the same five minutes price failed the opening range.
  Flow confirmed price rather than leading it, which is exactly the role §1c
  assigns it.
- **E1 (vol mispricing) — see the failure below.**
- **Vehicle selection: QQQ over SPY.** Three independent reasons, all available
  before 10:00: QQQ gapped 2.6× harder (−1.32% vs −0.51%), QQQ's RV exceeded its
  IV while SPY's did not, and QQQ's IV rank was 34 against SPY's 14. The
  playbook's relative-strength filter says trade the leader, and QQQ was leading
  down.

**Trigger.** Both names printed the same pattern: the 09:40 five-minute candle
poked above the opening-range high and closed back below it — pattern 1, a
rejection wick at resistance, the failed-breakout read. Entry on that close.

## Outcome — graded against real marks

Marks are Robinhood `get_option_historicals`, 10-minute bars, so these are
**achieved contract prices, not modeled ones.**

| Contract | Entry (09:40 close) | Peak (11:00 ET) | Close | Peak | At close |
|---|---|---|---|---|---|
| **QQQ 719P 8/19** | 3.21 | **4.67** | 3.25 | **+45.5%** (+$146) | +1.2% (+$4) |
| SPY 768P 8/19 | 1.84 | 2.37 | 1.92 | +28.8% (+$53) | +4.3% (+$8) |

**The vehicle choice was worth 17 percentage points.** QQQ was the right call
and the spec's own tests identified it.

**Exit timing dominated everything.** Both peaked at 11:00 and gave back the
entire gain by the bell. Held to close, a +45% trade became +1%. The playbook's
prime-window rule and "the plan is selling into strength" would have banked it;
diamond-hands returned nothing.

### Sizing, at the ratified limits

Entry 3.21 → premium **$321**, inside the $400 cap. A 4% risk cap ($49.68) puts
the stop at **2.71**, roughly where QQQ reclaiming the opening-range high would
invalidate the idea. One contract, $50 risk.

Peak **+$146 on $50 risk = 2.9R.**

### …and the process would have refused the trade

Open heat was **$382 (30.8%)** against a 12% ceiling. Stage 6 blocks any new
position. **The heat rule cost a 2.9R winner.**

That is the rule working as designed, not a bug: the book was 2.6× over its
ceiling with three unstopped positions expiring in three days. But it is the
concrete price of leaving heat unmanaged, and it is a better argument for
clearing the book than any abstract one.

---

## FINDING — E1 is wrong for intraday trades

**The implied-move test would have killed this trade.**

E1 as written compares the move the thesis needs against `implied_move_perc`,
and kills anything needing more than ~1.5×. Applied here:

- QQQ needed 0.49% (entry to the 11:10 low). Implied move for 1DTE: **0.63%**.
- Needed **less** than implied → E1's reading is "the market is overpricing your
  scenario, long premium has negative edge" → **kill.**

The trade returned **+45.5%.**

**Why the test was wrong:** `implied_move_perc` is an *expiry* statistic — it
answers "will the underlying finish past the strike." An intraday trade never
holds to expiry; it harvests the **mark**, where P&L is
`Δ × move + vega × ΔIV − θ × time_held`. On a gap-down trending morning the
underlying travelled only 0.49%, but a ~0.45-delta put with vol expanding and
90 minutes of theta paid gained 45%. Direction, speed and IV all paid; only the
distance-to-expiry question said no, and that question was not being asked.

**Fix applied to `SKILL.md`:** E1 now has two modes, and the card must name
which is in force —

- **Hold-to-expiry:** unchanged. Needed move vs implied move; kill above ~1.5×.
- **Intraday:** the test is not distance, it is **speed against theta**.
  Estimate `Δ × expected_move × 100` against `θ × (expected_hours / 6.5) × 100`
  and require the delta term to clear the theta term by a stated multiple.
  IV direction is part of the thesis, not a footnote: buying premium into an
  expanding-vol break is a different trade from buying it into a quiet drift,
  and `RV > IV` (as QQQ had) is evidence the expansion is real.

**Second fix:** vehicle selection is promoted from a passing mention in E2 to a
required step, because it was worth 17 points here. When two correlated
instruments express the same thesis, compare gap size, `RV` vs `IV`, and IV rank
before choosing, and state the comparison on the card.

---

## Honesty about this test

- **n = 1.** One session, one direction, on a day that trended cleanly from the
  open. It says the process *can* find a real trade; it says nothing about hit
  rate. Everything remains **UNCALIBRATED.**
- **Two stages could not be honestly replayed.** `gex-levels` has no historical
  endpoint, so Stage 1's regime read was reconstructed after the fact.
  `volatility/stats` is dated 2026-08-18 but was fetched after the close — the
  values may have been computed intraday, so treating them as 09:30 inputs is an
  assumption, not a fact.
- **Entry and exit were chosen with hindsight available.** The 09:40 trigger
  follows a written rule, which limits the damage, but the 11:00 exit is where
  the peak happened to be. A live run must define the exit *before* it happens —
  which is precisely why §7 requires the resting limit at entry.
- **No slippage or commission** is modelled. Entry is a 10-minute bar close, not
  a fill.
- **The brief was not used.** The §3a intake path is untested.
