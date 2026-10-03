# Results — overnight 1DTE study (computed 2026-10-03; PREREG.md unchanged above its Addendum A)

Scripts: analyze.py (H1-H5), calib.py + calib2.py (real-option calibration). Data: Robinhood.
Every P&L figure is a MODEL estimate except the 5 real SPY nights in section C.

## A. Scored against the pre-registration

| # | Expected | Got (SPY / QQQ) | Verdict |
|---|---|---|---|
| H1 | 2-4 PM direction calls the gap 48-56% | 42.6% (72/169) / 44.0% (74/168) | WRONG, worse than I said. Afternoon selloffs were followed by a gap UP 62% of the time. Contrarian, n=169, one 8-month bull window; not a signal until re-tested out of sample |
| A1 | full-day direction 48-56% (2y) | 48.9% (n=499) / 50.2% (n=502) | Right: coin flip |
| H2 | 180-SMA trend filter helps a little, 52-58% | true 4h SMA180 (Jun-Oct, n=34/40): 61.8% / 47.5%. 2y proxy: 59.1% / 57.8% | No help beyond the base rate. Nights gap up 58.2% / 57.4% of the time anyway; "above the SMA -> calls" just rediscovers that |
| H3 | median gap smaller than option cost | median gap 0.29% / 0.43%; one real ATM SPY 1DTE at the close cost 0.23-0.48% of SPY | Right. My cost guess (0.15-0.25%) was too LOW, and overnight decay was WORSE than I assumed |
| H4 | first 15 min extends a good gap ~half the time | 48.3% (29/60) / 43.1% (25/58) | Right: no reliable "pop". Best price inside 15 min median +0.11% / +0.20% over the open |
| H5 | reversal pays ~50% | by 9:45: 63.2% (43/68) / 59.4% (41/69); 9:45->close: 52.9% / 47.8% | Partly wrong: the first 15 min DID tend to keep going with the gap. But catching it means entering at 9:30 (I-14), and after 9:45 it's a coin flip |

## B. The money question (calendar-time Black-Scholes, fitted to 20 real SPY option prices, rms error $0.31)

- To break even holding overnight and selling at 9:30 you must call the gap direction right
  **~67% (SPY) / ~64% (QQQ)** of nights. Best rule found: "always calls" = 58%.
- Even when you call it right, the trade still loses on **~41-42% of nights**: the gap is too small to
  pay for the overnight decay.
- 2-year model expectancy per trade, % of premium (sell 9:30 / sell 9:45 where 5m data exists):
  2-4 PM signal -23% / -19% (SPY), -21% / -16% (QQQ); day-direction -18% / -12%, -18% / -10%;
  always-call -12% / -7%, -9% / -2%; always-put -23% / -25%, -22% / -21%.

## C. Real SPY 1DTE marks, 5 nights (last-trade prices, 3:55 bar -> 9:45 bar)

Straddle time value: $3.36->$0.60, $4.03->$0.94, $4.27->$1.25, $5.38->$2.47, $5.11->$0.27.
**70-95% of the time value is gone by 9:45.** The 2-4 PM side won 4 of these 5 nights
(+98, +23, +30, -42, +182%); that sample is far too small to outweigh the 169-night H1 result.
Two nights (9/21, 9/22) had no real closing prints and were dropped (interpolated bars).

## D. Limits
Intraday history only reaches 2026-01-30 (5m: 2026-04-01). QQQ IV is VIX x realized ratio (no VXN feed).
Spreads assumed $0.02 SPY / $0.03 QQQ round trip each side, which is optimistic for market orders at the open.
Support/resistance from 4h price action was NOT tested — it needs its own pre-registered level definition.
