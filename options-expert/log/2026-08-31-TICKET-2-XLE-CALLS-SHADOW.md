# Ticket 2 — XLE 9/4 calls  [SHADOW — NOT TRADED]

**Written 2026-08-31, 09:22 ET. XLE $63.73 premarket, Friday close 62.68.
Market not yet open. Outcome unknown at write time (§9).**

**This is a paper ticket.** No capital is committed. It exists to test whether
the `SWING_STRATEGY.md` framework produces good options decisions *before* the
account is funded to trade them — the calibration record CLAUDE.md §7 has been
asking for since 2026-08-18.

**Hypothetical account: $1,500** (the `SWING_STRATEGY` §7 funding gate).
Real account is $205.03; the live version of today's idea is Ticket 1 (shares).

---

## Thesis and levels

Identical to Ticket 1 — same catalyst (US–Iran strikes, WTI +3.1%), same levels
(Friday high **62.74**, call wall **63.00**, flip **63.51**, magnet 62.50,
upside flip **64.46**), same 95%-call-sided Friday USO flow. See Ticket 1 for
sourcing. **This ticket differs only in instrument and sizing** — deliberately,
so that when both are graded we learn whether the options wrapper adds anything
over shares on the same read.

## Contract selection rule

Chosen at entry, not now — premarket option quotes are `NA_no_data` (the 9/4
63C showed 0.49 × 0.71 with $0.69 of intrinsic already, a stale Friday quote).

| Parameter | Rule |
|---|---|
| Expiry | **2026-09-04** (4 DTE at entry) — `SWING_STRATEGY` §3 |
| Type | Call |
| Delta target | **0.45–0.60** (slightly ITM) — the 8/19 moneyness evidence |
| Expected strike | **63.00** (OI 13,518, the deepest book) |
| Spread gate | Reject if ask−bid > 2% of mid at entry |
| IV context | XLE IV 24.2%, rank 41.7, RV 22.9% — middling, not cheap |

**Do not substitute a cheaper OTM strike.** Affordability is not a reason;
far-OTM weeklies are the structure that has lost 5+ times in this account.

## Size (hypothetical $1,500)

Formula, filled at entry:

```
R_underlying = entry_price − 62.70           (stop distance)
R_option     = R_underlying × delta × 100    (risk per contract)
contracts    = floor( 1500 × 0.04 / R_option )
```

Worked at an assumed 63.25 entry, delta 0.55:
`R_underlying 0.55 → R_option ≈ $30/contract → 60/30 = 2 contracts.`
Premium ≈ **$260** (17% of the hypothetical account), **risk to stop ≈ $60**
(4.0%) — inside CLAUDE.md §5's `MAX_TRADE_RISK_PCT` and `MAX_TRADE_PREMIUM_USD 400`.

**The premium cap is conditional on the resting stop existing.** Without a
working stop the risk is the full $260 and the position is oversized — do not
take it.

## Entry condition — identical gates to Ticket 1

1. No entry before **10:00 ET**.
2. Do not buy the open.
3. Retest entry only: pullback into **63.00–63.51**, two consecutive 5-min
   closes above the pullback low, participation ≥0.40.
4. **Flow gate:** re-pull XLE net-premium ticks at entry; persistent adverse
   ticks veto regardless of price.
5. **Re-pull `gex-levels` at entry** and treat any pull before ~10:30 as
   provisional (the 8/25 evidence — TSLA's wall read 387.5 then 352.5 in 19 min).
6. No retest into the zone = **no trade**.

## Stop, invalidation, management

- **Resting stop-limit** on the option, 15-cent buffer, priced off underlying
  **62.70**, placed in the same action as entry.
- **Time invalidation:** below 62.74 at noon → out, thesis dead (brief §9).
- **Overnight:** 4 DTE buys one overnight, not three. If the thesis has not begun
  working by Tuesday's open, exit regardless of P&L (`SWING_STRATEGY` §5c).
- **30-minute rule:** red at 30 minutes and not stopped → close.
- **Give-back rule — HARD:** at **+50% on premium**, half comes off and the stop
  moves to entry, permanently. A position that has been +50% may never close red.
  (Origin: 2026-08-28 SPY 771C, ~+$400 open profit exited at +$202.)
- **Event note:** nothing scheduled today beyond Dallas Fed 10:30 (minor). The
  9/4 expiry sits ON Friday's jobs report (8:30 AM, high impact) — **this
  position must be closed before Thursday's close.** The thesis is an oil
  gap-hold, not a payrolls bet.

## Pre-registered expectation (§9)

**I expect this ticket to be worse than Ticket 1 on the same read**, and I want
that on the record before the outcome. Reasoning: the thesis is multi-day, the
option decays daily, XLE's IV rank at 41.7 is not a discount, and the 4DTE
wrapper forces an exit before Friday for reasons that have nothing to do with
oil. If the shares work and the calls do not, the framework's DTE assumption
(`SWING_STRATEGY` §3, marked `[REASONED]`) is the thing that failed.

- **If right:** retest holds after 10:00, XLE works toward 64.46, the 63C gains
  roughly $0.55 × 0.55 delta ≈ $0.30 (+25% on a $1.20 contract) on a 1-point move.
- **If wrong:** no retest prints and the correct outcome is **no trade** — same
  as Ticket 1.
- **Grading:** condition discipline first, then P&L, then the Ticket 1 vs
  Ticket 2 comparison, which is the real experiment.

## Status

`SHADOW — NOT TRADED.` To be marked up with the actual outcome at the close,
whether or not the condition printed.
