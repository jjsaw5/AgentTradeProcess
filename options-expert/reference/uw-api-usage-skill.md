---
name: uw-api-usage-monitor
description: Monitor Unusual Whales API usage by inspecting response headers from any successful REST API call. Use this skill whenever a user or agent asks about API usage, rate limits, remaining quota, daily request counts, how close they are to hitting limits, or wants to check their API consumption. Also trigger when building workflows that need to throttle, pace, or gate requests based on remaining capacity. Works with any UW API endpoint response.
---

# Unusual Whales API Usage Monitor

Extract and interpret API usage metrics from Unusual Whales REST API response headers.

## When To Use

- User asks "how many API calls have I used today?" or "am I close to my limit?"
- Agent needs to check remaining capacity before making a batch of requests
- Building a pacing/throttling strategy for multi-endpoint workflows
- Diagnosing 429 rate limit errors or unexpected request failures
- Reporting usage statistics to the user

## How It Works

Every successful UW API response includes usage headers. No dedicated "usage" endpoint
exists — simply inspect the headers from any API call you've already made (or make a
lightweight call like `/api/news/headlines` to check).

## Response Headers Reference

| Header                          | Type | Description                                                                        |
| ------------------------------- | ---- | ---------------------------------------------------------------------------------- |
| `x-uw-token-req-limit`          | int  | Daily request limit for this API token                                             |
| `x-uw-daily-req-count`          | int  | Successful requests made today (resets daily at 8 PM Eastern / `America/New_York`) |
| `x-uw-req-per-minute-remaining` | int  | Requests still available in the current minute window                              |
| `x-uw-minute-req-counter`       | int  | Successful requests made in the current minute window                              |
| `x-uw-req-per-minute-reset`     | int  | Milliseconds until the per-minute counter resets                                   |

## Extracting Usage From a Response

Given any `requests.Response` object from a UW API call:

```python
import requests

def get_api_usage(response: requests.Response) -> dict:
    """Extract UW API usage metrics from response headers.

    Works with any successful UW API response. Returns a dict with
    raw values and computed fields for easy decision-making.
    """
    def safe_int(val):
        try:
            return int(val)
        except (TypeError, ValueError):
            return None

    daily_limit = safe_int(response.headers.get("x-uw-token-req-limit"))
    daily_used = safe_int(response.headers.get("x-uw-daily-req-count"))
    minute_remaining = safe_int(response.headers.get("x-uw-req-per-minute-remaining"))
    minute_used = safe_int(response.headers.get("x-uw-minute-req-counter"))
    minute_reset_ms = safe_int(response.headers.get("x-uw-req-per-minute-reset"))

    # Computed fields
    daily_remaining = (daily_limit - daily_used) if daily_limit is not None and daily_used is not None else None
    daily_pct_used = round((daily_used / daily_limit) * 100, 1) if daily_limit is not None and daily_used is not None else None
    minute_reset_sec = round(minute_reset_ms / 1000, 1) if minute_reset_ms else None

    return {
        "daily": {
            "limit": daily_limit,
            "used": daily_used,
            "remaining": daily_remaining,
            "percent_used": daily_pct_used,
        },
        "per_minute": {
            "used": minute_used,
            "remaining": minute_remaining,
            "resets_in_seconds": minute_reset_sec,
        },
    }
```

## Quick Check Pattern

When you just need a fast usage check and don't have an existing response:

```python
headers = {
    "Accept": "application/json, text/plain",
    "Authorization": "Bearer <TOKEN>"
}
resp = requests.get("https://api.unusualwhales.com/api/news/headlines", headers=headers)
```

`/api/news/headlines` is ideal for this because it's lightweight, always available,
and still counts as a normal request (so the returned headers are accurate).

After making the request, always follow the full error-handling sequence in the
**Error Handling** section below — never assume the request succeeded.

## Interpreting Results for Agents

Evaluate thresholds in the priority order below. **Stop at the first match** — higher
rows take precedence over lower rows.

### Per-Minute Thresholds (check first)

Per-minute limits can block you immediately, so evaluate these before daily thresholds.

| Priority | Condition                            | Meaning         | Recommended Action                            |
| -------- | ------------------------------------ | --------------- | --------------------------------------------- |
| 1        | `per_minute.remaining` == 0          | Minute cap hit  | Must wait `resets_in_seconds` before retrying |
| 2        | `per_minute.remaining` >= 1 and <= 4 | Near minute cap | Wait `resets_in_seconds` before next call     |

If `per_minute.remaining` >= 5, no per-minute action is needed.

