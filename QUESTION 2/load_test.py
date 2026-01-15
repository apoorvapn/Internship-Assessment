import asyncio
import aiohttp
import time

URL = "http://127.0.0.1:8000/event"
TOTAL_REQUESTS = 1000

async def send_event(session, i):
    payload = {
        "user_id": i,
        "timestamp": "2026-01-12T10:00:00Z",
        "metadata": {
            "page": "home",
            "click_id": i
        }
    }
    async with session.post(URL, json=payload):
        pass

async def main():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [send_event(session, i) for i in range(TOTAL_REQUESTS)]
        await asyncio.gather(*tasks)
    print("Completed in", time.time() - start, "seconds")

asyncio.run(main())
