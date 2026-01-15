from fastapi import FastAPI
import asyncio
from database import init_db, insert_batch

app = FastAPI()

event_queue = asyncio.Queue(maxsize=100000)
db_conn = init_db()

BATCH_SIZE = 100
FLUSH_INTERVAL = 1  # seconds

@app.on_event("startup")
async def start_worker():
    asyncio.create_task(background_worker())

@app.post("/event", status_code=202)
async def collect_event(event: dict):
    await event_queue.put(event)
    return {"status": "accepted"}

async def background_worker():
    batch = []
    while True:
        try:
            event = await asyncio.wait_for(event_queue.get(), timeout=FLUSH_INTERVAL)
            batch.append(event)

            if len(batch) >= BATCH_SIZE:
                insert_batch(db_conn, batch)
                batch.clear()

        except asyncio.TimeoutError:
            if batch:
                insert_batch(db_conn, batch)
                batch.clear()
