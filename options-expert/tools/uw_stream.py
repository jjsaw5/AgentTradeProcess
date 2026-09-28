#!/usr/bin/env python3
"""
Live Unusual Whales websocket monitor for intraday sessions.

Replaces the playbook's 5-minute REST polling (PLAYBOOK.md §4) with a push
feed. The tripwires are the same ones, evaluated on completed 5-minute buckets
summed from the socket's ~2-second tide increments (cumulative since the
stream started — start it before the open or the morning is missing). Since 2026-09-28 it is also the odte-desk's live layer
(odte-desk/SKILL.md §3, §8): per-contract tape, live gamma aggregate, price
and volume, every headline, rolled up into a FRAME block on each wall-clock
boundary and appended to a JSONL file the scheduled desk read consumes.

    python uw_stream.py --tickers SPY,QQQ
    python uw_stream.py --tickers SPY,QQQ --contracts SPY260930P00738000 \
        --frame-file /path/to/stream-2026-09-30.jsonl
    python uw_stream.py --tickers SPY --channels market_tide,news,trading_halts

Requires:  pip install websockets
Auth:      UNUSUAL_WHALES_API_KEY in the environment. Never passed on argv,
           never logged — the token rides in the URL, so the URL is never
           printed either.

Verified against wss://api.unusualwhales.com/socket: market_tide, gex:TICKER,
news, trading_halts (2026-08-18, after the close); option_trades:TICKER,
price:TICKER, flow-alerts (2026-09-28, market open — see
odte-desk/log/2026-09-28-PROBE.md for payload shapes and rates: ~80 prints/s
on option_trades:SPY, exec→receive median 30 ms).

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

# Per-print alert on a watched contract at or above this premium (dollars).
# A round number chosen 2026-09-28 with no evidence behind it; the frame
# roll-up is the product, this is only the "look now" line.
BIG_PRINT_USD = 50_000


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


def fnum(v):
    """float or None — never 0.0 for a missing measurement (CLAUDE.md §4)."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


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
        self.last = {}                    # latest tide reading, for the frame

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
        self.last = {"net_call_premium": nc, "net_put_premium": npu, "at": ts()}

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


