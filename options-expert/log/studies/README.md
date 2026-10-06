# Studies

One folder per study. Each holds `PREREG.md` (written before results, per CLAUDE.md §9; addenda are
dated and also written before results), `RESULTS.md` (scored against the pre-registration, including
misses), and the scripts. Everything here is UNCALIBRATED (§7).

| Folder | Question | Short answer |
|---|---|---|
| `2026-10-03-overnight-1dte/` | Buy 1DTE late in the day, hold overnight, sell into the open? | No: the gap is a coin flip and ~70-95% of the option's time value is gone by 9:45 |
| `2026-10-03-0dte-vs-1dte/` | Is 1DTE a better vehicle than 0DTE for the in-session trade? | It lost far less when wrong (8 sessions only); 0DTE made ~2x the % when right |
| `2026-10-06-time-exit/` | Sell by 11:00 vs hold to 3:30 (0DTE and 1DTE)? | Pre-registered; data accrues nightly in `../marks/option_marks.csv` from 10/06; evaluated once at 20 sessions |
