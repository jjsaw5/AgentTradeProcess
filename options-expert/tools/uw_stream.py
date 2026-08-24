#!/usr/bin/env python3
"""
Live Unusual Whales websocket monitor for intraday sessions.

Replaces the playbook's 5-minute REST polling (PLAYBOOK.md §4) with a push
feed. The tripwires are the same ones, evaluated on live data instead of
completed-bar polls.

    python uw_stream.py --tickers SPY,QQQ
    python uw_stream.py --tickers SPY --channels market_tide,news,trading_halts
    python uw_stream.py --tickers SPY,NVDA --dark      # + off-exchange prints

Requires:  pip install websockets
Auth:      UNUSUAL_WHALES_API_KEY in the environment. Never passed on argv,
           never logged — the token rides in the URL, so the URL is never
           printed either.

Verified against wss://api.unusualwhales.com/socket on 2026-08-18: all of
market_tide, gex:TICKER, news and trading_halts joined with status ok.

off_lit_trades was NOT part of that verification. It is opt-in behind --dark,
its payload schema is unconfirmed, and the first payload received is dumped to
the console so the real field names can be recorded in DATA_LAYER.md §3a
instead of guessed. See the DARK POOL section below before relying on it.

Windows note (learned the hard way, PLAYBOOK.md §4): the console defaults to
cp1252 and will raise UnicodeEncodeError on the alert glyphs at exactly the
moment an alert fires. stdout is forced to UTF-8 below. Do not remove that.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from collections import defaultdict, deque

# --- Windows cp1252 guard: must run before any alert can print -------------
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import websockets
except ImportError:
    sys.exit("websockets not installed — run: pip install websockets")

WS_BASE = "wss://api.unusualwhales.com/socket"

# Tripwire thresholds. Calibrated at VIX ~14 (PLAYBOOK.md §4); recalibrate on
# a regime change rather than trusting them across volatility regimes.
PUT_PREMIUM_ALERT = 40_000_000      # tripwire B: net put premium above this
CALL_DRAWDOWN_ALERT = 40_000_000    # tripwire C: calls this far off high-water


def ts() -> str:
    return time.strftime("%H:%M:%S")


def money(v) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "NA"
    for unit, div in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(v) >= div:
            return f"{v/div:+.2f}{unit}"
    return f"{v:+.0f}"


# --- DARK POOL (off_lit_trades) --------------------------------------------
# WHY THIS IS OPT-IN. off_lit_trades is the whole off-exchange print tape, not a
# per-ticker feed, and off-exchange is a large fraction of US consolidated share
# volume. Joining it market-wide pushes every one of those prints through
# json.loads in the processor, which is precisely how a client falls behind and
# starts taking SERVER-SIDE drops on market_tide and gex -- the channels that
# actually drive decisions (DATA_LAYER.md §3f). So: never in the default channel
# list, requires a non-empty watch list, and everything under the floors is
# counted rather than printed.
#
# UNVERIFIED, and deliberately not papered over:
#   - whether the channel accepts a per-ticker suffix (off_lit_trades:TICKER).
#     gex and net_flow do; option_trades is documented as option_trades[:TICKER];
#     this one is written bare in DATA_LAYER §3f. --dark-ticker-channels tries
#     the suffixed form for anyone who wants to find out.
#   - the payload field names. The REST route's schema was confirmed live on
#     2026-08-24 and every candidate key below hit on its first choice, which is
#     evidence but NOT proof: that is the REST route, and this socket payload has
#     still never been observed. _dp_fields tries a short list of candidate keys
#     and gives up honestly rather than inventing a number.
#
# Thresholds are operator ergonomics, not calibrated edge. They exist to keep the
# console readable, and nothing downstream should treat them as meaningful.
DARK_WINDOW_SEC = 900                      # cluster lookback (15 minutes)
DARK_CLUSTER_MIN_PRINTS = 4                # E2b reads repetition, not one print
DARK_CLUSTER_MIN_NOTIONAL = 5_000_000
DARK_SINGLE_PRINT_NOTIONAL = 25_000_000    # one print worth seeing on its own

_DP_PRICE_KEYS = ("price", "trade_price", "px")
_DP_SIZE_KEYS = ("size", "quantity", "volume")
_DP_PREM_KEYS = ("premium", "notional", "value")
_DP_BID_KEYS = ("nbbo_bid", "nbbo_bid_price", "bid")
_DP_ASK_KEYS = ("nbbo_ask", "nbbo_ask_price", "ask")


def _first_float(payload, keys):
    """First key present with a numeric value, else None. None means unknown."""
    for k in keys:
        v = payload.get(k)
        if v is None:
            continue
        try:
            return float(v)
        except (TypeError, ValueError):
            continue
    return None


def _dp_fields(payload):
    """(ticker, notional, side) from an off_lit_trades payload.

    `side` is "above" / "at" / "below" the NBBO midpoint at execution, or None
    when the NBBO is absent. None stays None: an unclassifiable print is
    NA_unresolved and is NEVER bucketed into "at" to keep the arithmetic tidy
    (CLAUDE.md §4 -- the two kinds of missing do not collapse).

    Returns None when the print cannot be measured at all, which the caller
    counts rather than discards silently.
    """
    t = payload.get("ticker") or payload.get("symbol")
    if not t:
        return None
    price = _first_float(payload, _DP_PRICE_KEYS)
    size = _first_float(payload, _DP_SIZE_KEYS)
    notional = _first_float(payload, _DP_PREM_KEYS)
    if notional is None and price is not None and size is not None:
        notional = price * size
    if notional is None:
        return None

    side = None
    bid = _first_float(payload, _DP_BID_KEYS)
    ask = _first_float(payload, _DP_ASK_KEYS)
    if price is not None and bid is not None and ask is not None and ask >= bid:
        mid = (bid + ask) / 2.0
        # Mid-crossed prints are common and land exactly on the midpoint, so
        # compare with a tolerance scaled to the spread rather than with ==.
        tol = max((ask - bid) * 0.01, 1e-6)
        side = "above" if price > mid + tol else "below" if price < mid - tol else "at"
    return str(t).upper(), notional, side


def _dp_money(v):
    """Unsigned money. money() prints a leading + which reads oddly on size."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "NA"
    for unit, div in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(v) >= div:
            return f"${v/div:.1f}{unit}"
    return f"${v:.0f}"