class FrameState:
    """Everything the desk wants rolled up per frame (odte-desk/SKILL.md §5).

    Accumulates between wall-clock boundaries; `snapshot()` returns the frame
    dict and resets the per-frame counters. Latest-value fields (price, gex,
    tide) carry across frames; counters (prints, premium, headlines) reset.
    Missing measurements stay None — never 0.0 (CLAUDE.md §4).
    """

    def __init__(self, contracts: set):
        self.contracts = contracts                # option_symbols to track
        self.frame_no = 0
        self.frame_open = time.time()
        self.tape = {c: self._blank() for c in contracts}
        self.price = {}                           # ticker -> latest price msg
        self.gex = {}                             # ticker -> latest gex msg
        self.gex_sign = {}                        # ticker -> (sign_oi, sign_vol)
        self.headlines = []                       # this frame's headlines
        self.halts = []
        self.alerts = 0                           # flow-alerts count this frame
        # Socket market_tide and net_flow payloads are ~2-second INCREMENTS
        # (verified 2026-09-28), not the session-cumulative values the REST
        # market-tide returns. They are summed here from stream start and
        # labelled "since hh:mm" — a stream started at 1:00 does not know
        # the morning. Tripwires evaluate on completed 5-minute buckets.
        self.started = ts()
        self.tide_cum = {"net_call_premium": 0.0, "net_put_premium": 0.0, "net_volume": 0}
        self.tide_bucket = None                   # current 5-min bucket key
        self.flow_cum = {}                        # ticker -> cumulative net_call/put prem+vol

    @staticmethod
    def _blank():
        return {
            "prints": 0, "ask_side": 0, "bid_side": 0, "mid_side": 0,
            "ask_prem": 0.0, "bid_prem": 0.0, "mid_prem": 0.0,
            "first_mid": None, "last_mid": None, "last_price": None,
            "last_bid": None, "last_ask": None, "volume": None,
            "open_interest": None, "last_at": None, "big_prints": [],
        }

    def trade(self, p: dict):
        """One option_trades print. Returns alert lines (big prints only)."""
        sym = p.get("option_symbol")
        if sym not in self.tape:
            return []
        t = self.tape[sym]
        prem = fnum(p.get("premium"))
        tags = p.get("tags") or []
        side = next((x for x in ("ask_side", "bid_side", "mid_side") if x in tags), None)
        t["prints"] += 1
        if side:
            t[side] += 1
            if prem is not None:
                t[side.replace("_side", "_prem")] += prem
        bid, ask = fnum(p.get("nbbo_bid")), fnum(p.get("nbbo_ask"))
        mid = (bid + ask) / 2 if bid is not None and ask is not None else None
        if mid is not None:
            if t["first_mid"] is None:
                t["first_mid"] = mid
            t["last_mid"] = mid
        t["last_price"] = fnum(p.get("price"))
        t["last_bid"], t["last_ask"] = bid, ask
        t["volume"] = p.get("volume", t["volume"])
        t["open_interest"] = p.get("open_interest", t["open_interest"])
        t["last_at"] = p.get("executed_at")
        out = []
        if prem is not None and prem >= BIG_PRINT_USD:
            line = (f"BIG PRINT {sym} {side or 'no_side'} size {p.get('size')} @ {p.get('price')} "
                    f"= {money(prem)}  nbbo {bid}/{ask}  spot {p.get('underlying_price')}")
            t["big_prints"].append(line)
            out.append(f"[{ts()}] *** {line}")
        return out

    def tide_increment(self, p: dict):
        """Sum a market_tide increment. Returns the completed 5-min bucket's
        cumulative reading when a bucket rolls over, else None."""
        nc, npu = fnum(p.get("net_call_premium")), fnum(p.get("net_put_premium"))
        if nc is not None:
            self.tide_cum["net_call_premium"] += nc
        if npu is not None:
            self.tide_cum["net_put_premium"] += npu
        try:
            self.tide_cum["net_volume"] += int(p.get("net_volume") or 0)
        except (TypeError, ValueError):
            pass
        stamp = str(p.get("timestamp", ""))          # 2026-09-28T17:31:20Z
        bucket = stamp[:14] + ("%02d" % (int(stamp[14:16]) // 5 * 5)) if len(stamp) >= 16 else None
        if bucket != self.tide_bucket:
            prev = self.tide_bucket
            self.tide_bucket = bucket
            if prev is not None:
                return dict(self.tide_cum, bucket=prev)
        return None

    def flow_increment(self, t: str, p: dict):
        f = self.flow_cum.setdefault(t, {"net_call_prem": 0.0, "net_put_prem": 0.0,
                                         "net_call_vol": 0, "net_put_vol": 0})
        for k in ("net_call_prem", "net_put_prem"):
            v = fnum(p.get(k))
            if v is not None:
                f[k] += v
        for k in ("net_call_vol", "net_put_vol"):
            try:
                f[k] += int(p.get(k) or 0)
            except (TypeError, ValueError):
                pass

    def gex_update(self, t: str, p: dict):
        """Live aggregate gamma. Returns an alert line on a sign flip."""
        self.gex[t] = p
        g_oi = fnum(p.get("gamma_per_one_percent_move_oi"))
        g_vol = fnum(p.get("gamma_per_one_percent_move_vol"))
        sign = (None if g_oi is None else g_oi > 0, None if g_vol is None else g_vol > 0)
        prev = self.gex_sign.get(t)
        self.gex_sign[t] = sign
        if prev is not None and prev != sign and None not in sign:
            lab = lambda s: "POS" if s else "NEG"
            return (f"[{ts()}] *** GEX FLIP {t}  oi {lab(prev[0])}->{lab(sign[0])}  "
                    f"vol {lab(prev[1])}->{lab(sign[1])}  spot {p.get('price')}")
        return None

    def snapshot(self, tw: "Tripwires", stats: dict) -> dict:
        self.frame_no += 1
        now = time.time()
        frame = {
            "frame": self.frame_no,
            "opened": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.frame_open)),
            "closed": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now)),
            "tz": time.strftime("%Z"),
            "price": {t: {"close": fnum(p.get("close")), "vol": p.get("vol"),
                          "time": p.get("time")} for t, p in self.price.items()},
            "gex": {t: {k: fnum(p.get(k)) for k in (
                        "gamma_per_one_percent_move_oi", "gamma_per_one_percent_move_vol",
                        "gamma_per_one_percent_move_dir", "delta_per_one_percent_move_oi",
                        "charm_per_one_percent_move_oi", "vanna_per_one_percent_move_oi")}
                    | {"price": fnum(p.get("price")), "timestamp": p.get("timestamp")}
                    for t, p in self.gex.items()},
            "tide_since_start": dict(self.tide_cum, since=self.started),
            "tide_last_bucket": dict(tw.last) if tw.last else None,
            "net_flow_since_start": {t: dict(v) for t, v in self.flow_cum.items()},
            "contracts": {},
            "headlines": list(self.headlines),
            "halts": list(self.halts),
            "flow_alerts": self.alerts,
            "stream": {"rx": stats["rx"], "dropped": stats["dropped"], "errors": stats["errors"]},
        }
        for sym, t in self.tape.items():
            drift = (None if t["first_mid"] is None or t["last_mid"] is None
                     else round(t["last_mid"] - t["first_mid"], 4))
            frame["contracts"][sym] = {
                "prints": t["prints"], "ask_side": t["ask_side"], "bid_side": t["bid_side"],
                "mid_side": t["mid_side"],
                "ask_prem": round(t["ask_prem"], 2) if t["prints"] else None,
                "bid_prem": round(t["bid_prem"], 2) if t["prints"] else None,
                "nbbo_mid_drift": drift, "last_price": t["last_price"],
                "last_bid": t["last_bid"], "last_ask": t["last_ask"],
                "volume": t["volume"], "open_interest": t["open_interest"],
                "last_at": t["last_at"], "big_prints": list(t["big_prints"]),
            }
        # reset the per-frame counters; latest-value fields carry over
        self.tape = {c: self._blank() for c in self.contracts}
        self.headlines, self.halts, self.alerts = [], [], 0
        self.frame_open = now
        return frame


