# Pre-registration — overnight 1DTE study (written 2026-10-02 22:04 ET, before any data is pulled)

Owner idea (10/03): buy a 1DTE SPY/QQQ option mid-afternoon or near the close in the
day's direction, hold overnight, sell into the first 15 minutes if the open goes our
way; if wrong, close and re-enter 0DTE the other way.

Questions and what I expect BEFORE looking:

H1  Afternoon direction (2:00 PM -> 4:00 PM close) predicts the sign of the next
    day's open gap. EXPECT: close to a coin flip, 48-56%.
H2  Same, filtered by trend (close above/below the 180-period SMA on 4-hour bars).
    EXPECT: small improvement at best, 52-58%; not enough alone.
H3  Size: median |overnight gap| vs the cost of an at-the-money 1DTE option
    (about half the 1-day expected move: SPY ~0.15-0.25%, QQQ ~0.25-0.35%).
    EXPECT: median |gap| is SMALLER than the option's cost, so a correct-direction
    hold often still loses money after overnight decay.
H4  When the gap goes your way, does the first 15 minutes give a better exit than
    the 9:30 open? EXPECT: roughly half the time it extends, half it gives back
    (no reliable "first 15-minute pop").
H5  "If wrong, reverse": after a gap against you, does the first 15 minutes keep
    going against the original direction (reversal pays)? EXPECT: ~50%, not reliable.

Data: Robinhood daily, hourly, 4-hour and 5-minute SPY/QQQ bars, regular hours.
Cost model is an ESTIMATE from expected moves, not real option marks; stated as such.

## Addendum A — written 2026-10-03, after checking data COVERAGE, before computing any result

Coverage found (the "200 is not a success" check):
- Robinhood intraday history is shallow. 30-minute bars are real only from 2026-01-30
  (earlier bars come back `interpolated: true` with placeholder prices — e.g. SPY "683"
  in Oct 2024). Native hourly bars are real from 2025-12-22 but have holes (missing
  9:30 half-hour, some hours with ~10k volume). Native 4-hour bars are real from
  2025-11-03 but many days have only ONE 4-hour bar. Native hourly/4-hour are NOT used.
- 5-minute bars real 2026-04-01 -> 2026-10-02. Daily bars real 2024-10-01 -> 2026-10-01.

Plan changes (declared before results):
- H1 uses 30-minute bars (2026-01-30 -> 2026-10-02), 2:00 PM open -> 4:00 PM close.
- H2 "4-hour 180 SMA": 4-hour bars are BUILT from 30-minute bars (9:30-13:30, 13:30-16:00,
  the usual 2-bars-a-day split), SMA of last 180 such closes = ~90 trading days. That only
  exists from ~June 2026, so H2 is ALSO run on a 2-year proxy: 90-day SMA of daily closes.
- A1 (new, secondary): full-day direction (open -> close) predicts next open gap sign,
  2 years of daily bars. EXPECT 48-56%, same as H1.
- H3 cost: Black-Scholes ESTIMATE, IV = VIX (SPY) / VXN (QQQ) daily close if available,
  ATM 1DTE bought at the 4:00 PM close, valued at next-day 9:30 open and 9:45. Two time
  conventions bracket the answer (calendar time; trading time with overnight = 0.25 session).
  EXPECT: a correct-direction gap of median size does NOT cover overnight decay + spread
  on a majority of nights; strategy expectancy <= 0 before spreads.
- H4/H5 on 5-minute bars (2026-04-01 -> 2026-10-02).
