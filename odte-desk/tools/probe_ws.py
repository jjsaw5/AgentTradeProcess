#!/usr/bin/env python3
# Probe the Unusual Whales websocket for the odte-desk channels: news,
# option_trades:TICKER (per-contract counts, aggressor tags, exec->recv latency),
# flow-alerts, price:TICKER. Runs 60 s. Key from the environment; never printed.
# Usage: UNUSUAL_WHALES_API_KEY=... python3 probe_ws.py   (needs: pip install websockets certifi)
import asyncio, json, os, ssl, time, certifi, websockets
from collections import Counter
KEY=os.environ["UNUSUAL_WHALES_API_KEY"]
URL=f"wss://api.unusualwhales.com/socket?token={KEY}"
CH=["news","option_trades:SPY","flow-alerts","price:SPY"]
async def main():
    ctx=ssl.create_default_context(cafile=certifi.where())
    counts=Counter(); acks={}; samples={}; per_contract=Counter(); side=Counter(); latency=[]
    t0=time.time()
    try:
        async with websockets.connect(URL, ssl=ctx, max_queue=8192) as ws:
            for c in CH: await ws.send(json.dumps({"channel":c,"msg_type":"join"}))
            while time.time()-t0<60:
                try: raw=await asyncio.wait_for(ws.recv(), timeout=5)
                except asyncio.TimeoutError: continue
                try: ch,payload=json.loads(raw)
                except Exception: counts["unparsed"]+=1; continue
                if isinstance(payload,dict) and "status" in payload and "response" in payload:
                    acks[ch]=payload["status"]; continue
                counts[ch]+=1
                if ch=="option_trades:SPY":
                    per_contract[payload.get("option_symbol")]+=1
                    for t in payload.get("tags",[]):
                        if t.endswith("_side"): side[t]+=1
                    latency.append(time.time()*1000-payload["executed_at"])
                if ch not in samples: samples[ch]=payload
    except Exception as e:
        print("ERROR:", type(e).__name__, str(e).replace(KEY,"<KEY>"))
    print("elapsed", round(time.time()-t0,1),"s; acks", acks); print("counts", dict(counts))
    print("top contracts:", per_contract.most_common(5)); print("aggressor tags:", dict(side))
    if latency: latency.sort(); print("exec->recv latency ms: median", int(latency[len(latency)//2]), "p90", int(latency[int(len(latency)*.9)]))
    for ch,p in samples.items():
        if ch!="option_trades:SPY": print("sample",ch,":",json.dumps(p)[:500].replace(KEY,"<KEY>"))
asyncio.run(main())