def render_frame(f: dict) -> str:
    """The FRAME block, human-readable. The JSONL line is the record."""
    lines = [f"[{ts()}] ===== FRAME {f['frame']}  {f['opened'][11:]} -> {f['closed'][11:]} {f['tz']} ====="]
    for t, p in sorted(f["price"].items()):
        lines.append(f"  PRICE {t}  {p['close']}  cum vol {p['vol']}  (basis UNVERIFIED)")
    for t, g in sorted(f["gex"].items()):
        lines.append(f"  GEX   {t}  gamma/1% oi {money(g['gamma_per_one_percent_move_oi'])}  "
                     f"vol {money(g['gamma_per_one_percent_move_vol'])}  "
                     f"dir {money(g['gamma_per_one_percent_move_dir'])}  spot {g['price']}")
    tc = f["tide_since_start"]
    lines.append(f"  TIDE  calls {money(tc['net_call_premium'])}  puts {money(tc['net_put_premium'])}  "
                 f"(cumulative since {tc['since']}, socket increments — not the REST session tide)")
    for t, v in sorted(f["net_flow_since_start"].items()):
        lines.append(f"  NFLOW {t}  net_call {money(v['net_call_prem'])} ({v['net_call_vol']:+d})  "
                     f"net_put {money(v['net_put_prem'])} ({v['net_put_vol']:+d})  since {tc['since']}")
    for sym, c in sorted(f["contracts"].items()):
        if c["prints"] == 0:
            lines.append(f"  TAPE  {sym}  no prints this frame")
            continue
        lines.append(
            f"  TAPE  {sym}  {c['prints']} prints  ask {c['ask_side']} ({money(c['ask_prem'])})  "
            f"bid {c['bid_side']} ({money(c['bid_prem'])})  mid {c['mid_side']}  "
            f"last {c['last_price']}  nbbo {c['last_bid']}/{c['last_ask']}  "
            f"mid drift {c['nbbo_mid_drift']}  vol {c['volume']}  oi {c['open_interest']}"
        )
    lines.append(f"  NEWS  {len(f['headlines'])} headline(s)  ALERTS {f['flow_alerts']}  "
                 f"HALTS {len(f['halts'])}  stream rx {f['stream']['rx']} dropped {f['stream']['dropped']}")
    return "\n".join(lines)


