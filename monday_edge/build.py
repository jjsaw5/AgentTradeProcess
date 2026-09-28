"""Assemble the dataset: one row per (session, ticker) -> output/weekends.csv.

Context columns use only Friday data and weekend news (no look-ahead).
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd

from sessions import (compute_outcomes, em_bucket, find_sessions, gap_bucket, gap_size, gex_regime,
                      lookup_on_or_before, news_window, vix_regime)
from tagger import tag_weekend, tone_vs_gap

UTC = timezone.utc

TAG_FIELDS = ("category", "category_2nd", "category_score", "risk_tone", "tone_score", "trump_mode",
              "trump_action_hits", "trump_statement_hits", "n_headlines", "trump_market_posts", "tagger",
              "summary", "surprise")


def _posts_in_window(posts: list[dict], start: datetime, end: datetime) -> list[dict]:
    out = []
    for p in posts:
        try:
            ts = datetime.fromisoformat(p["ts_utc"])
        except (KeyError, ValueError):
            continue
        if start <= ts < end:
            out.append(p)
    return out


def build_dataset(fmp, uw, cfg, use_llm: bool = False, log=print, today: date | None = None, workers: int = 3):
    """Return (DataFrame, notes dict). Also writes cfg.out_dir/weekends.csv."""
    today = today or date.today()
    tickers = list(cfg.tickers)
    start = cfg.start_date - timedelta(days=20)
    end = min(cfg.end_date, today)

    log(f"[build] daily bars {start} -> {end} for {', '.join(tickers)} and ^VIX")
    daily = {t: fmp.eod(t, start, end) for t in tickers}
    vix = fmp.eod("^VIX", start, end)
    gex = {t: uw.greek_exposure(t) for t in tickers}
    for t in tickers:
        if daily[t].empty:
            raise SystemExit(f"[build] no daily bars for {t}: check FMP_API_KEY and the date range")

    sessions = [s for s in find_sessions(daily[tickers[0]]["date"], today=today) if s[1] >= cfg.start_date]
    log(f"[build] {len(sessions)} weekend sessions found")
    if not sessions:
        raise SystemExit("[build] no sessions in range")

    first_start, _ = news_window(*sessions[0])
    posts = uw.potus_posts(first_start) if uw.enabled else []
    log(f"[build] {len(posts)} presidential posts since {first_start.date()}")

    def one_session(pd_: tuple):
        p, d = pd_
        w_start, w_end = news_window(p, d)
        headlines = fmp.news(w_start, w_end, symbols=tuple(tickers))
        truncated = bool(getattr(fmp, "last_news_truncated", False))
        w_posts = _posts_in_window(posts, w_start, w_end)
        tag = tag_weekend(headlines, w_posts, cfg, use_llm=use_llm)
        vix_p = lookup_on_or_before(vix, p, "close")
        out, missing = [], 0
        for t in tickers:
            intr = fmp.intraday_5m(t, d)
            oc = compute_outcomes(daily[t], p, d, intr)
            if not oc:
                continue
            if not oc["has_intraday"]:
                missing += 1
            em = uw.implied_moves(t, p) if uw.enabled else {}
            em1, em5 = em.get(1, np.nan), em.get(5, np.nan)
            regime, net_g, pctile = gex_regime(gex[t], p)
            gb = gap_bucket(oc["gap_pct"], cfg.gap_flat, cfg.gap_large)
            out.append({
                "session": d, "prev": p, "ticker": t,
                "window_start_utc": w_start.isoformat(), "window_end_utc": w_end.isoformat(),
                **{k: tag.get(k) for k in TAG_FIELDS},
                "top_headlines": " | ".join(tag.get("top_headlines") or []),
                "news_truncated": truncated,
                **oc,
                "em1_pct": em1, "em5_pct": em5, "em_bucket": em_bucket(oc["gap_pct"], em1),
                "vix": vix_p, "vix_regime": vix_regime(vix_p),
                "gex_net": net_g, "gex_regime": regime, "gex_pctile": pctile,
                "gap_bucket": gb, "gap_size": gap_size(oc["gap_pct"], cfg.gap_flat, cfg.gap_large),
                "tone_vs_gap": tone_vs_gap(tag["risk_tone"], gb),
            })
        return out, missing, len(headlines) == 0, truncated, tag

    rows = []
    missing_intraday = 0
    no_headlines = 0
    n_truncated = 0
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        for (p, d), (out, missing, empty, truncated, tag) in zip(sessions, ex.map(one_session, sessions)):
            rows.extend(out)
            missing_intraday += missing
            no_headlines += int(empty)
            n_truncated += int(truncated)
            done += 1
            if done % 10 == 0 or done == len(sessions):
                log(f"[build] {done}/{len(sessions)} sessions ({d}) — {tag['category']}/{tag['trump_mode']}, "
                    f"{tag['n_headlines']} headlines{' [news window truncated]' if truncated else ''}")

    df = pd.DataFrame(rows)
    df = df.sort_values(["session", "ticker"]).reset_index(drop=True)
    heads_by_year = (df.drop_duplicates("session").assign(year=lambda x: pd.to_datetime(x["session"]).dt.year)
                     .groupby("year")["n_headlines"].median().to_dict())
    oldest_post = min((p["ts_utc"] for p in posts), default=None)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = cfg.out_dir / "weekends.csv"
    df.to_csv(out_path, index=False)
    n_rows = len(df)
    notes = {
        "n_sessions": len(sessions),
        "n_rows": n_rows,
        "date_range": (sessions[0][1], sessions[-1][1]),
        "missing_intraday_pct": (100.0 * missing_intraday / n_rows) if n_rows else float("nan"),
        "no_headlines_pct": (100.0 * no_headlines / len(sessions)) if sessions else float("nan"),
        "news_truncated_pct": (100.0 * n_truncated / len(sessions)) if sessions else float("nan"),
        "uw_notes": list(uw.notes),
        "fmp_notes": list(getattr(fmp, "notes", [])),
        "headlines_median_by_year": {int(k): float(v) for k, v in heads_by_year.items()},
        "oldest_post_utc": oldest_post[:10] if oldest_post else None,
        "n_posts": len(posts),
        "tagger": "llm" if use_llm else "rules",
        "out_path": str(out_path),
    }
    log(f"[build] wrote {out_path} ({n_rows} rows)")
    return df, notes