class DarkPool:
    """Per-ticker off-exchange print accumulator, mirroring SKILL.md E2b.

    E2b's reading rule is that a lone block means nothing and REPETITION is the
    pattern worth naming, so this emits on clusters, not on prints. A single
    print surfaces only when it is large enough that an operator holding the
    name would want to see it, and that line is marked `not citable` so it
    cannot be mistaken for the cluster signal.

    The above/below-mid split is INFERRED. The tape does not mark which side
    initiated an off-exchange print; placing it against the NBBO midpoint is a
    heuristic, and it is weaker than UW's options aggressor-side fields. Every
    line this class emits carries that caveat, because a console line gets
    pasted into a log entry with none of its context.
    """

    def __init__(self):
        self.prints = defaultdict(deque)   # ticker -> deque[(t, notional, side)]
        self.fired = defaultdict(float)
        self.unparsed = 0
        self.schema_dumped = False

    def _once(self, key, cooldown=DARK_WINDOW_SEC):
        now = time.time()
        if now - self.fired[key] < cooldown:
            return False
        self.fired[key] = now
        return True

    def add(self, payload, watch):
        """Return lines to print. Cheap by design -- this runs per message."""
        out = []

        if not self.schema_dumped and isinstance(payload, dict):
            self.schema_dumped = True
            # One-shot. The point is to END the guessing in _dp_fields: record
            # these keys in DATA_LAYER.md §3a and pin the parser to them.
            out.append(
                f"[{ts()}] DARK  schema (first payload, record in DATA_LAYER §3a): "
                f"{sorted(payload.keys())}"
            )

        parsed = _dp_fields(payload) if isinstance(payload, dict) else None
        if parsed is None:
            self.unparsed += 1
            return out
        t, notional, side = parsed
        if t not in watch:
            return out

        now = time.time()
        q = self.prints[t]
        q.append((now, notional, side))
        cutoff = now - DARK_WINDOW_SEC
        while q and q[0][0] < cutoff:
            q.popleft()

        if notional >= DARK_SINGLE_PRINT_NOTIONAL and self._once(f"single:{t}", 60):
            out.append(
                f"[{ts()}] dark  {t}  single print {_dp_money(notional)} "
                f"{side or 'side NA_unresolved'} — not citable on its own (E2b)"
            )

        total = sum(n for _, n, _ in q)
        if len(q) >= DARK_CLUSTER_MIN_PRINTS and total >= DARK_CLUSTER_MIN_NOTIONAL \
                and self._once(f"cluster:{t}"):
            above = sum(1 for _, _, sd in q if sd == "above")
            at = sum(1 for _, _, sd in q if sd == "at")
            below = sum(1 for _, _, sd in q if sd == "below")
            unres = sum(1 for _, _, sd in q if sd is None)
            split = f"{above} above / {at} at / {below} below mid"
            if unres:
                split += f" / {unres} NA_unresolved"
            out.append(
                f"[{ts()}] DARK  {t}  {len(q)} prints in "
                f"{DARK_WINDOW_SEC // 60}m, {_dp_money(total)} — {split} "
                f"[inferred from NBBO, not a signed side; no ADV denominator here]"
            )
        return out