def handle(channel: str, payload, tw: Tripwires, watch: set, fs: FrameState):
    """Return a list of lines to print. Keep this cheap — see drop policy."""
    out = []

    if channel == "market_tide" and isinstance(payload, dict):
        # ~2-second increments (verified 2026-09-28). Summed; the tripwires
        # see one reading per completed 5-minute bucket, as the playbook's
        # "completed bars only" rule requires. Per-tick printing removed —
        # it was 30 lines a minute of noise.
        done = fs.tide_increment(payload)
        if done:
            out.append(f"[{ts()}] TIDE  5m bucket {done['bucket'][11:]}  cum calls {money(done['net_call_premium'])}  "
                       f"puts {money(done['net_put_premium'])}  (since {fs.started})")
            for a in tw.update(done["net_call_premium"], done["net_put_premium"]):
                out.append(f"[{ts()}] *** {a}")

    elif channel.startswith("gex") and isinstance(payload, dict):
        # Socket payload (verified 2026-09-28) is the aggregate greek exposure
        # per 1% move, split _oi/_vol/_dir, with a ms timestamp. It does NOT
        # carry call_wall/put_wall/gamma_flip — those are the REST gex-levels.
        t = payload.get("ticker", channel.split(":")[-1])
        if not watch or t in watch:
            flip = fs.gex_update(t, payload)
            if flip:
                out.append(flip)

    elif channel.startswith("price") and isinstance(payload, dict):
        t = payload.get("ticker", channel.split(":")[-1])
        fs.price[t] = payload

    elif channel.startswith("option_trades") and isinstance(payload, dict):
        out.extend(fs.trade(payload))

    elif channel.startswith("net_flow") and isinstance(payload, dict):
        # Keys are net_call_prem / net_put_prem / net_call_vol / net_put_vol
        # (NOT net_call_premium), per-tick increments. Summed into the frame.
        t = payload.get("ticker", channel.split(":")[-1])
        fs.flow_increment(t, payload)

    elif channel == "news" and isinstance(payload, dict):
        # Every headline is kept for the frame (odte-desk §8: the war-headline
        # tape is mostly ticker-less macro headlines). Printed live when it
        # names a watched ticker, is a Truth Social post, or has no tickers.
        tickers = payload.get("tickers") or []
        trump = bool(payload.get("is_trump_ts"))
        held = bool(set(tickers) & watch)
        rec = {"at": ts(), "ts": payload.get("timestamp"), "source": payload.get("source"),
               "tickers": tickers, "trump": trump, "held": held,
               "headline": str(payload.get("headline", ""))[:240]}
        fs.headlines.append(rec)
        if held or trump or not tickers:
            tag = "TRUTH" if trump else ("HELD " if held else "MACRO")
            out.append(f"[{ts()}] {tag} {tickers} {rec['headline'][:160]}")

    elif channel == "trading_halts" and isinstance(payload, dict):
        # Always surface. A halt on an open position is not a "low priority" event.
        fs.halts.append({"at": ts(), "ticker": payload.get("ticker"), "state": payload.get("state")})
        out.append(f"[{ts()}] *** HALT  {payload.get('ticker','?')}  {payload.get('state', payload)}")

    elif channel == "flow-alerts" and isinstance(payload, dict):
        # Verified shape 2026-09-28: ticker, option_chain, total_premium,
        # total_ask_side_prem, total_bid_side_prem, has_sweep/has_floor,
        # open_interest, volume, underlying_price, rule_name.
        t = payload.get("ticker")
        if not watch or t in watch:
            fs.alerts += 1
            out.append(
                f"[{ts()}] ALERT {t} {payload.get('option_chain','')} {payload.get('rule_name','')} "
                f"prem {money(payload.get('total_premium'))} "
                f"ask {money(payload.get('total_ask_side_prem'))} bid {money(payload.get('total_bid_side_prem'))} "
                f"vol {payload.get('volume','NA')} oi {payload.get('open_interest','NA')}"
                f"{'  SWEEP' if payload.get('has_sweep') else ''}{'  FLOOR' if payload.get('has_floor') else ''}"
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


async def processor(queue, tw, watch, fs, stats):
    while True:
        raw = await queue.get()
        try:
            msg = json.loads(raw)
            if not isinstance(msg, list) or len(msg) != 2:
                continue
            channel, payload = msg
            if isinstance(payload, dict) and "status" in payload and "response" in payload:
                if payload.get("status") != "ok":
                    print(f"[{ts()}] *** join {channel}: {payload.get('status')}", flush=True)
                continue                      # join acknowledgement
            for line in handle(channel, payload, tw, watch, fs):
                print(line, flush=True)
        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 5:
                print(f"[{ts()}] parse error: {type(e).__name__}", flush=True)
        finally:
            queue.task_done()


async def framer(fs, tw, stats, interval, frame_file):
    """Print the FRAME block and append its JSON on every wall-clock boundary
    (interval=900 → :00/:15/:30/:45, the day cards' verdict candle).
    Boundaries are computed on the wall clock so a late start still lands on
    the next boundary rather than an offset."""
    while True:
        now = time.time()
        await asyncio.sleep(interval - (now % interval))
        frame = fs.snapshot(tw, stats)
        print(render_frame(frame), flush=True)
        if frame_file:
            try:
                with open(frame_file, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(frame, separators=(",", ":")) + "\n")
            except OSError as e:
                print(f"[{ts()}] *** frame file write failed: {type(e).__name__}", flush=True)


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
    ap.add_argument("--contracts", default="",
                    help="comma-separated OCC option symbols to tape (e.g. SPY260930P00738000); "
                         "their underlyings are added to the watch list")
    ap.add_argument("--channels", default="", help="override channel list")
    ap.add_argument("--frame-interval", type=int, default=900,
                    help="seconds between FRAME roll-ups, wall-clock aligned (default 900 = 15 min)")
    ap.add_argument("--frame-file", default="",
                    help="append one JSON line per frame here (the desk's scheduled read consumes it)")
    ap.add_argument("--no-tape", action="store_true",
                    help="do not join option_trades:TICKER (the heaviest channel)")
    ap.add_argument("--queue-size", type=int, default=50_000)
    args = ap.parse_args()

    token = os.environ.get("UNUSUAL_WHALES_API_KEY")
    if not token:
        sys.exit("UNUSUAL_WHALES_API_KEY not set")

    watch = {t.strip().upper() for t in args.tickers.split(",") if t.strip()}
    contracts = {c.strip().upper() for c in args.contracts.split(",") if c.strip()}
    for c in contracts:
        # OCC symbol: root padded to 6 then YYMMDD C/P strike*1000 (8 digits)
        watch.add(c[:-15].strip())
    if args.channels:
        channels = [c.strip() for c in args.channels.split(",") if c.strip()]
    else:
        channels = ["market_tide", "news", "trading_halts", "flow-alerts"]
        for t in sorted(watch):
            channels += [f"gex:{t}", f"net_flow:{t}", f"price:{t}"]
            if not args.no_tape:
                channels.append(f"option_trades:{t}")

    url = f"{WS_BASE}?token={token}"      # never print this
    queue = asyncio.Queue(maxsize=args.queue_size)
    stats = defaultdict(int)
    tw = Tripwires()
    fs = FrameState(contracts)

    print(f"[{ts()}] watching {', '.join(sorted(watch))}"
          f"{'  taping ' + ', '.join(sorted(contracts)) if contracts else ''}"
          f"  frame every {args.frame_interval}s"
          f"{'  -> ' + args.frame_file if args.frame_file else ''}", flush=True)
    await asyncio.gather(
        consumer(url, queue, channels, stats),
        processor(queue, tw, watch, fs, stats),
        framer(fs, tw, stats, args.frame_interval, args.frame_file),
        heartbeat(stats, queue),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nstopped")
