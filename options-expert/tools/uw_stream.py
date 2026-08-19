#!/usr/bin/env python3
"""
Live Unusual Whales websocket monitor for intraday sessions.

Replaces the playbook's 5-minute REST polling (PLAYBOOK.md §4) with a push
feed. The tripwires are the same ones, evaluated on live data instead of
completed-bar polls.

    python uw_stream.py --tickers SPY,QQQ
    python uw_stream.py --tickers SPY --channels market_tide,news,trading_halts

Requires:  pip install websockets
Auth:      UNUSUAL_WHALES_API_KEY in the environment. Never passed on argv,
           never logged — the token rides in the URL, so the URL is never
           printed either.

Verified against wss://api.unusualwhales.com/socket on 2026-08-18: all of
market_tide, gex:TICKER, news and trading_halts joined with status ok.

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


def handle(channel: str, payload, tw: Tripwires, watch: set):
    """Return a list of lines to print. Keep this cheap — see drop policy."""
    out = []

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


async def processor(queue, tw, watch, stats):
    while True:
        raw = await queue.get()
        try:
            msg = json.loads(raw)
            if not isinstance(msg, list) or len(msg) != 2:
                continue
            channel, payload = msg
            if isinstance(payload, dict) and "status" in payload and "response" in payload:
                continue                      # join acknowledgement
            for line in handle(channel, payload, tw, watch):
                print(line, flush=True)
        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 5:
                print(f"[{ts()}] parse error: {type(e).__name__}", flush=True)
        finally:
            queue.task_done()


async def heartbeat(stats, queue):
    """Queue depth and drop counter. Without these, 'the server dropped it'
    and 'I fell behind' are indistinguishable."""
    while True:
        await asyncio.sleep(300)
        print(
            f"[{ts()}] -- rx {stats['rx']}  dropped {stats['dropped']}  "
            f"errors {stats['errors']}  queue {queue.qsize()}",
            flush=True,
        )


async def main():
    ap = argparse.ArgumentParser(description="UW websocket monitor")
    ap.add_argument("--tickers", default="SPY,QQQ", help="comma-separated watch list")
    ap.add_argument("--channels", default="", help="override channel list")
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

    url = f"{WS_BASE}?token={token}"      # never print this
    queue = asyncio.Queue(maxsize=args.queue_size)
    stats = defaultdict(int)
    tw = Tripwires()

    print(f"[{ts()}] watching {', '.join(sorted(watch))}", flush=True)
    await asyncio.gather(
        consumer(url, queue, channels, stats),
        processor(queue, tw, watch, stats),
        heartbeat(stats, queue),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nstopped")
