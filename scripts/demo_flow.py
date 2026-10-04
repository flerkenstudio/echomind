"""Runs the whole pitch flow against a running server. Usage: python scripts/demo_flow.py [base_url]"""
import json
import sys

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
D = "2026-10-08"
c = httpx.Client(base_url=BASE, timeout=120)


def show(title, resp):
    print(f"\n=== {title} ===")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


show("health", c.get("/api/health"))
show("ingest", c.post("/api/ingest"))
built = c.post("/api/reminders/build")
show("build reminders (pharmacy should be priority 1)", built)
cid = built.json()["reminders"][0]["commitment_id"]
show("tick #1 (gentle)", c.post("/api/reminders/tick"))
show("tick #2 (escalated)", c.post("/api/reminders/tick"))
for q in ["what did the doctor say about my pills?", "when is my niece's wedding?",
          "can I take ibuprofen with my pills?"]:
    show(f"Q&A: {q}", c.post("/api/qa", json={"question": q}))
show("digest", c.post(f"/api/digest/{D}"))
show("caregiver view", c.get(f"/api/caregiver/{D}"))
show("acknowledge", c.post(f"/api/reminders/{D}/{cid}/ack"))
