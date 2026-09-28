# Monday Edge

Measures what SPY and QQQ do **after** a post-weekend open, given the size of
the gap and the kind of weekend news behind it. Only patterns that survive an
out-of-sample holdout become 0DTE–4DTE trade ideas.

Nothing here trades. The tool reads FMP and Unusual Whales, writes CSV and
HTML, and stops. The human executes every order (CLAUDE.md §2).

## Question answered

Given this weekend's gap and news, what usually happens after 9:30 on Monday,
and through Friday?

- Instruments: SPY, QQQ (configurable).
- Horizons: Monday close (0DTE) … Friday (4DTE). Nothing beyond.
- Sessions: every trading day that follows 3+ calendar days off (normal and
  long weekends; a holiday Monday shifts the session to Tuesday).
- Not in scope: orders, option pricing or P&L, intraday signals after the
  first hour.

## Setup

```
cd monday_edge
pip install -r requirements.txt        # requests, pandas, numpy
cp .env.example .env                   # add FMP_API_KEY (required), UW_API_KEY (optional)
```

`anthropic` is optional and only needed for `--llm`. Keys reach code through
the environment only; `.env`, `cache/` and `output/` are git-ignored.

## Commands

```
python run.py study [--llm] [--start YYYY-MM-DD]     # ~5y history → output/study_report.html, patterns.csv, weekends.csv
python run.py today [--llm] [--gap SPY=0.45 --gap QQQ=0.70]   # Monday pre-open → output/brief_YYYY-MM-DD.html
python run.py study --mock [--seed N]                 # synthetic world → output/mock/
python run.py today --mock
python acceptance.py                                  # the spec §11 acceptance test over seeds 7, 11, 23, 42, 99
```

The first real `study` is several thousand API calls; every historical
response is cached under `cache/` (SHA1 of URL + params, key excluded), so
re-runs are cheap. `today` fetches its news, posts and quote uncached.

## How it works

1. **Sessions** (`sessions.py`): a session is day `d` whose previous trading
   day `p` is 3+ calendar days back. News window `p 16:00 ET → d 09:30 ET`.
2. **Context**, known before the open: gap %, Friday return, prior-week
   return and its direction vs the gap, Friday VIX regime, Friday GEX regime
   (UW), Friday implied 1-day move (UW), and the weekend's news tags.
3. **Outcomes**, measured from the open: signed returns at k=0..4 (positive =
   continued with the gap), fill of Friday's close over days 0..k, MFE/MAE,
   and from 5-minute bars: minutes to fill, fill within the first hour,
   opening-range (first 30 min) hold and break/follow.
4. **Tagging** (`tagger.py`): keyword rules give a `category`, a `risk_tone`
   and a Trump `action` / `statement` / `none` mode. `--llm` sends titles only
   to an Anthropic model, caches the answer, and merges it over the rules.
5. **Analysis** (`analyze.py`): the newest 30% of weekends are held out. Each
   group is compared against a **size-adjusted baseline** (what its own mix of
   flat/small/large gaps would give), on four metrics: same-day fill,
   close-with-gap, 0DTE return, 4DTE return. `confirmed` needs n ≥ 15 and
   |z| ≥ 2 in discovery, then the holdout (n ≥ 5) agreeing with |z| ≥ 1. Pure
   noise passes that about 0.7% of the time; the report shows the eligible
   test count and the implied fluke count next to the confirmed list.
6. **Reports** (`report.py`): self-contained HTML, light/dark, phone-scrollable.

## Reading the output honestly

- Returns are **underlying moves, not option P&L**.
- SPY and QQQ are highly correlated: a pattern in both is **one** finding.
- Rows with n under ~15 are anecdotes. `discovery only` means the holdout was
  too small to say anything; `failed holdout` means it said no.
- Everything here is history. It is UNCALIBRATED as a live process until
  Mondays are logged against their brief and reviewed (CLAUDE.md §7).
- Rule tagging counts keywords. Compare a category split with `--llm` before
  believing it.

## Known limits

- **Early-close Fridays:** the window still starts at 16:00 ET, so news
  between 13:00 and 16:00 on those days is lost. Accepted for v1.
- **UW plan depth:** history endpoints may return 403 on lower tiers. The
  tool records the gap in the report's data notes and leaves the field
  `n/a`; it never crashes and never substitutes a number.
- **FMP news timezone:** `publishedDate` is naive; the zone is
  `FMP_NEWS_TZ` (default America/New_York). Verify once on your account.
- **Presidential posts** come from UW `potus/posts`. Market relevance uses
  the feed's flag when present, else a keyword fallback.

## Files

| File | Role |
|---|---|
| `config.py` | settings + `.env` loader (no extra dependencies) |
| `clients.py` | FMP + UW clients, disk cache, 429 backoff, 403 plan-limit notes |
| `sessions.py` | session discovery, outcomes, buckets |
| `tagger.py` | rule tagger, optional LLM tagger, tone-vs-gap |
| `build.py` | one row per session × ticker → `output/weekends.csv` |
| `analyze.py` | split, size-adjusted baseline, z/t tests, status, analogs |
| `report.py` | study report and today brief (HTML) |
| `mock_data.py` | synthetic world with planted effects |
| `acceptance.py` | spec §11 acceptance test |
| `run.py` | CLI |

## Later (not in v1)

Pre-market ES/NQ path features, 0DTE net flow in the first 30 minutes as a
live filter, option P&L replay from UW contract history, a scheduled Monday
8:45 ET run, and a 12-week live log before trading from it.
