---
name: websocket
description: Use when the user wants to consume the UnusualWhales websocket at wss://api.unusualwhales.com/socket — connecting, subscribing to channels, and processing high-throughput messages without dropping data.
---

# UnusualWhales websocket

## When to use

When the user asks to work with the UnusualWhales websocket at `wss://api.unusualwhales.com/socket`.

## First step: get current docs

Before writing code, fetch the live channel docs — the available channels and subscribe frame shape change:

```
curl https://api.unusualwhales.com/docs/operations/PublicApi.SocketController.channels
```

Use the response to determine valid channels and the exact subscribe message format.

## What makes this socket different

High throughput hundreds to thousands of messages per second. **If the consumer can't keep up, the server drops messages on its side.** This means:

- The receive loop must do as little work as possible.
- Any DB or disk writes must be batched. One insert per message will not keep up.

## Decisions to confirm with the user

- **Batch flush trigger:** by size, by time, or both (both is usually right — size for throughput, time so quiet periods still flush).
- **Sink:** database (use `executemany` / `COPY`), files (one write per batch), or HTTP bulk endpoint.

## Reference sketch

```python
import asyncio, json, websockets

queue = asyncio.Queue(maxsize=50_000)  # ~throughput * acceptable_lag_seconds

async def ws_consumer(url):
    async with websockets.connect(url) as ws:
        # send subscribe frame(s) here — see live docs for shape
        async for raw_msg in ws:
            try:
                queue.put_nowait(raw_msg)
            except asyncio.QueueFull:
                # pick policy with user — example: drop oldest, drop newest or wait
                queue.get_nowait()
                queue.put_nowait(raw_msg)

async def processor():
    batch = []
    while True:
        raw_msg = await queue.get()
        try:
            batch.append(json.loads(raw_msg))
            if len(batch) >= BATCH_SIZE:  # and/or time-based trigger
                await flush_batch(batch)
                batch.clear()
        finally:
            queue.task_done()

async def main():
    await asyncio.gather(ws_consumer(URL), processor())

asyncio.run(main())
```

## Things to add for production

- Reconnect loop with exponential backoff, resubscribe on reconnect.
- Queue depth + drop counter logging — without these, "server dropped" and "I fell behind" are indistinguishable.
- `orjson` over stdlib `json` at high message rates.
- Auth token from env, never hardcoded.
