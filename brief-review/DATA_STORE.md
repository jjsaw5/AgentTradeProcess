# Scoring database (Turso / libSQL)

**Added 2026-08-20 at the owner's request.** The review process's structured
history lives in a Turso database so accuracy can be queried across time
instead of re-read from markdown. The markdown reviews in `reviews/` remain
the evidence record; the database is the *queryable index* of them. On any
disagreement, the review file wins and the row gets fixed.

- **Database:** `briefscoring-jjsaw5` (`aws-us-east-2.turso.io`)
- **Access:** HTTP pipeline API (`POST $TURSO_URL/v2/pipeline`), token via
  `Authorization: Bearer`. Helper: `tools/scoredb.sh`.
- **Credentials:** `TURSO_URL` and `TURSO_TOKEN` come from the environment or
  a gitignored `.env` — referenced by variable name only, per `CLAUDE.md` §6.

## What is stored — and what is deliberately not

**Stored:** per-brief rubric scores, per-radar-item grades, per-ticker
watchlist outcomes, the improvement ledger, open items, and a
**credentials registry that holds metadata only** (name, storage location,
exposure status) — never secret values.

**Not stored: API keys.** The owner asked to keep API keys in this database;
that collides with `CLAUDE.md` §6 ("keys live only in `.env` or the
deployment's secret manager … a key written down anywhere else is
compromised"), which the owner ratified. A remote database reachable by
bearer token is exactly the "anywhere else" §6 warns about: anyone holding
the DB token would hold every key in it. So the registry records *where each
key lives and whether it is exposed*, which is the useful, queryable part —
the values stay in `.env`/secret managers. If the owner wants raw keys stored
here anyway, that is a §6 amendment to make explicitly in `CLAUDE.md`, not a
quiet insert.

**Exposure note (standing, per §6):** the Turso token itself was pasted into
a session transcript on 2026-08-20 during setup. By §6's own rule it is a
known exposure until rotated (`turso db tokens revoke` / re-issue). Recorded
in `credentials_registry` with status `KNOWN EXPOSURE — ROTATE RECOMMENDED`.

## Schema (v1, 2026-08-20)

| Table | Grain | Notes |
|---|---|---|
| `brief_reviews` | one row per brief date | The scorecard row: F/O/M/G counts and grades, radar roll-up, watchlist precision/recall, top gap. `status` = GRADED or PENDING. |
| `radar_items` | one row per §9 card | `grade` ∈ CONF-PAID / CONF-FAILED / INVALIDATED / NO-TRIGGER / OPEN / UNGRADEABLE, with evidence text. |
| `watchlist_events` | one row per (date, ticker) scored | `flagged` 0/1, close-to-close `move_pct` (NULL when unmeasured — never 0.0 for missing, §4), `outcome` ∈ PRECISION-HIT / PRECISION-MISS / RECALL-CAUGHT / RECALL-MISS. |
| `improvements` | one row per ledger item | Mirrors `IMPROVEMENTS.md` (PROPOSED / RATIFIED / REJECTED). |
| `open_items` | one row per unresolved thesis | With `resolve_by` deadline and eventual `resolution`. |
| `credentials_registry` | one row per credential | **Metadata only.** Name, storage location, exposure status, notes. |

## Workflow

Each review session (SKILL.md → Output) now ends with a DB sync: upsert the
`brief_reviews` row, its `radar_items` and `watchlist_events`, any
`improvements`/`open_items` changes, and flip resolved OPEN items. Sentinel
vocabulary applies inside text fields exactly as in the markdown.

Useful queries live in the helper header, e.g. cumulative hit rates:

```sql
SELECT SUM(radar_conf_paid) || '/' || SUM(radar_conf_fired) AS confs_paid,
       SUM(wl_precision_hits) || '/' || SUM(wl_precision_total) AS precision,
       SUM(wl_recall_caught) || '/' || SUM(wl_recall_total) AS recall
FROM brief_reviews WHERE status='GRADED';
```
