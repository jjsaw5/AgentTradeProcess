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

## P7 — reserved

Not yet written. `tesla/PROPOSED-RANGE-GATE.md` names P7 as the slot for the
range gate's forward test; it is recorded here so the numbering does not
collide, and stays empty until that proposal is ratified or withdrawn.

## P8 — the green stop. **Expected: stopping while green beats continuing.**

Registered **2026-08-26**, before any session has been traded under it.
Proposal and evidence: `tesla/PROPOSED-GREEN-STOP.md`. **Warning-only** — it
kills nothing during the test.

Backtest across 62 realized closes over 7 sessions (2026-08-14 → 2026-08-26):
stopping at the 90-minute mark when green turns **+$888 into +$1,245**. It beats
the actual result at **11 of 11** cutoffs from 45m to 240m; the unconditional
version beats it at **1 of 11**. The effect is concentrated in two sessions
(08-24 +$113, 08-26 +$264) which are the two that prompted the analysis.

**Predict:** across the next **five** sessions in which the mark-inclusive
session P&L is **positive at 11:00 ET**, the P&L accumulated **after** 11:00 is
**negative in aggregate**.

**Falsified if:** that post-11:00 aggregate is **positive**, or if it is
negative by less than **$50** in total — an effect that small is
indistinguishable from commission-scale noise at this sample size and would not
justify a gate that ends the session before noon.

**Inconclusive if:** fewer than five green-at-11:00 sessions occur in the test
window, or if a single session contributes more than 70% of the post-11:00
total. In either case the window extends rather than the prediction changing.

**Measurement, fixed now so it cannot be chosen later:**

- "Green at 11:00" means **realized P&L plus the mark of any open position** at
  11:00:00 ET, read from `get_pnl_trade_history` and `get_option_positions` /
  `get_option_quotes`. Not realized-only — §5 of the proposal explains why.
- Post-11:00 P&L is attributed by **entry** time, not exit time. Positions
  opened before 11:00 and closed after belong to the pre-11:00 bucket.
- Sessions with **zero** trades after 11:00 count as $0 and are included.

**Nothing above may be revised once the first session is recorded.**

## P9 — the unconditional stop, **account-wide**. **Expected: afternoon trading is net negative.**

Registered **2026-08-26**, hours after P8 and before any session has been traded
under either. Evidence: `tesla/PROPOSED-GREEN-STOP.md` **AMENDMENT**.
**Warning-only** — it kills nothing during the test.

**Scope: the whole brokerage account, all symbols.** This is the first
prediction in this file that is not TSLA-only, and it is here because this is
the repository's only pre-registration ledger. It is flagged rather than filed
elsewhere so the scope difference stays visible.

*Note on P8, which is NOT amended:* P8 was registered without an explicit scope
line and is read as **TSLA-scoped** by the location of its evidence. That
ambiguity is disclosed here rather than fixed by editing a registered
prediction (§9).

Why a second prediction rather than a correction to the first: across **153
closes over 16 sessions** the *conditional* (green) stop **loses $246** while
the *unconditional* stop **saves $638**. The seven-day TSLA sample behind P8
showed the reverse. Rule A is positive at 8 of 9 cutoffs with a monotonically
decaying edge, and its leave-one-day-out edge (+$193 to +$1,324) never changes
sign; Rule B's does.

**Predict:** across the next **ten** trading sessions, aggregate realized P&L
from positions **entered after 11:00 ET, all symbols**, will be **negative**.

**Falsified if:** that aggregate is **positive**, or negative by less than
**$100** in total — an effect that small does not justify closing the book
before noon.

**Inconclusive if:** fewer than ten sessions contain a post-11:00 entry, or if a
single session contributes more than **70%** of the absolute total. The window
extends; the prediction does not change.

**Measurement, fixed now:**

- Attribution is by **entry** time, from `get_option_orders` /
  `get_equity_orders` — not by exit time. A position opened before 11:00 and
  closed after belongs to the pre-11:00 bucket and is excluded.
- Expirations (closes timestamped at 16:00 ET with price 0) are **excluded**;
  they have no entry decision on the day they settle.
- Sessions with zero post-11:00 entries count as **$0** and are included in the
  count of ten.
- All symbols, all asset classes the account trades.

**Nothing above may be revised once the first session is recorded.**

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
