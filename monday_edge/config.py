"""Settings and .env loader for Monday Edge.

No extra dependencies: `.env` is parsed as KEY=VALUE lines and applied with
os.environ.setdefault, so an exported shell variable always wins.

Secrets reach code only through the environment and are referenced by variable
name (CLAUDE.md §6). Nothing here prints a key.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_env(paths=None) -> None:
    """Parse KEY=VALUE lines from .env files; existing env vars are not overridden."""
    paths = paths or [HERE / ".env", Path.cwd() / ".env"]
    for p in paths:
        p = Path(p)
        if not p.is_file():
            continue
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            if key:
                os.environ.setdefault(key, val)


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


@dataclass
class Settings:
    # credentials (by variable name only; never logged)
    fmp_api_key: str
    uw_api_key: str
    anthropic_api_key: str
    llm_model: str
    # universe and window
    tickers: tuple
    start_date: date
    end_date: date
    # paths
    cache_dir: Path
    out_dir: Path
    # data
    fmp_news_tz: str
    request_pause: float
    max_news_pages: int
    # buckets and tests
    gap_flat: float
    gap_large: float
    quiet_threshold: float
    holdout_frac: float
    min_n: int

    def ensure_dirs(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)


def settings(start: str | None = None, end: str | None = None) -> Settings:
    """Build Settings from the environment (after loading .env)."""
    load_env()
    tickers = tuple(t.strip().upper() for t in _env("TICKERS", "SPY,QQQ").split(",") if t.strip())
    start_s = start or _env("START_DATE", "2021-01-01")
    end_s = end or _env("END_DATE", "")
    cache_dir = Path(_env("CACHE_DIR", str(HERE / "cache")))
    out_dir = Path(_env("OUT_DIR", str(HERE / "output")))
    return Settings(
        fmp_api_key=_env("FMP_API_KEY"),
        uw_api_key=_env("UW_API_KEY") or _env("UNUSUAL_WHALES_API_KEY"),
        anthropic_api_key=_env("ANTHROPIC_API_KEY"),
        llm_model=_env("LLM_MODEL", "claude-sonnet-5"),
        tickers=tickers or ("SPY", "QQQ"),
        start_date=date.fromisoformat(start_s),
        end_date=date.fromisoformat(end_s) if end_s else date.today(),
        cache_dir=cache_dir,
        out_dir=out_dir,
        fmp_news_tz=_env("FMP_NEWS_TZ", "America/New_York"),
        request_pause=float(_env("REQUEST_PAUSE", "0.25")),
        max_news_pages=int(_env("MAX_NEWS_PAGES", "8")),
        gap_flat=float(_env("GAP_FLAT", "0.25")),
        gap_large=float(_env("GAP_LARGE", "0.75")),
        quiet_threshold=float(_env("QUIET_THRESHOLD", "3.0")),
        holdout_frac=float(_env("HOLDOUT_FRAC", "0.30")),
        min_n=int(_env("MIN_N", "15")),
    )