### Daily Thresholds (check second)

| Priority | Condition                           | Meaning            | Recommended Action                         |
| -------- | ----------------------------------- | ------------------ | ------------------------------------------ |
| 1        | `daily.remaining` < 100             | Critical           | Stop non-essential requests, alert user    |
| 2        | `daily.percent_used` >= 80          | Approaching limit  | Throttle to essential requests only        |
| 3        | `daily.percent_used` >= 50 and < 80 | Moderate usage     | Consider batching or prioritizing requests |
| 4        | `daily.percent_used` < 50           | Plenty of headroom | Proceed normally                           |

The `daily.remaining < 100` check comes first because a low absolute count is critical
regardless of percentage — a 200-request plan at 40% usage has only 120 calls left.

## Example Output

```json
{
  "daily": {
    "limit": 15000,
    "used": 342,
    "remaining": 14658,
    "percent_used": 2.3
  },
  "per_minute": {
    "used": 1,
    "remaining": 119,
    "resets_in_seconds": 23.4
  }
}
```

## Human-Friendly Summary

When presenting usage to a human user, format it conversationally:

```
API Usage: 342 / 15,000 daily requests used (2.3%)
Per-minute: 1 used, 119 remaining (resets in 23s)
```

Avoid dumping raw header names — translate to plain language.

## Error Handling

Always check the response status before extracting usage headers. The API does not
return `x-uw-*` headers on authentication failures, so calling `get_api_usage()` on
a failed response will produce all `None` values. Follow this sequence:

```python
resp = requests.get(url, headers=headers)

if resp.ok:
    usage = get_api_usage(resp)
    # Present human-friendly summary (see above)

elif resp.status_code == 401:
    # Token is missing, invalid, or expired. UW headers will NOT be present.
    print("Unable to check API usage: authentication failed (HTTP 401).")
    print("Your API token is missing, invalid, or expired.")
    print()
    print("To fix this:")
    print("  1. Verify your token at https://unusualwhales.com/settings/developer-settings")
    print("  2. Set it in your environment: export UW_API_TOKEN=\"your-token-here\"")
    print("     Or add UW_API_TOKEN=your-token-here to your .env file")

elif resp.status_code == 429:
    # Rate limit exceeded. UW per-minute headers ARE still present.
    usage = get_api_usage(resp)
    m = usage["per_minute"]
    wait = m["resets_in_seconds"] or "unknown"
    print(f"Rate limit exceeded (HTTP 429). Per-minute request cap hit.")
    print(f"Wait {wait} seconds before retrying.")

elif resp.status_code == 403:
    # Token is valid but lacks permission for this endpoint.
    print("Access denied (HTTP 403).")
    print("Your API token does not have permission for this endpoint.")
    print("Check your subscription tier at https://unusualwhales.com/settings/account")

else:
    # Unexpected error — could be a server issue or network problem.
    print(f"API request failed (HTTP {resp.status_code}).")
    print("This may be a temporary server issue. Try again in a few moments.")
    print("If the problem persists, email support@unusualwhales.com")
```

### Error Output Templates

Use these exact formats when presenting errors to a human user:

**401 — Invalid Token:**

```
Unable to check API usage: authentication failed (HTTP 401).
Your API token is missing, invalid, or expired.

To fix this:
  1. Verify your token at https://unusualwhales.com/settings/developer-settings
  2. Set it in your environment: export UW_API_TOKEN="your-token-here"
     Or add UW_API_TOKEN=your-token-here to your .env file
```

**429 — Rate Limited:**

```
Rate limit exceeded (HTTP 429). Per-minute request cap hit.
Wait <resets_in_seconds> seconds before retrying.
```

**403 — Forbidden:**

```
Access denied (HTTP 403).
Your API token does not have permission for this endpoint.
Check your subscription tier at https://unusualwhales.com/settings/account
```

**Other Errors:**

```
API request failed (HTTP <status_code>).
This may be a temporary server issue. Try again in a few moments.
If the problem persists, email support@unusualwhales.com
```

### Edge Cases

- **Network error (no response at all):** If `requests.get()` raises a
  `requests.ConnectionError` or `requests.Timeout`, tell the user:
  "Could not reach the Unusual Whales API. Check your internet connection."
- **`daily.limit` is `None` on a successful response:** The token may not have a
  daily limit configured (uncommon but possible for some enterprise tiers).
  Report: "Daily limit: not configured for this token."
- **`daily.used` is 0:** This is valid — it means no requests have been made since
  the last daily reset (8 PM Eastern / America/New_York). Do not treat zero as an error.
