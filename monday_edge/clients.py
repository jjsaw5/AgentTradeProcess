"""FMP and Unusual Whales clients with an on-disk JSON cache.

Rules that come from this repo's data layer (CLAUDE.md §3):

* A ``200`` is not a success. UW answers a bad parameter with ``200`` and
  ``{"data": []}``; an empty result is returned as empty and the caller decides
  whether that is a fact about the world or a pipeline failure.
* A default page size is a silent filter. News and posts are paginated until a
  short page or the page cap.
* Read the timestamp. Every row keeps its own timestamp; nothing assumes
  freshness.

The API key is never part of a cache key, a log line or an exception message.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

UTC = timezone.utc
ET = ZoneInfo("America/New_York")

SECRET_PARAMS = ("apikey", "api_key", "token", "key")


class CachedHTTP:
    """GET with disk cache. Only HTTP 200 is cached. 429 retried with backoff."""

    def __init__(self, cache_dir: Path, pause: float = 0.25, max_attempts: int = 4, timeout: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pause = pause
        self.max_attempts = max_attempts
        self.timeout = timeout
        self.session = requests.Session()
        self.calls = 0
        self.cache_hits = 0

    @staticmethod
    def cache_key(url: str, params: dict | None) -> str:
        clean = {k: v for k, v in (params or {}).items() if k.lower() not in SECRET_PARAMS}
        blob = url + "?" + json.dumps(sorted(clean.items()), default=str)
        return hashlib.sha1(blob.encode("utf-8")).hexdigest()

    def get(self, url: str, params: dict | None = None, headers: dict | None = None, cache: bool = True):
        """Return (status_code, parsed_json_or_None)."""
        key = self.cache_key(url, params)
        path = self.cache_dir / f"{key}.json"
        if cache and path.is_file():
            try:
                self.cache_hits += 1
                return 200, json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                pass
        status, body = None, None
        for attempt in range(self.max_attempts):
            try:
                resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
                self.calls += 1
            except requests.RequestException:
                if attempt == self.max_attempts - 1:
                    return 0, None
                time.sleep(2 ** attempt)
                continue
            status = resp.status_code
            if status == 429 or status >= 500:
                if attempt == self.max_attempts - 1:
                    break
                time.sleep(2 ** attempt)
                continue
            break
        if self.pause:
            time.sleep(self.pause)
        if status is None:
            return 0, None
        try:
            body = resp.json()
        except ValueError:
            body = None
        if status == 200 and cache and body is not None:
            try:
                path.write_text(json.dumps(body), encoding="utf-8")
            except OSError:
                pass
        return status, body


def _rows(body):
    """FMP/UW payloads may be a list or a dict with historical/data."""
    if body is None:
        return []
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for k in ("historical", "data", "results"):
            if isinstance(body.get(k), list):
                return body[k]
        return [body] if body else []
    return []


def _to_utc(ts, tz):
    """Localize a naive timestamp in `tz` (or parse an aware one) and return UTC datetime."""
    if ts is None or ts == "":
        return None
    if isinstance(ts, (int, float)):
        val = float(ts)
        if val > 1e11:  # epoch ms
            val /= 1000.0
        return datetime.fromtimestamp(val, tz=UTC)
    t = pd.Timestamp(ts)
    if pd.isna(t):
        return None
    if t.tzinfo is None:
        t = t.tz_localize(tz)
    return t.tz_convert("UTC").to_pydatetime()


class FMP:
    """Financial Modeling Prep, `stable` base, `apikey=` query param."""

    BASE = "https://financialmodelingprep.com/stable"

    def __init__(self, http: CachedHTTP, api_key: str, news_tz: str = "America/New_York", max_news_pages: int = 8):
        self.http = http
        self.api_key = api_key
        self.news_tz = ZoneInfo(news_tz)
        self.max_news_pages = max_news_pages
        self.notes: list[str] = []
        self.last_news_truncated = False

    def _get(self, path: str, params: dict, cache: bool = True):
        p = dict(params)
        p["apikey"] = self.api_key
        status, body = self.http.get(f"{self.BASE}/{path}", p, cache=cache)
        if status != 200:
            self.notes.append(f"FMP {path}: HTTP {status}")
            return []
        return _rows(body)

    def eod(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        rows = self._get("historical-price-eod/full", {"symbol": symbol, "from": str(start), "to": str(end)})
        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        df["date"] = pd.to_datetime(df["date"]).dt.date
        for c in ("open", "high", "low", "close", "volume"):
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            else:
                df[c] = float("nan")
        df = df[["date", "open", "high", "low", "close", "volume"]].dropna(subset=["close"])
        return df.sort_values("date").drop_duplicates("date").reset_index(drop=True)

    def intraday_5m(self, symbol: str, day: date) -> pd.DataFrame:
        """5-minute bars for one day. Timestamps are naive US/Eastern bar starts; keeps 09:30 <= ts < 16:00."""
        rows = self._get("historical-chart/5min", {"symbol": symbol, "from": str(day), "to": str(day)})
        df = pd.DataFrame(rows)
        cols = ["ts", "open", "high", "low", "close", "volume"]
        if df.empty or "date" not in df.columns:
            return pd.DataFrame(columns=cols)
        df["ts"] = pd.to_datetime(df["date"])
        for c in ("open", "high", "low", "close", "volume"):
            df[c] = pd.to_numeric(df.get(c), errors="coerce")
        df = df[df["ts"].dt.date == day]
        t = df["ts"].dt.hour * 60 + df["ts"].dt.minute
        df = df[(t >= 9 * 60 + 30) & (t < 16 * 60)]
        return df[cols].sort_values("ts").reset_index(drop=True)

    def _news_day(self, path: str, day: date, extra: dict, start_utc: datetime, cache: bool) -> tuple[list, bool]:
        """Page one endpoint for one calendar day, newest first, until a page reaches back past
        `start_utc`, a short page arrives, or the page cap. Returns (rows, truncated)."""
        out = []
        for page in range(self.max_news_pages):
            rows = self._get(path, {**extra, "from": str(day), "to": str(day), "page": page, "limit": 250}, cache=cache)
            out.extend(rows)
            if len(rows) < 250:
                return out, False
            oldest = None
            for r in rows:
                ts = _to_utc(r.get("publishedDate") or r.get("published_date") or r.get("date"), self.news_tz)
                if ts is not None and (oldest is None or ts < oldest):
                    oldest = ts
            if oldest is not None and oldest < start_utc:
                return out, False
        return out, True  # cap hit before the page reached the window start: coverage is not proven

    def news(self, start_utc: datetime, end_utc: datetime, symbols=("SPY", "QQQ"), cache: bool = True) -> list[dict]:
        """General + stock news inside [start_utc, end_utc), deduped by title.

        Verified 2026-09-28: `general-latest` honors from/to but pages newest-first at ~1000 rows
        per day, so a single Fri->Mon query spends the page cap on Monday afternoon and never
        reaches the weekend. Each day is therefore queried on its own. `self.last_news_truncated`
        is True when the cap cut a day short of the window start (a fact about coverage, not
        about the weekend)."""
        start_local = start_utc.astimezone(self.news_tz).date()
        end_local = end_utc.astimezone(self.news_tz).date()
        raw, truncated = [], False
        day = start_local
        while day <= end_local:
            for path, extra in (("news/general-latest", {}), ("news/stock", {"symbols": ",".join(symbols)})):
                rows, trunc = self._news_day(path, day, extra, start_utc, cache)
                raw.extend(rows)
                truncated = truncated or trunc
            day += timedelta(days=1)
        self.last_news_truncated = truncated
        seen, out = set(), []
        for r in raw:
            title = (r.get("title") or "").strip()
            if not title:
                continue
            ts = _to_utc(r.get("publishedDate") or r.get("published_date") or r.get("date"), self.news_tz)
            if ts is None or not (start_utc <= ts < end_utc):
                continue
            key = title.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "title": title,
                "text": (r.get("text") or "")[:500],
                "published_utc": ts.isoformat(),
                "source": r.get("site") or r.get("publisher") or "",
                "url": r.get("url") or "",
                "is_major": False,
                "sentiment": None,
                "origin": "fmp",
            })
        out.sort(key=lambda x: x["published_utc"])
        return out

    def quote(self, symbol: str) -> dict:
        rows = self._get("quote", {"symbol": symbol}, cache=False)
        return rows[0] if rows else {}

    def premarket(self, symbol: str) -> dict:
        """Pre-market bid/ask mid from `aftermarket-quote` (verified live 2026-09-28 08:40 ET;
        `quote` itself stays stamped at Friday's close until the open). {} if unavailable."""
        rows = self._get("aftermarket-quote", {"symbol": symbol}, cache=False)
        if not rows:
            return {}
        r = rows[0]
        bid, ask = pd.to_numeric(r.get("bidPrice"), errors="coerce"), pd.to_numeric(r.get("askPrice"), errors="coerce")
        if not (pd.notna(bid) and pd.notna(ask)) or bid <= 0 or ask <= 0:
            return {}
        return {"price": float((bid + ask) / 2), "bid": float(bid), "ask": float(ask), "timestamp": r.get("timestamp")}


class UW:
    """Unusual Whales. Bearer auth. Degrades to empty + a note on plan limits; never crashes."""

    BASE = "https://api.unusualwhales.com/api"
    MAX_PAGES = 60

    def __init__(self, http: CachedHTTP, api_key: str):
        self.http = http
        self.api_key = api_key
        self.enabled = bool(api_key)
        self.notes: list[str] = []
        if not self.enabled:
            self.notes.append("UW_API_KEY not set: GEX regime, implied move, presidential posts and live headlines skipped.")

    def _get(self, path: str, params: dict | None = None, cache: bool = True):
        if not self.enabled:
            return []
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        status, body = self.http.get(f"{self.BASE}/{path}", params or {}, headers=headers, cache=cache)
        if status == 403:
            code = ""
            if isinstance(body, dict):
                code = str(body.get("code") or body.get("error") or body.get("message") or "")[:80]
            self._note(f"UW {path}: 403 {code or 'forbidden'} (plan lacks this data) — left empty")
            return []
        if status != 200:
            self._note(f"UW {path}: HTTP {status} — left empty")
            return []
        rows = _rows(body)
        return rows

    def _note(self, msg: str) -> None:
        if msg not in self.notes:
            self.notes.append(msg)

    def greek_exposure(self, ticker: str) -> pd.DataFrame:
        rows = self._get(f"stock/{ticker}/greek-exposure", {"timeframe": "6Y"})
        df = pd.DataFrame(rows)
        cols = ["date", "call_gamma", "put_gamma", "net_gamma"]
        if df.empty or "date" not in df.columns:
            if self.enabled:
                self._note(f"UW greek-exposure {ticker}: empty response — GEX regime n/a")
            return pd.DataFrame(columns=cols)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        for c in ("call_gamma", "put_gamma"):
            df[c] = pd.to_numeric(df.get(c), errors="coerce")
        df["net_gamma"] = df["call_gamma"] + df["put_gamma"]
        return df[cols].dropna(subset=["net_gamma"]).sort_values("date").drop_duplicates("date").reset_index(drop=True)

    def implied_moves(self, ticker: str, day: date) -> dict:
        """{days: implied move in %} from interpolated-iv for `day` (fraction → %)."""
        rows = self._get(f"stock/{ticker}/interpolated-iv", {"date": str(day)})
        out = {}
        for r in rows:
            d = pd.to_numeric(r.get("days"), errors="coerce")
            m = pd.to_numeric(r.get("implied_move_perc"), errors="coerce")
            if pd.notna(d) and pd.notna(m):
                out[int(d)] = float(m) * 100.0
        return out

    def _paged(self, path: str, params: dict, since_utc: datetime, ts_key_candidates, cache: bool):
        out = []
        for page in range(self.MAX_PAGES):
            rows = self._get(path, {**params, "page": page}, cache=cache)
            if not rows:
                break
            oldest = None
            for r in rows:
                ts = None
                for k in ts_key_candidates:
                    if r.get(k) not in (None, ""):
                        ts = _to_utc(r[k], UTC)
                        break
                r["_ts_utc"] = ts
                if ts is not None and (oldest is None or ts < oldest):
                    oldest = ts
            out.extend(rows)
            if oldest is not None and oldest < since_utc:
                break
            if len(rows) < int(params.get("limit", 100)):
                break
        return out

    def potus_posts(self, since_utc: datetime, cache: bool = True) -> list[dict]:
        """Truth Social posts newer than since_utc. `timestamp` is epoch ms UTC."""
        rows = self._paged("potus/posts", {"limit": 200}, since_utc, ("timestamp", "created_at", "date"), cache)
        out = []
        for r in rows:
            ts = r.get("_ts_utc")
            if ts is None or ts < since_utc:
                continue
            text = r.get("text") or r.get("content") or r.get("post") or r.get("body") or ""
            rel = None
            for k in ("is_market_relevant", "market_relevant", "relevant", "is_relevant"):
                if k in r:
                    rel = bool(r[k])
                    break
            out.append({"ts_utc": ts.isoformat(), "text": str(text), "market_relevant": rel,
                        "tickers": r.get("tickers") or [], "origin": "uw_potus"})
        out.sort(key=lambda x: x["ts_utc"])
        return out

    def headlines(self, since_utc: datetime, cache: bool = False) -> list[dict]:
        """Live headlines with is_major / sentiment (used in `today`)."""
        rows = self._paged("news/headlines", {"limit": 100}, since_utc, ("created_at", "timestamp", "date"), cache)
        out = []
        for r in rows:
            ts = r.get("_ts_utc")
            title = (r.get("headline") or r.get("title") or "").strip()
            if ts is None or ts < since_utc or not title:
                continue
            out.append({"title": title, "text": "", "published_utc": ts.isoformat(),
                        "source": r.get("source") or "uw", "url": "",
                        "is_major": bool(r.get("is_major")), "sentiment": r.get("sentiment"),
                        "tickers": r.get("tickers") or [], "origin": "uw_headlines"})
        out.sort(key=lambda x: x["published_utc"])
        return out


def make_clients(cfg):
    http = CachedHTTP(cfg.cache_dir, pause=cfg.request_pause)
    fmp = FMP(http, cfg.fmp_api_key, news_tz=cfg.fmp_news_tz, max_news_pages=cfg.max_news_pages)
    uw = UW(http, cfg.uw_api_key)
    return fmp, uw
