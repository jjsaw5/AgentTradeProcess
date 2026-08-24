#!/usr/bin/env python3
"""
Offline checks for uw_stream.py's dark pool layer (SKILL.md E2b).

    python test_uw_stream.py

Zero network, zero API key, about a second. Run it after touching the dark pool
code in uw_stream.py -- the wiring is easy to break in ways that produce
plausible console lines rather than an error, which is the failure mode this
repo cares about most.

What it does NOT prove: that the live off_lit_trades payload looks anything like
the fixtures here. The schema is unconfirmed (see uw_stream.py's DARK POOL
section); these fixtures encode what we GUESS the payload is, so a pass here
means the parser handles that shape, not that the shape is right. The one-shot
schema dump on the first live payload is what settles that, and the answer
belongs in DATA_LAYER.md §3a.
"""
import sys, types, importlib.util
sys.modules.setdefault("websockets", types.ModuleType("websockets"))
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "uw_stream", os.path.join(_HERE, "uw_stream.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class FakeTime:
    def __init__(self): self.t = 1_000_000.0
    def time(self): return self.t
    def strftime(self, f): return "12:00:00"
    def sleep(self, n): pass
ft = FakeTime(); m.time = ft

checks = []
def ok(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

def pr(tkr="NVDA", price=100.0, size=50_000, bid=99.98, ask=100.02, **kw):
    d = {"ticker": tkr, "price": price, "size": size,
         "nbbo_bid": bid, "nbbo_ask": ask}
    d.update(kw); return d

# --- _dp_fields classification ---
ok("above mid", m._dp_fields(pr(price=100.02))[2] == "above")
ok("below mid", m._dp_fields(pr(price=99.98))[2] == "below")
ok("at mid", m._dp_fields(pr(price=100.00))[2] == "at")
ok("mid tolerance absorbs float noise",
   m._dp_fields(pr(price=100.0 + 1e-12))[2] == "at")
ok("no NBBO -> side is None, NOT 'at'",
   m._dp_fields({"ticker":"X","price":10.0,"size":100})[2] is None)
ok("notional from price*size", m._dp_fields(pr())[1] == 100.0*50_000)
ok("explicit premium wins over price*size",
   m._dp_fields(pr(premium=7_777_777))[1] == 7_777_777)
ok("no ticker -> unparseable", m._dp_fields({"price":1,"size":1}) is None)
ok("no size and no premium -> unparseable",
   m._dp_fields({"ticker":"X","price":10.0}) is None)
ok("string numerics coerce", m._dp_fields(pr(price="100.02"))[2] == "above")
ok("crossed/None NBBO falls back to no side",
   m._dp_fields(pr(bid=None, ask=None))[2] is None)
ok("alt key names work (symbol/notional)",
   m._dp_fields({"symbol":"abc","notional":5e6})[0] == "ABC")

# --- cluster gating ---
W = {"NVDA"}
dp = m.DarkPool()
out = dp.add(pr(premium=2e6), W)
ok("first payload dumps the schema", any("schema" in l for l in out))
ok("schema dumps only once", not any("schema" in l for l in dp.add(pr(premium=2e6), W)))
lines = dp.add(pr(premium=2e6), W)
ok("3 prints do not fire a cluster", not any("DARK " in l for l in lines))
lines = dp.add(pr(premium=2e6), W)
ok("4th print crosses count+notional and fires", any("DARK " in l for l in lines))
ok("cluster line reports the split", any("above" in l and "below mid" in l for l in lines))
ok("cluster line carries the inference caveat",
   any("not a signed side" in l for l in lines))
ok("cooldown suppresses an immediate refire",
   not any("DARK " in l for l in dp.add(pr(premium=2e6), W)))

# --- notional floor: many tiny prints must NOT fire ---
dp2 = m.DarkPool(); dp2.schema_dumped = True
fired = [l for _ in range(20) for l in dp2.add(pr(premium=1000), W)]
ok("20 tiny prints never reach the notional floor", not any("DARK " in l for l in fired))

# --- watch filter ---
dp3 = m.DarkPool(); dp3.schema_dumped = True
out = [l for _ in range(10) for l in dp3.add(pr(tkr="AAPL", premium=9e6), W)]
ok("off-watchlist ticker emits nothing", out == [])
ok("off-watchlist ticker is not accumulated", "AAPL" not in dp3.prints)

# --- window eviction ---
dp4 = m.DarkPool(); dp4.schema_dumped = True
for _ in range(3): dp4.add(pr(premium=2e6), W)
ft.t += m.DARK_WINDOW_SEC + 1
lines = dp4.add(pr(premium=2e6), W)
ok("prints older than the window are evicted, so no cluster",
   not any("DARK " in l for l in lines) and len(dp4.prints["NVDA"]) == 1)

# --- single large print ---
dp5 = m.DarkPool(); dp5.schema_dumped = True
lines = dp5.add(pr(premium=30e6), W)
ok("a single huge print surfaces", any("single print" in l for l in lines))
ok("and is marked not citable", any("not citable" in l for l in lines))

# --- NA_unresolved is reported, never bucketed as 'at' ---
dp6 = m.DarkPool(); dp6.schema_dumped = True
for _ in range(4): dp6.add({"ticker":"NVDA","premium":2e6}, W)
lines = [l for l in dp6.add({"ticker":"NVDA","premium":2e6}, W)]
dp6b = m.DarkPool(); dp6b.schema_dumped = True
out = []
for _ in range(4): out += dp6b.add({"ticker":"NVDA","premium":2e6}, W)
ok("unclassifiable prints report NA_unresolved in the split",
   any("NA_unresolved" in l for l in out), out)
ok("unclassifiable prints are not counted as 'at mid'",
   any("0 at " in l for l in out), out)

# --- unparsed counter ---
dp7 = m.DarkPool(); dp7.schema_dumped = True
for _ in range(3): dp7.add({"garbage": 1}, W)
ok("unparseable payloads are counted, not silently dropped", dp7.unparsed == 3)

# --- handle() routing ---
ok("handle routes off_lit_trades to the accumulator",
   m.handle("off_lit_trades", pr(premium=30e6), None, W, m.DarkPool()) != [])
ok("handle with dp=None returns nothing rather than raising",
   m.handle("off_lit_trades", pr(premium=30e6), None, W, None) == [])
ok("suffixed channel name also routes",
   m.handle("off_lit_trades:NVDA", pr(premium=30e6), None, W, m.DarkPool()) != [])

bad = [c for c in checks if not c[1]]
for n, p, d in checks:
    if not p: print(f"FAIL  {n}  {d}")
print(f"\n{len(checks)-len(bad)}/{len(checks)} checks passed")
sys.exit(1 if bad else 0)
