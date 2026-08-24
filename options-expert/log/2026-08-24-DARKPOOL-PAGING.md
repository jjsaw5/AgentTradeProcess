# 2026-08-24 — `/api/darkpool/{ticker}` paging, measured

Probe run against the live API at ~12:36 ET on 2026-08-24 (Monday, market open),
ticker TSLA. Purpose: settle the paging behaviour that `SKILL.md` E2b and
`DATA_LAYER.md` had both flagged `UNVERIFIED` when the layer shipped that
morning.

## Pre-registration

Stated before the calls were made, per `CLAUDE.md` §9:

> Expected to find that `limit` is honoured, as it is on `/darkpool/recent`, and
> that a large enough limit returns a full session of prints. Expected E2b's
> "% of 30-day ADV" denominator to work as written.

**Both expectations were wrong.** What follows is what the API actually did.

## What was run

| Request | Status | Rows | `executed_at` span (ET) |
|---|---|---|---|
| `/darkpool/TSLA` | 200 | **500** | 12:07:29 – 12:34:43 (27.2 min) |
| `/darkpool/TSLA?limit=200` | 200 | 200 | — |
| `/darkpool/TSLA?limit=2000` | **422** | — | — |
| `/darkpool/TSLA?date=2026-08-24&limit=500` | 200 | 500 | 12:10:28 – 12:36:33 (26.1 min) |
| `/darkpool/TSLA?limit=500&page=1` | 200 | 500 | 12:10:28 – 12:36:33 (26.1 min) |

The `422` body names the cap outright:

```
Invalid query input(s): limit=2000 (Invalid limit 2000 - limit must be
smaller than 500. valid example: limit=10)
```

## Findings

1. **`limit` is honoured, and capped at 500.** Above that the request is
   rejected with a `422` rather than silently clamped — a genuinely good failure
   mode, and the opposite of the §3d trap.
2. **`page` is accepted and ignored.** `page=1` returned the identical window as
   the call without it. There is no pagination on this route.
3. **`date` is accepted and ignored.** Passing today's date changed nothing;
   the two calls differ only by the seconds that elapsed between them. This
   route cannot be walked backwards through a session, or to a prior day.
4. **Therefore the route returns the most recent ≤500 prints and nothing else.**
   On TSLA that was **27 minutes**. On a less active name it would reach
   further back, and on a more active one, less — the window length is a
   property of the tape, not of the request, and it is never asserted by the
   response.

Note that 2 and 3 are the §3d silent-failure pattern in a new costume: not an
empty array, but a *plausible full-looking response* to a parameter that did
nothing. A caller who assumed `page` worked would have paged forever through
the same 500 rows and called it a session.

## The defect this exposed in E2b

E2b, as written and committed earlier the same day, required aggregate block
size to be expressed as **a percent of 30-day average share volume**. That is a
one-day denominator. The numerator available is 27 minutes.

On this TSLA data the broken metric read **0.82% of 30d ADV** — a number that
looks small and specific and means nothing at all, because the two sides of the
ratio describe different lengths of time. It is the same class of error as the
2026-08-18 GEX incident: a fact about the response wearing the costume of a fact
about the market.

**Fixed in the same commit** by matching the rate to the window:

```
normal_rate  = ADV30 / 390                            # shares per session minute
off_lit_rate = dark_shares / (normal_rate * window_min)
```

On this data: 307,064 shares over 27.2 minutes against a 96,221 sh/min norm →
**11.7%** of the name's normal *total* volume for an equal span. The denominator
includes lit volume and UW's feed may not carry every off-exchange print, so the
figure is not dark-versus-dark and must not be described as such.

**It is reported, never thresholded.** One name on one day is not a baseline,
and nothing in this repository yet establishes what a normal off-lit rate looks
like for any ticker. Building that is future work.

## Incidental: the REST payload schema is confirmed

Fields observed on every row: `ticker`, `price`, `size`, `premium`,
`executed_at`, `nbbo_bid`, `nbbo_ask`, `nbbo_bid_quantity`, `nbbo_ask_quantity`,
`market_center`, `volume`, `canceled`, `sale_cond_codes`, `ext_hour_sold_codes`,
`trade_code`, `trade_settlement`, `trf_executed_at`, `tracking_id`.

This matches what `DATA_LAYER.md` §3a already recorded, and `uw_stream.py`'s
`_dp_fields` candidate keys all hit on their first choice. That is evidence for
the socket parser, **not proof**: this is the REST route, and the
`off_lit_trades` websocket payload has still never been observed.

## Mid-split base rate, recorded without interpretation

The 500-row window classified **219 above / 83 at / 198 below mid**, 0
unresolved. Near-balanced, which under E2b's own reading table is
`NA_no_data` — nothing to cite.

Recorded here only so a future baseline has a first data point. One window on
one liquid name on one day does not establish a base rate, and this number must
not be used as a reference level until many more exist.
