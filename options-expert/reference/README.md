# Vendored Unusual Whales reference

Upstream documents, copied here so the expert loads them at runtime instead of
depending on a network fetch mid-session. **Do not edit the vendored bodies** —
re-fetch to update, and record corrections in this file rather than in the copy.

| File | Upstream | Fetched |
|---|---|---|
| `uw-api-skill.md` | https://unusualwhales.com/skill.md | 2026-08-18 |
| `uw-websocket-skill.md` | https://unusualwhales.com/skills/websocket.md | 2026-08-18 |
| `uw-api-usage-skill.md` | https://unusualwhales.com/skills/uw-api-usage-monitor-skill.md | 2026-08-18 |

The full machine-readable spec is `GET https://api.unusualwhales.com/api/openapi`
(~957 KB YAML, 207 paths). It is the authority. Fetch it rather than guessing.

## Corrections — read before trusting `uw-api-skill.md`

**1. Its "Strict Whitelist" claim is false as stated.** The document says:

> You may **ONLY** use endpoints listed in the "Valid Endpoint Reference"
> section below. If a URL is not on that list, it does not exist.

That is an **anti-hallucination guardrail, not an inventory.** The list covers
26 endpoints; the API documents **207**. Endpoints verified working despite
being absent from it include `iv-rank`, `gex-levels`, `max-pain`,
`volatility/stats`, `variance-risk-premium`, `historical-risk-reversal-skew`,
`ohlc/{candle_size}`, `flow-per-strike-intraday`, `greek-flow`, `nope`,
`sector-tide` and the 15 websocket channels.

Correct reading: **the whitelist is safe-by-default, the OpenAPI spec is true.**
An endpoint's absence from the whitelist is not evidence it is missing — probe
it. Its *blacklist* of hallucinated paths (`/api/options/flow`,
`/api/stock/{t}/flow`, anything under `/api/v1/` or `/api/v2/`, `apiKey=` query
params) remains accurate and useful.

**2. Two behaviours it does not warn about**, both of which return a confident
wrong answer with no error — see `../DATA_LAYER.md` §3d and §3e:

- A bad parameter value yields `HTTP 200` with `{"data": []}`, indistinguishable
  from a genuine no-results response.
- Default page sizes silently truncate. `spot-exposures/strike` returns ~50 rows
  ascending by strike, which on SPY stopped below spot and produced a wrong
  regime read until `limit=500` was passed.
