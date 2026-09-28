"""Synthetic world with planted effects, same interface as the real clients.

Planted effects (spec §11):
  1. geopolitical weekends fill the same day ~80% of the time; all others ~50%.
  2. tariff weekends with a Trump ACTION fill ~15% (they continue with the gap).
     `action` only occurs on tariff weekends and is rare, so its discovery n
     stays under `min_n`: the sample-size guard must keep it out of "confirmed".

Everything else is noise: random-walk prices, QQQ at beta 1.3 to SPY, VIX
uniform 12-30, GEX a random walk, headlines from per-category templates.
"""
from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from sessions import news_window

ET = ZoneInfo("America/New_York")
UTC = timezone.utc

CATEGORY_P = {
    "geopolitical": 0.24, "tariffs_trade": 0.14, "fed_rates": 0.17, "fiscal_politics": 0.08,
    "energy": 0.08, "financial_stress": 0.05, "megacap_ai": 0.10, "quiet": 0.14,
}
GAP_VOL = {  # % std of the Monday gap by hidden category
    "geopolitical": 0.85, "tariffs_trade": 0.95, "fed_rates": 0.60, "fiscal_politics": 0.50,
    "energy": 0.50, "financial_stress": 1.00, "megacap_ai": 0.60, "quiet": 0.30,
}
P_TRUMP_ACTION_ON_TARIFF = 0.28
P_TRUMP_STATEMENT = 0.30  # on any non-quiet weekend without an action

TEMPLATES = {
    "geopolitical": [
        "Iran missile attack on Israel raises fears of wider war",
        "Houthi drone strike hits tanker near Hormuz",
        "Ukraine says Russia launched overnight missile barrage",
        "Taiwan reports military drills as tensions rise",
        "NATO ministers weigh response to attack",
        "Ceasefire talks stall after weekend strikes",
        "Israel warns of retaliation after rocket attack",
    ],
    "tariffs_trade": [
        "Tariff threat on EU imports rattles trade talks",
        "Trade war fears grow as reciprocal tariffs loom",
        "Export controls on chips widened, trade deal in doubt",
        "Customs officials brace for new import duties",
        "Trade talks with China end without a deal",
    ],
    "fed_rates": [
        "Fed officials signal patience on rate cuts",
        "Powell speech puts inflation back in focus",
        "Yields jump after hot CPI print revisions",
        "FOMC minutes show split on rate hike path",
        "Payrolls revision revives recession chatter",
        "PCE data due; Fed rate cut bets shift",
    ],
    "fiscal_politics": [
        "Shutdown deadline nears as Congress stalls on spending bill",
        "Debt ceiling talks resume at the White House",
        "Supreme Court to hear election case",
        "Continuing resolution passes Congress late Friday",
        "Stimulus proposal draws fire in Congress",
    ],
    "energy": [
        "OPEC+ surprises with output cut, crude jumps",
        "Brent tops $90 as oil supply worries grow",
        "WTI slides after inventory build",
        "Gasoline prices climb ahead of holiday",
        "Natural gas spikes on cold forecast",
    ],
    "financial_stress": [
        "Regional bank failure sparks contagion fears",
        "Bank run reported at mid-sized lender",
        "Sovereign default risk rises after downgrade",
        "Bailout talks for troubled insurer",
        "Bankruptcy filing shakes credit markets",
    ],
    "megacap_ai": [
        "Nvidia unveils new AI chips at weekend event",
        "Apple and Microsoft in AI partnership talks",
        "Google, Amazon race on AI spending",
        "Meta shares in focus after AI product leak",
        "Tesla, OpenAI headlines dominate weekend tech news",
    ],
    "quiet": [
        "Weekend reading: what to watch this week",
        "Retail earnings preview for the week ahead",
        "Housing market update: listings rise",
        "Sports team sells naming rights to stadium",
        "Local weather: mild week expected",
        "Travel demand steady into autumn",
    ],
}
TRUMP_ACTION = [
    "Trump signs executive order imposing 25% tariffs on imports",
    "White House: tariffs take effect Monday after Trump signed order",
    "Trump ordered new tariffs on Chinese goods, customs told to enforce",
]
TRUMP_STATEMENT = {
    "geopolitical": ["Trump says he may consider a response to the Iran attack",
                     "Trump warns Russia, says ceasefire deal could come soon"],
    "tariffs_trade": ["Trump says he will consider tariffs on EU cars",
                      "Trump threatens tariffs, says trade deal talks may resume"],
    "fed_rates": ["Trump says Fed should cut rates, expects Powell to act",
                  "Trump claims inflation is beaten, wants a rate cut"],
    "fiscal_politics": ["Trump says Congress will avoid a shutdown",
                        "Trump warns he could reject the spending bill"],
    "energy": ["Trump says OPEC should pump more oil", "Trump expects crude to fall soon"],
    "financial_stress": ["Trump says banks are sound, no bailout planned",
                         "Trump claims the default fears are overblown"],
    "megacap_ai": ["Trump says AI chips export rules may loosen",
                   "Trump wants Apple to build more in the US, he says"],
}
POST_ACTION = ["I have SIGNED the order. TARIFFS take effect Monday. Great for our economy!",
               "Tariffs imposed today. The stock market will love it!"]