class Tripwires:
    """Playbook §4 tide tripwires, evaluated on live tide updates.

    A = net call premium falls on two consecutive updates while net put
        premium rises. The reversal signature: buyers stepping back AND
        sellers arriving, which is different from either alone.
    B = net put premium above PUT_PREMIUM_ALERT — the "sellers attacking" half.
    C = net call premium CALL_DRAWDOWN_ALERT below its session high-water mark.

    A and C alone mean buyers stepping back. B is the aggressive half. Firing
    A or C without B is information, not an exit signal — the playbook is
    explicit that flow is a confirmation/veto layer and never the trigger.
    """

    def __init__(self):
        self.calls = deque(maxlen=3)
        self.puts = deque(maxlen=3)
        self.call_high = None
        self.fired = defaultdict(float)   # name -> last fire time (dedupe)

    def _once(self, name: str, cooldown: float = 300.0) -> bool:
        now = time.time()
        if now - self.fired[name] < cooldown:
            return False
        self.fired[name] = now
        return True

    def update(self, net_call, net_put):
        alerts = []
        try:
            nc, npu = float(net_call), float(net_put)
        except (TypeError, ValueError):
            return alerts

        self.calls.append(nc)
        self.puts.append(npu)
        self.call_high = nc if self.call_high is None else max(self.call_high, nc)

        if len(self.calls) == 3:
            calls_falling = self.calls[0] > self.calls[1] > self.calls[2]
            puts_rising = self.puts[0] < self.puts[1] < self.puts[2]
            if calls_falling and puts_rising and self._once("A"):
                alerts.append(
                    f"TRIPWIRE A — reversal signature: calls draining "
                    f"({money(self.calls[0])} -> {money(self.calls[2])}) "
                    f"while puts wake up ({money(self.puts[0])} -> {money(self.puts[2])})"
                )

        if npu > PUT_PREMIUM_ALERT and self._once("B"):
            alerts.append(f"TRIPWIRE B — net put premium {money(npu)} (sellers attacking)")

        if self.call_high is not None:
            drawdown = self.call_high - nc
            if drawdown > CALL_DRAWDOWN_ALERT and self._once("C"):
                alerts.append(
                    f"TRIPWIRE C — net call premium {money(drawdown)} off the "
                    f"session high-water mark ({money(self.call_high)})"
                )
        return alerts


