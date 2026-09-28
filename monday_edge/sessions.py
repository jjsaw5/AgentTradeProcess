"""Weekend sessions and their outcomes.

A session is a trading day `d` whose previous trading day `p` is 3+ calendar
days earlier (normal weekends, long weekends; a holiday Monday shifts the
session to Tuesday).

No look-ahead: context features use only `p` (Friday) data and weekend news.
Outcomes are measured from the session open `o`.

Sign convention: `d_sign` is +1 for an up gap, -1 for a down gap, so a positive
`h{k}_ret` means the move continued WITH the gap. Returns are underlying moves
in %, not option P&L.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ET = ZoneInfo("America/New_York")
UTC = timezone.utc
TRIVIAL_GAP = 1e-5  # 0.001% as a fraction


def find_sessions(dates, today: date | None = None) -> list[tuple[date, date]]:
    """(prev_trading_day, session_day) pairs where the calendar gap is >= 3 days."""
    ds = sorted(set(dates))
    out = []
    for p, d in zip(ds, ds[1:]):
        if (d - p).days >= 3:
            if today is not None and d >= today:
                continue
            out.append((p, d))
    return out


def news_window(p: date, d: date) -> tuple[datetime, datetime]:
    """`p 16:00 ET` -> `d 09:30 ET`, both as UTC datetimes."""
    start = datetime(p.year, p.month, p.day, 16, 0, tzinfo=ET).astimezone(UTC)
    end = datetime(d.year, d.month, d.day, 9, 30, tzinfo=ET).astimezone(UTC)
    return start, end


def _sign(x: float) -> int:
    return 1 if x >= 0 else -1


def compute_outcomes(daily: pd.DataFrame, p: date, d: date, intraday: pd.DataFrame | None) -> dict:
    """Context + daily + intraday outcomes for one session x ticker.

    `daily` has columns date, open, high, low, close (sorted ascending).
    `intraday` has ts (naive ET bar start), open, high, low, close, or None.
    """
    dl = daily.reset_index(drop=True)
    pos = {dt: i for i, dt in enumerate(dl["date"])}
    if p not in pos or d not in pos:
        return {}
    ip, i0 = pos[p], pos[d]
    closes = dl["close"].to_numpy(dtype=float)
    highs = dl["high"].to_numpy(dtype=float)
    lows = dl["low"].to_numpy(dtype=float)
    opens = dl["open"].to_numpy(dtype=float)

    prev_close = closes[ip]
    o = opens[i0]
    if not (np.isfinite(prev_close) and np.isfinite(o)) or prev_close <= 0:
        return {}
    gap = o / prev_close - 1.0
    d_sign = _sign(gap)
    trivial = abs(gap) < TRIVIAL_GAP

    out: dict = {
        "prev_close": prev_close,
        "open": o,
        "gap_pct": gap * 100.0,
        "gap_dir": "up" if gap >= 0 else "down",
        "d_sign": d_sign,
    }
    # ----- context (known before the open) -----
    out["friday_ret_pct"] = (closes[ip] / closes[ip - 1] - 1.0) * 100.0 if ip >= 1 else np.nan
    out["prior_week_ret_pct"] = (closes[ip] / closes[ip - 5] - 1.0) * 100.0 if ip >= 5 else np.nan
    if np.isfinite(out["prior_week_ret_pct"]):
        out["prior_week_dir_vs_gap"] = "same" if _sign(out["prior_week_ret_pct"]) == d_sign else "opposite"
    else:
        out["prior_week_dir_vs_gap"] = "n/a"

    # ----- daily outcomes, k = 0..4 -----
    for k in range(5):
        ik = i0 + k
        if ik >= len(dl):
            for f in ("ret", "abs", "fill", "mfe", "mae"):
                out[f"h{k}_{f}"] = np.nan
            continue
        c = closes[ik]
        out[f"h{k}_ret"] = d_sign * (c / o - 1.0) * 100.0
        out[f"h{k}_abs"] = abs(c / o - 1.0) * 100.0
        lo = np.nanmin(lows[i0:ik + 1])
        hi = np.nanmax(highs[i0:ik + 1])
        if trivial:
            filled = True
        elif d_sign > 0:
            filled = bool(lo <= prev_close)
        else:
            filled = bool(hi >= prev_close)
        out[f"h{k}_fill"] = filled
        if d_sign > 0:
            out[f"h{k}_mfe"] = (hi / o - 1.0) * 100.0
            out[f"h{k}_mae"] = (1.0 - lo / o) * 100.0
        else:
            out[f"h{k}_mfe"] = (1.0 - lo / o) * 100.0
            out[f"h{k}_mae"] = (hi / o - 1.0) * 100.0
    out["continuation"] = bool(out["h0_ret"] > 0) if np.isfinite(out["h0_ret"]) else np.nan
    out["fill_same_day"] = out["h0_fill"]
    out["close_0"] = closes[i0]

    # ----- intraday outcomes -----
    intr_fields = ("min_to_fill", "fill_1h", "or_high", "or_low", "c30", "first30_ret",
                   "first30_holds", "orb_break", "orb_follow")
    for f in intr_fields:
        out[f] = np.nan
    out["has_intraday"] = False
    if intraday is None or len(intraday) < 20:
        return out

    bars = intraday.sort_values("ts").reset_index(drop=True)
    ts = pd.to_datetime(bars["ts"])
    mins = ((ts.dt.hour * 60 + ts.dt.minute) - (9 * 60 + 30) + 5).to_numpy()
    bh = bars["high"].to_numpy(dtype=float)
    bl = bars["low"].to_numpy(dtype=float)
    bc = bars["close"].to_numpy(dtype=float)
    out["has_intraday"] = True

    if trivial:
        mtf = 0.0
    else:
        hit = (bl <= prev_close) if d_sign > 0 else (bh >= prev_close)
        idx = np.flatnonzero(hit)
        mtf = float(mins[idx[0]]) if len(idx) else np.nan
    out["min_to_fill"] = mtf
    out["fill_1h"] = bool(mtf <= 60) if np.isfinite(mtf) else False

    orm = mins <= 30
    if orm.any():
        or_high = float(np.nanmax(bh[orm]))
        or_low = float(np.nanmin(bl[orm]))
        c30 = float(bc[orm][-1])
        close = float(closes[i0])
        out["or_high"], out["or_low"], out["c30"] = or_high, or_low, c30
        out["first30_ret"] = d_sign * (c30 / o - 1.0) * 100.0
        out["first30_holds"] = bool(_sign(c30 / o - 1.0) == _sign(close / c30 - 1.0))
        after = np.flatnonzero(mins > 30)
        brk, follow = "none", np.nan
        for j in after:
            if bc[j] > or_high:
                brk, follow = "up", bool(close > or_high)
                break
            if bc[j] < or_low:
                brk, follow = "down", bool(close < or_low)
                break
        out["orb_break"], out["orb_follow"] = brk, follow
    return out


# ----- buckets -----

def gap_size(gap_pct: float, flat: float, large: float) -> str:
    a = abs(gap_pct)
    if not np.isfinite(a):
        return "n/a"
    if a < flat:
        return "flat"
    if a < large:
        return "small"
    return "large"


def gap_bucket(gap_pct: float, flat: float, large: float) -> str:
    s = gap_size(gap_pct, flat, large)
    if s in ("flat", "n/a"):
        return s
    return f"{s}_{'up' if gap_pct >= 0 else 'down'}"


def em_bucket(gap_pct: float, em1_pct: float | None) -> str:
    if em1_pct is None or not np.isfinite(em1_pct) or em1_pct <= 0 or not np.isfinite(gap_pct):
        return "n/a"
    r = abs(gap_pct) / em1_pct
    if r < 0.5:
        return "<0.5 EM"
    if r < 1.0:
        return "0.5-1 EM"
    return ">1 EM"


def vix_regime(vix: float | None) -> str:
    if vix is None or not np.isfinite(vix):
        return "n/a"
    if vix < 15:
        return "<15"
    if vix < 20:
        return "15-20"
    if vix < 30:
        return "20-30"
    return ">30"


def gex_regime(gex: pd.DataFrame | None, p: date) -> tuple[str, float, float]:
    """(regime, net_gamma, percentile vs trailing 252) using the latest row on or before `p`."""
    if gex is None or gex.empty:
        return "n/a", np.nan, np.nan
    sub = gex[gex["date"] <= p]
    if sub.empty:
        return "n/a", np.nan, np.nan
    vals = sub["net_gamma"].to_numpy(dtype=float)
    latest = vals[-1]
    if not np.isfinite(latest):
        return "n/a", np.nan, np.nan
    trail = vals[-252:]
    trail = trail[np.isfinite(trail)]
    pct = float((trail <= latest).mean() * 100.0) if len(trail) else np.nan
    return ("positive" if latest >= 0 else "negative"), float(latest), pct


def lookup_on_or_before(df: pd.DataFrame, p: date, col: str):
    if df is None or df.empty:
        return np.nan
    sub = df[df["date"] <= p]
    if sub.empty:
        return np.nan
    return float(sub[col].iloc[-1])
