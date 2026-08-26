# 2026-08-26 — intraday `gex-levels` does not hold still

Four observations of `/api/stock/TSLA/gex-levels` across one session, taken while
answering a live levels question. Recorded because the result changes how Stage 1
should be used, and because it was not what was expected.

## Pre-registration

Written at 09:36 ET, before the second observation, per `CLAUDE.md` §9:

> The 09:36 frame is thin — 7 minutes of session volume behind a `source: "vol"`
> calculation. Expect it to firm up by 10:00, at which point ~30 minutes of
> volume should give levels stable enough to map against.

**Wrong.** It did not firm up at 10:00, and it was still moving at 10:41.

## The measurement

All four are `source: "vol"`, `date: 2026-08-26`, stamped by the vendor.

| level | 09:36 | 09:44 | 10:05 | 10:41 | range |
|---|---|---|---|---|---|
| `call_wall` | 345.00 | 357.50 | 352.50 | 352.50 | **12.50** |
| `gamma_flip` | 341.50 | 348.70 | 351.59 | 347.28 | **10.09** |
| `gamma_magnet` | 340.00 | 350.00 | 350.00 | 345.00 | **10.00** |
| `put_wall` | 342.50 | 347.50 | 340.00 | 335.00 | **12.50** |

TSLA's own range over the same window was 342.53–351.93 (9.40 points), so the
levels moved about as much as the underlying did.

`gamma_magnet` held from 09:44 to 10:05 and looked like the one trustworthy
number. It then moved 5.00 points by 10:41. Nothing was stable.

## The finding that matters

**At 09:44:** price 349.155, flip 348.70 → price above the flip by 0.45.
**At 10:05:** price 348.41, flip 351.59 → price below the flip by 3.18.

Price fell 0.75. The flip rose 2.89. **Roughly four-fifths of that regime change
came from the model moving rather than from the market moving.**

A trigger written as "5-min close below the gamma flip" would have fired on a
recalculated level while price sat essentially still. That is the operative
danger: not that the number is wrong, but that it is a *moving* number being used
where the process expects a *fixed* one.

## What this is NOT

**It is not evidence the vendor is miscomputing anything.** A volume-weighted
gamma frame recomputing as the day's volume arrives is the endpoint doing its
job. The finding is about **usability as a static level**, not vendor error.
`DATA_LAYER.md` §3e's rule — use the vendor's `gex-levels`, never sum strikes —
stands unchanged and is unrelated.

**It is one session, and that session is an expiry day.** 0DTE positioning churns
hardest into an expiry, so today is plausibly the *worst* case rather than the
typical one. A single expiry-day observation cannot establish what a normal
Tuesday looks like. Do not generalise this into "GEX levels are useless"; the
honest claim is narrower and stated below.

## What changes

1. **A gamma level is never a trigger, a stop, or an invalidation.** Triggers
   stay on price structure that does not move underneath you — PDH/PDL/PDC,
   opening range, VWAP, prior-session levels. This was already the playbook's
   rule (all triggers are 5-min closes through mapped levels); it is now also a
   measured requirement rather than a stylistic preference.
2. **Gamma is a character read, not a coordinate.** Use it for *which regime am
   I in* and *is continuation licensed*, which survives the level wobbling by a
   couple of points. Do not use it for *what price will act as resistance*.
3. **Any gamma level older than ~15 minutes is void.** Re-pull before citing.
4. **Cross-check against the OI-based frame.** `/api/stock/{t}/greek-exposure/strike`
   is the static, open-interest-based, end-of-day view (`DATA_LAYER.md` §3a). It
   does not rebuild intraday, so where the two disagree sharply, the vol frame is
   the one moving. Not yet tested as a cross-check — that is the next experiment.
5. **On expiry days, expect this to be at its worst**, and expect the front-month
   contribution to vanish at the bell.

## Open question for the next session

Is this expiry-day-specific? Take the same four-observation sample on an ordinary
mid-week non-expiry session and compare the ranges. Until that exists, everything
above is one day of evidence and is labelled accordingly.

## Session context, for the record

TSLA gapped down ~2% to a 342.53 low, recovered 6.6 points to 351.93, then faded
to 346.25 by 10:41 (−1.14% vs PDC 350.25). Volume ran 2.20× normal at the open
and decayed to 0.77× by 10:41, with the final minutes under 0.45×. Session flow
turned over the same span: net call premium +1.54M at 10:05 to −2.71M at 10:41,
cumulative `net_delta` −117,517 to −598,463.

**No driver was found for any of it.** The UW news feed carried zero TSLA-tagged
headlines across four checks between 09:36 and 10:41. Per the honesty rules that
is `NO CLEAR DRIVER FOUND`, not an absence of news — this feed is one source and
the gap is as likely to be in our coverage as in the world.