POST_STATEMENT = ["We may have to do something big about this soon. Markets will be fine!",
                  "Considering all options. The economy is the strongest ever!"]


def _labor_day(year: int) -> date:
    d = date(year, 9, 1)
    while d.weekday() != 0:
        d += timedelta(days=1)
    return d


def _trading_days(start: date, end: date) -> list[date]:
    days = []
    d = start
    while d <= end:
        if d.weekday() < 5 and d != _labor_day(d.year):
            days.append(d)
        d += timedelta(days=1)
    return days


class MockWorld:
    def __init__(self, start: date = date(2020, 11, 2), end: date | None = None, seed: int = 42,
                 tickers=("SPY", "QQQ")):
        self.start = start
        self.end = end or date.today()
        self.seed = seed
        self.tickers = tuple(tickers)
        self.rng = np.random.default_rng(seed)
        self.days = _trading_days(self.start, self.end)
        self.truth: dict[date, dict] = {}
        self.prices: dict[str, pd.DataFrame] = {}
        self.intraday: dict[tuple[str, date], pd.DataFrame] = {}
        self.news: dict[date, list[dict]] = {}
        self.posts: list[dict] = []
        self.gex: dict[str, pd.DataFrame] = {}
        self.vix: pd.DataFrame
        self._build()

    # ----- generation -----
    def _build(self) -> None:
        rng = self.rng
        cats = list(CATEGORY_P)
        probs = np.array([CATEGORY_P[c] for c in cats])
        probs = probs / probs.sum()
        level = {"SPY": 350.0, "QQQ": 290.0}
        for t in self.tickers:
            level.setdefault(t, 100.0)
        beta = {t: (1.3 if t == "QQQ" else 1.0) for t in self.tickers}
        rows = {t: [] for t in self.tickers}
        prev_day = None
        vix_rows, gex_rows = [], {t: [] for t in self.tickers}
        gex_level = {t: 0.0 for t in self.tickers}
        for d in self.days:
            is_session = prev_day is not None and (d - prev_day).days >= 3
            vix_rows.append({"date": d, "close": float(rng.uniform(12, 30))})
            for t in self.tickers:
                gex_level[t] += rng.normal(0, 1.0)
                cg = abs(gex_level[t]) + rng.uniform(0.5, 2.0)
                gex_rows[t].append({"date": d, "call_gamma": cg, "put_gamma": gex_level[t] - cg})
            if is_session:
                cat = str(rng.choice(cats, p=probs))
                if cat == "tariffs_trade" and rng.random() < P_TRUMP_ACTION_ON_TARIFF:
                    mode = "action"
                elif cat != "quiet" and rng.random() < P_TRUMP_STATEMENT:
                    mode = "statement"
                else:
                    mode = "none"
                if cat == "geopolitical":
                    p_fill = 0.80
                elif cat == "tariffs_trade" and mode == "action":
                    p_fill = 0.15
                else:
                    p_fill = 0.50
                fill = bool(rng.random() < p_fill)
                gap_spy = float(rng.normal(0, GAP_VOL[cat]))
                if abs(gap_spy) < 0.02:
                    gap_spy = 0.02 * (1 if gap_spy >= 0 else -1)
                through = abs(rng.normal(0, 0.35)) + 0.05   # % beyond Friday close on fill days
                cont = abs(rng.normal(0, 0.45)) + 0.05      # % beyond the open on no-fill days
                self.truth[d] = {"category": cat, "trump_mode": mode, "fill": fill, "gap_spy": gap_spy}
                for t in self.tickers:
                    prev_close = level[t]
                    gap = beta[t] * gap_spy + rng.normal(0, 0.05)
                    sign = 1 if gap >= 0 else -1
                    o = prev_close * (1 + gap / 100.0)
                    if fill:
                        close = prev_close * (1 - sign * beta[t] * through / 100.0)
                    else:
                        close = o * (1 + sign * beta[t] * cont / 100.0)
                    bars = self._bridge(o, close, prev_close, sign, fill, d)
                    hi, lo = float(bars["high"].max()), float(bars["low"].min())
                    rows[t].append({"date": d, "open": o, "high": hi, "low": lo, "close": close,
                                    "volume": float(rng.integers(40e6, 90e6))})
                    self.intraday[(t, d)] = bars
                    level[t] = close
                self.news[d] = self._headlines(prev_day, d, cat, mode)
                self._posts(prev_day, d, mode)
            else:
                shock = rng.normal(0, 0.8)
                for t in self.tickers:
                    prev_close = level[t]
                    o = prev_close * (1 + rng.normal(0, 0.12) / 100.0)
                    close = o * (1 + beta[t] * shock / 100.0)
                    rng_hi = abs(rng.normal(0, 0.3)) / 100.0
                    rng_lo = abs(rng.normal(0, 0.3)) / 100.0
                    rows[t].append({"date": d, "open": o, "high": max(o, close) * (1 + rng_hi),
                                    "low": min(o, close) * (1 - rng_lo), "close": close,
                                    "volume": float(rng.integers(40e6, 90e6))})
                    level[t] = close
            prev_day = d
        for t in self.tickers:
            self.prices[t] = pd.DataFrame(rows[t])
            g = pd.DataFrame(gex_rows[t])
            g["net_gamma"] = g["call_gamma"] + g["put_gamma"]
            self.gex[t] = g
        self.vix = pd.DataFrame(vix_rows)
        self.vix["open"] = self.vix["high"] = self.vix["low"] = self.vix["close"]
        self.vix["volume"] = 0.0
        self.posts.sort(key=lambda p: p["ts_utc"])

    def _bridge(self, o: float, close: float, prev_close: float, sign: int, fill: bool, d: date) -> pd.DataFrame:
        """78 five-minute bars as a Brownian bridge from open to close."""
        rng = self.rng
        n = 78
        sigma = o * 0.0009
        steps = rng.normal(0, sigma, n)
        w = np.concatenate([[0.0], np.cumsum(steps)])
        tgrid = np.arange(n + 1) / n
        bridge = w - tgrid * w[-1]
        closes = o + (close - o) * tgrid + bridge
        closes[0], closes[-1] = o, close
        if not fill:  # never touch Friday's close
            pad = abs(o - prev_close) * 0.15 + o * 0.0002
            if sign > 0:
                closes = np.maximum(closes, prev_close + pad)
            else:
                closes = np.minimum(closes, prev_close - pad)
            closes[-1] = close
        bars = []
        t0 = datetime.combine(d, time(9, 30))
        for i in range(n):
            bo, bc = closes[i], closes[i + 1]
            wig_h = abs(rng.normal(0, o * 0.0004))
            wig_l = abs(rng.normal(0, o * 0.0004))
            hi, lo = max(bo, bc) + wig_h, min(bo, bc) - wig_l
            if not fill:
                pad = abs(o - prev_close) * 0.1 + o * 0.0001
                if sign > 0:
                    lo = max(lo, prev_close + pad)
                else:
                    hi = min(hi, prev_close - pad)
            bars.append({"ts": t0 + timedelta(minutes=5 * i), "open": bo, "high": hi, "low": lo, "close": bc,
                         "volume": float(rng.integers(2e5, 2e6))})
        return pd.DataFrame(bars)

    def _rand_ts(self, p: date, d: date) -> datetime:
        start, end = news_window(p, d)
        span = (end - start).total_seconds()
        return start + timedelta(seconds=float(self.rng.uniform(0, span - 1)))

    def _headlines(self, p: date, d: date, cat: str, mode: str) -> list[dict]:
        rng = self.rng
        out = []
        if cat == "quiet":
            n = int(rng.integers(3, 7))
            pool = TEMPLATES["quiet"]
            for _ in range(n):
                out.append(self._hl(str(rng.choice(pool)), p, d, False))
            return out
        n = int(rng.integers(6, 13))
        others = [c for c in TEMPLATES if c != cat]
        for _ in range(n):
            if rng.random() < 0.7:
                title = str(rng.choice(TEMPLATES[cat]))
            else:
                title = str(rng.choice(TEMPLATES[str(rng.choice(others))]))
            out.append(self._hl(title, p, d, rng.random() < 0.2))
        if mode == "action":
            out.append(self._hl(str(rng.choice(TRUMP_ACTION)), p, d, True))
        elif mode == "statement":
            out.append(self._hl(str(rng.choice(TRUMP_STATEMENT[cat])), p, d, rng.random() < 0.5))
        rng.shuffle(out)
        return out

    def _hl(self, title: str, p: date, d: date, major: bool) -> dict:
        return {"title": title, "text": "", "published_utc": self._rand_ts(p, d).isoformat(),
                "source": "mock", "url": "", "is_major": bool(major), "sentiment": None, "origin": "mock"}

    def _posts(self, p: date, d: date, mode: str) -> None:
        rng = self.rng
        if mode == "none":
            return
        pool = POST_ACTION if mode == "action" else POST_STATEMENT
        for _ in range(int(rng.integers(1, 3))):
            self.posts.append({"ts_utc": self._rand_ts(p, d).isoformat(), "text": str(rng.choice(pool)),
                               "market_relevant": True, "tickers": [], "origin": "mock"})

    def clients(self):
        return MockFMP(self), MockUW(self)


