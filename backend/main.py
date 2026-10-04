import logging
from contextlib import asynccontextmanager
from datetime import datetime

import config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agents.commitment_agent import extract_commitments
from agents.digest_agent import build_state_pack, caregiver_pack, write_digest
from agents.qa_agent import answer_question
from agents.repetition_agent import detect_repetition
from aws.bedrock_client import health_check, llm_mode
from config import BACKEND_DIR, DEFAULT_DATE
from ingest.bee_adapter import get_source
from ingest.store import get_store
from models import AddReminderRequest, QARequest
from reminders import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    ok = health_check()
    logging.info("LLM (%s) health: %s", llm_mode(), "OK" if ok else "FAILED - check model access/credentials")
    logging.info("Store: %s", get_store().kind)
    yield


app = FastAPI(title="EchoMind", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _day(date: str) -> dict:
    """Return the stored day, auto-ingesting from the active source if missing."""
    store = get_store()
    rec = store.get_day_record(date)
    if rec is None:
        store.store_day(get_source().get_day(date))
        rec = store.get_day_record(date)
    return rec["day"]


@app.get("/api/health")
def health():
    return {"status": "ok", "llm": llm_mode(), "store": get_store().kind}


@app.get("/api/day")
def get_day(date: str | None = None):
    return get_source().get_day(date)


@app.post("/api/ingest")
def ingest_day(date: str | None = None):
    day = get_source().get_day(date)
    return {"ingested": True, "date": get_store().store_day(day), "segments": len(day["segments"])}


@app.get("/api/record/{date}")
def get_record(date: str):
    rec = get_store().get_day_record(date)
    if rec is None:
        raise HTTPException(404, f"No stored day for {date}")
    return rec


@app.post("/api/commitments/extract")
def run_commitment_agent(date: str = DEFAULT_DATE):
    commitments = extract_commitments(_day(date))
    get_store().save_commitments(date, commitments)
    return {"extracted": len(commitments), "commitments": [c.model_dump() for c in commitments]}


@app.get("/api/commitments/{date}")
def list_commitments(date: str, status: str | None = None):
    return get_store().get_commitments(date, status)


@app.post("/api/reminders/build")
def build_reminders(date: str = DEFAULT_DATE):
    """day -> commitments -> repetition scan -> reminders. Idempotent: existing reminders keep their state."""
    day, store = _day(date), get_store()
    commitments = extract_commitments(day)
    store.save_commitments(date, commitments)
    repetition = detect_repetition(day)
    existing = {r["commitment_id"]: r for r in store.get_reminders(date)}
    for r in engine.create_reminders([c.model_dump() for c in commitments], repetition):
        existing.setdefault(r["commitment_id"], r)
    reminders = list(existing.values())
    store.save_reminders(date, reminders)
    return {"reminders": reminders, "repetition": repetition}


@app.get("/api/reminders/{date}")
def list_reminders(date: str):
    return get_store().get_reminders(date)


@app.post("/api/reminders/tick")
def tick(date: str = DEFAULT_DATE, now: str | None = None):
    """Fire due reminders. `now` simulates the clock (default: 19:00 on the day being replayed)."""
    try:
        clock = datetime.fromisoformat(now) if now else datetime.fromisoformat(f"{date}T19:00")
    except ValueError:
        raise HTTPException(400, "now must look like 2026-10-08T19:00")
    store = get_store()
    all_r = store.get_reminders(date)
    fired = [engine.fire(r, clock) for r in engine.due_reminders(all_r, clock)]
    if fired:
        store.save_reminders(date, all_r)
    return {"clock": clock.isoformat(timespec="minutes"),
            "fired": [{"commitment_id": f["reminder"]["commitment_id"], "message": f["message"],
                       "status": f["reminder"]["status"]} for f in fired]}


@app.post("/api/reminders/{date}/add")
def add_reminder(date: str, body: AddReminderRequest):
    store = get_store()
    all_r = store.get_reminders(date)
    new = engine.manual_reminder(date, body.action.strip())
    if not any(r["commitment_id"] == new["commitment_id"] for r in all_r):
        all_r.append(new)
        store.save_reminders(date, all_r)
    return new


@app.post("/api/reminders/{date}/{cid}/ack")
def ack(date: str, cid: str):
    store = get_store()
    all_r = store.get_reminders(date)
    for r in all_r:
        if r["commitment_id"] == cid:
            engine.acknowledge(r)
            store.save_reminders(date, all_r)
            return {"acknowledged": cid}
    raise HTTPException(404, "Reminder not found")


@app.post("/api/qa")
def qa(body: QARequest):
    question = body.question.strip()
    if not question:
        raise HTTPException(400, "question is required")
    return answer_question(_day(body.date or DEFAULT_DATE), question)


@app.post("/api/digest/{date}")
def make_digest(date: str):
    store = get_store()
    state = build_state_pack(_day(date), store.get_reminders(date))
    digest = write_digest(_day(date), state)
    store.save_digest_state(date, state, digest)
    return {"digest": digest}


@app.get("/api/digest/{date}")
def get_digest(date: str):
    _, digest = get_store().get_digest_state(date)
    if digest is None:
        raise HTTPException(404, "No digest yet")
    return {"digest": digest}


@app.get("/api/caregiver/{date}")
def caregiver_view(date: str):
    """Sarah's view: signals, never the raw transcript. Refreshes state from current reminders."""
    store = get_store()
    _, digest = store.get_digest_state(date)
    if digest is None:
        raise HTTPException(404, f"Run the digest first: POST /api/digest/{date}")
    state = build_state_pack(_day(date), store.get_reminders(date))
    return caregiver_pack(state, digest)


# AWS Lambda entrypoint (optional)
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:  # pragma: no cover
    handler = None

# LAST: serve the SPA at /
app.mount("/", StaticFiles(directory=str(BACKEND_DIR / "static"), html=True), name="static")