def handle(channel: str, payload, tw: Tripwires, watch: set, dp=None):
    """Return a list of lines to print. Keep this cheap — see drop policy."""
    out = []

    if channel.startswith("off_lit_trades"):
        # First branch on purpose: when --dark is on this is by far the highest
        # message rate on the socket, so it should not fall through every other
        # comparison first.
        return dp.add(payload, watch) if dp is not None else out

    if channel == "market_tide" and isinstance(payload, dict):
        nc = payload.get("net_call_premium")
        npu = payload.get("net_put_premium")
        out.append(f"[{ts()}] TIDE  calls {money(nc)}  puts {money(npu)}  vol {payload.get('net_volume','NA')}")
        for a in tw.update(nc, npu):
            out.append(f"[{ts()}] *** {a}")

    elif channel.startswith("gex"):
        if isinstance(payload, dict):
            t = payload.get("ticker", channel.split(":")[-1])
            if not watch or t in watch:
                out.append(
                    f"[{ts()}] GEX   {t}  magnet {payload.get('gamma_magnet','NA')}  "
                    f"call_wall {payload.get('call_wall','NA')}  put_wall {payload.get('put_wall','NA')}  "
                    f"flip {payload.get('gamma_flip','NA')}"
                )

    elif channel.startswith("net_flow") and isinstance(payload, dict):
        t = payload.get("ticker", channel.split(":")[-1])
        out.append(
            f"[{ts()}] FLOW  {t}  net_call {money(payload.get('net_call_premium'))}  "
            f"net_put {money(payload.get('net_put_premium'))}"
        )

    elif channel == "news" and isinstance(payload, dict):
        tickers = payload.get("tickers") or []
        relevant = (not watch) or (set(tickers) & watch)
        trump = payload.get("is_trump_ts")
        if relevant or trump:
            tag = "TRUTH" if trump else "NEWS "
            out.append(f"[{ts()}] {tag} {tickers} {str(payload.get('headline',''))[:160]}")

    elif channel == "trading_halts" and isinstance(payload, dict):
        # Always surface. A halt on an open position is not a "low priority" event.
        out.append(f"[{ts()}] *** HALT  {payload.get('ticker','?')}  {payload.get('state', payload)}")

    elif channel == "flow-alerts" and isinstance(payload, dict):
        t = payload.get("ticker")
        if not watch or t in watch:
            out.append(
                f"[{ts()}] ALERT {t} {payload.get('type','')} {payload.get('strike','')} "
                f"{payload.get('expiry','')} prem {money(payload.get('total_premium'))} "
                f"vol/oi {payload.get('volume_oi_ratio','NA')}"
            )
    return out


async def consumer(url, queue, channels, stats):
    """Receive loop. Does as little work as possible — the UW socket drops
    messages server-side if the client falls behind."""
    backoff = 1
    while True:
        try:
            async with websockets.connect(url, open_timeout=20, ping_interval=20) as ws:
                for ch in channels:
                    await ws.send(json.dumps({"channel": ch, "msg_type": "join"}))
                print(f"[{ts()}] connected; joined {', '.join(channels)}", flush=True)
                backoff = 1
                async for raw in ws:
                    stats["rx"] += 1
                    try:
                        queue.put_nowait(raw)
                    except asyncio.QueueFull:
                        # Drop oldest: a stale tide tick is worth less than a
                        # fresh one. Counted so "we fell behind" stays
                        # distinguishable from "server dropped".
                        try:
                            queue.get_nowait()
                            stats["dropped"] += 1
                            queue.put_nowait(raw)
                        except asyncio.QueueEmpty:
                            pass
        except Exception as e:
            print(f"[{ts()}] disconnected ({type(e).__name__}); retry in {backoff}s", flush=True)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