class MockFMP:
    def __init__(self, world: MockWorld):
        self.w = world
        self.notes: list[str] = []

    def eod(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        df = self.w.vix if symbol.upper() in ("^VIX", "VIX") else self.w.prices.get(symbol.upper())
        if df is None:
            return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        df = df[(df["date"] >= start) & (df["date"] <= end)]
        return df[["date", "open", "high", "low", "close", "volume"]].reset_index(drop=True)

    def intraday_5m(self, symbol: str, day: date) -> pd.DataFrame:
        bars = self.w.intraday.get((symbol.upper(), day))
        if bars is None:
            return pd.DataFrame(columns=["ts", "open", "high", "low", "close", "volume"])
        return bars.copy()

    def news(self, start_utc: datetime, end_utc: datetime, symbols=("SPY", "QQQ"), cache: bool = True) -> list[dict]:
        out = []
        for hs in self.w.news.values():
            for h in hs:
                ts = datetime.fromisoformat(h["published_utc"])
                if start_utc <= ts < end_utc:
                    out.append(h)
        out.sort(key=lambda h: h["published_utc"])
        return out

    def quote(self, symbol: str) -> dict:
        df = self.w.prices.get(symbol.upper())
        if df is None or df.empty:
            return {}
        today = date.today()
        row = df[df["date"] == today]
        if len(row):
            r = row.iloc[0]
            prev = df[df["date"] < today]
            return {"symbol": symbol, "price": float(r["open"]),
                    "previousClose": float(prev["close"].iloc[-1]) if len(prev) else float("nan"),
                    "timestamp": int(datetime.now(tz=UTC).timestamp())}
        last = df.iloc[-1]
        return {"symbol": symbol, "price": float(last["close"]), "previousClose": float(last["close"]),
                "timestamp": int(datetime.now(tz=UTC).timestamp())}


class MockUW:
    def __init__(self, world: MockWorld):
        self.w = world
        self.enabled = True
        self.notes: list[str] = ["mock UW: synthetic GEX, implied moves, posts and headlines"]

    def greek_exposure(self, ticker: str) -> pd.DataFrame:
        g = self.w.gex.get(ticker.upper())
        if g is None:
            return pd.DataFrame(columns=["date", "call_gamma", "put_gamma", "net_gamma"])
        return g[["date", "call_gamma", "put_gamma", "net_gamma"]].copy()

    def implied_moves(self, ticker: str, day: date) -> dict:
        v = self.w.vix[self.w.vix["date"] <= day]
        if v.empty:
            return {}
        vix = float(v["close"].iloc[-1])
        em1 = vix / math.sqrt(252)
        return {1: em1, 5: em1 * math.sqrt(5)}

    def potus_posts(self, since_utc: datetime, cache: bool = True) -> list[dict]:
        return [p for p in self.w.posts if datetime.fromisoformat(p["ts_utc"]) >= since_utc]

    def headlines(self, since_utc: datetime, cache: bool = False) -> list[dict]:
        out = []
        for hs in self.w.news.values():
            for h in hs:
                if datetime.fromisoformat(h["published_utc"]) >= since_utc:
                    out.append({**h, "origin": "uw_headlines"})
        return out
