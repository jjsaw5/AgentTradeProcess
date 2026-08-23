# RTH probe — pre-registration

`CLAUDE.md` §9: state what a test is expected to show **before** running it, and
record what it actually showed — including when the test embarrasses the design.
Written 2026-08-22, before the first live sample. **Do not edit the predictions
after seeing results.** Findings go in the dated files beside this one.

---

## Why an RTH probe exists at all

`tesla/DATA_LAYER-TSLA.md` was verified on a Saturday. Every liquidity number in
it is a **2026-08-21 closing snapshot**, and closing spreads are the widest of
the day. Six things the spec depends on cannot be measured with the market shut:

| # | What | Why only RTH answers it |
|---|---|---|
| 1 | The 5% spread gate | The gate that decides whether *any* TSLA trade happens, tested only against closing quotes |
| 2 | The ~185,000 volume floor | Measured from historical bars; never watched arm and disarm live |
| 3 | Feed freshness | A lag figure is meaningless when every feed is 25 hours stale |
| 4 | The E5 skew anomaly | One more print either confirms −0.6636 or clears it |
| 5 | Intraday regime drift | How often `/tsla-scan` must re-pull `gex-levels` |
| 6 | Real 0DTE theta burn | The number E1 Mode B is built on |

Each prediction below is falsifiable and names what would change the spec.

---

## P1 — Spread gate. **Expected: the gate is generous, not binding.**

Friday's close had near-money at 4.8–6.6% and ITM at 11.9–15.2%. Closing prints
on a 41,489-volume contract are not representative.

**Predict:** median spread on 0.30–0.60 delta TSLA 0DTE contracts, sampled
10:00–15:00, runs **1.5–3.0%** — comfortably inside the 5% gate.

**Predict also:** ITM (>0.70 delta) stays **above 5%** even intraday, so the
closing 11–15% is only partly an artifact.

**Falsified if:** median near-money spread exceeds 4%. Then the gate is
near-binding in live conditions and either the threshold is wrong or the module
must accept that most contracts fail it — a finding either way, and one that
changes `/tsla-scan` Stage 5.

## P2 — Volume floor. **Expected: arms in the doldrums, clear in the prime window.**

**Predict:** the ~185,000 floor is **clear 09:45–11:30** and **arms at least
once during 13:00–14:30** on a normal session.

**Falsified if:** it arms during 09:45–11:30 on a normal session. The floor
would then be blocking the exact window the process exists to trade, and the
threshold comes down.

**Also falsified if:** it never arms in five sessions — set too low to filter
anything, which makes it decoration.

## P3 — Feed freshness. **Expected: all three legs live to within ~2 minutes.**

**Predict, during RTH:** FMP 5-min bar lag **< 300s** (a bar in progress), UW
`spot-exposures` **< 120s**, UW `net-prem-ticks` **< 120s**.

**Falsified if:** any exceeds 900s while the market is open. The spec's
"re-pull anything you are about to trade on" assumption would be false, and a
delayed feed used as a live one is the kind of error that reads as a bad
decision rather than a bad input.

Note `gex-levels` carries **no timestamp**, so its freshness is unverifiable
from the payload — a standing limitation, not something this probe can close.

## P4 — E5 skew. **Expected: the 2026-08-21 print was an OPEX artifact.**

Five sessions sat in −0.010 to −0.030; 2026-08-21 printed **−0.6636** on an
expiration Friday.

**Predict:** the next print returns to the −0.010 to −0.030 band, confirming an
artifact. The caveat in `DATA_LAYER-TSLA.md` §7f is then narrowed to "OPEX
Fridays produce bad skew prints" rather than a general warning.

**Falsified if:** the value stays at that magnitude. Then −0.66 is real, the
band was wrong, and E5's whole scale needs re-reading.

**Falsified differently if:** it prints a *third* value unlike either. Then the
series is unreliable on TSLA and E5 comes out of the process until it is
understood.

## P5 — Regime drift. **Expected: a pre-open read survives the morning.**

**Predict:** `gamma_flip` moves **less than $5** between the 09:47 and 13:33
samples on a normal session.

**Falsified if:** it moves more. Then a pre-open regime read is stale by
mid-morning and `/tsla-scan` must re-pull `gex-levels` on every single run
rather than trusting `/tsla-open`'s.

## P6 — Theta. **Expected: brutal, and worse than the SPY precedent.**

Friday's 2DTE ATM showed θ −1.017 on a $3.125 mark = **−32.6%/day**.

**Predict:** an ATM TSLA 0DTE contract loses **more than 50%** of its mark
between 09:47 and 15:03 on a session where TSLA finishes within ±0.5% of its
09:47 price.

**Falsified if:** it loses less than 30%. The "a thesis that needs two hours is
a losing trade" rule in `/tsla-scan` E1 would then be overstated, and the
required delta-to-theta multiple comes down.

---

## Sampling

Three samples per weekday, chosen to cover the windows that matter rather than
to be evenly spaced:

| Sample | ET | Why |
|---|---|---|
| A | 09:47 | after the opening range forms — the entry window |
| B | 13:33 | inside the doldrums — worst-case spreads and the volume floor |
| C | 15:03 | just past the 15:00 decision bell — **exit** liquidity, which matters most given the 15:30 force-close |

Sample C is the one nobody thinks to take and the one a 0DTE process most
needs: a contract you cannot exit at 15:03 is a contract the broker exits for
you at 15:30.

## Stopping rule

Five clean trading sessions, or ten if any prediction is ambiguous. Then each
prediction is marked **confirmed / falsified / inconclusive** in a summary
appended here, the spec is amended where falsified, and the amendments are a
separate commit from this file so the original design stays legible.

**No prediction above may be revised after the first sample.** A post-hoc
review, if one is warranted, goes in its own document.