async def processor(queue, tw, watch, stats, dp=None):
    while True:
        raw = await queue.get()
        try:
            msg = json.loads(raw)
            if not isinstance(msg, list) or len(msg) != 2:
                continue
            channel, payload = msg
            if isinstance(payload, dict) and "status" in payload and "response" in payload:
                continue                      # join acknowledgement
            for line in handle(channel, payload, tw, watch, dp):
                print(line, flush=True)
        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 5:
                print(f"[{ts()}] parse error: {type(e).__name__}", flush=True)
        finally:
            queue.task_done()


async def heartbeat(stats, queue, dp=None):
    """Queue depth and drop counter. Without these, 'the server dropped it'
    and 'I fell behind' are indistinguishable."""
    while True:
        await asyncio.sleep(300)
        line = (f"[{ts()}] -- rx {stats['rx']}  dropped {stats['dropped']}  "
                f"errors {stats['errors']}  queue {queue.qsize()}")
        if dp is not None:
            # A climbing unparsed count means the payload schema is not what
            # _dp_fields guesses, and every dark line is therefore suspect.
            # Silence here would look identical to "no prints today".
            line += f"  dark_unparsed {dp.unparsed}"
        print(line, flush=True)


async def main():
    ap = argparse.ArgumentParser(description="UW websocket monitor")
    ap.add_argument("--tickers", default="SPY,QQQ", help="comma-separated watch list")
    ap.add_argument("--channels", default="", help="override channel list")
    ap.add_argument("--dark", action="store_true",
                    help="also join off_lit_trades (off-exchange prints). Opt-in: "
                         "it is the whole tape and can starve the channels that "
                         "drive decisions. Requires --tickers.")
    ap.add_argument("--dark-ticker-channels", action="store_true",
                    help="join off_lit_trades:TICKER instead of the bare channel. "
                         "UNVERIFIED — the suffix form may not be supported; watch "
                         "for a join acknowledgement before trusting it.")
    ap.add_argument("--queue-size", type=int, default=50_000)
    args = ap.parse_args()

    token = os.environ.get("UNUSUAL_WHALES_API_KEY")
    if not token:
        sys.exit("UNUSUAL_WHALES_API_KEY not set")

    watch = {t.strip().upper() for t in args.tickers.split(",") if t.strip()}
    if args.channels:
        channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    else:
        channels = ["market_tide", "news", "trading_halts"]
        for t in sorted(watch):
            channels += [f"gex:{t}", f"net_flow:{t}"]

    want_dark = args.dark or any(c.startswith("off_lit_trades") for c in channels)
    if want_dark and not watch:
        # Without a watch list every print in the market prints to the console,
        # which is useless and also the fastest way to fall behind the socket.
        sys.exit("--dark requires a non-empty --tickers watch list")
    if args.dark:
        channels += ([f"off_lit_trades:{t}" for t in sorted(watch)]
                     if args.dark_ticker_channels else ["off_lit_trades"])
    dp = DarkPool() if want_dark else None

    url = f"{WS_BASE}?token={token}"      # never print this
    queue = asyncio.Queue(maxsize=args.queue_size)
    stats = defaultdict(int)
    tw = Tripwires()

    print(f"[{ts()}] watching {', '.join(sorted(watch))}", flush=True)
    if dp is not None:
        print(f"[{ts()}] dark pool ON — clusters only "
              f"(>={DARK_CLUSTER_MIN_PRINTS} prints and "
              f"{_dp_money(DARK_CLUSTER_MIN_NOTIONAL)} per "
              f"{DARK_WINDOW_SEC // 60}m, filtered to the watch list). "
              f"Mid-relative side is INFERRED, never a signed side.", flush=True)
    await asyncio.gather(
        consumer(url, queue, channels, stats),
        processor(queue, tw, watch, stats, dp),
        heartbeat(stats, queue, dp),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nstopped")
