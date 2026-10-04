from fastapi.testclient import TestClient

from main import app

D = "2026-10-08"


def test_full_flow():
    with TestClient(app) as c:
        assert c.get("/api/health").json()["status"] == "ok"
        assert c.get("/api/day").json()["user"] == "Martha"
        assert c.post("/api/ingest").json()["segments"] == 7
        assert c.get(f"/api/record/{D}").status_code == 200
        assert c.get("/api/record/1999-01-01").status_code == 404

        built = c.post("/api/reminders/build").json()
        assert built["reminders"][0]["priority"] == 1
        cid = built["reminders"][0]["commitment_id"]
        assert len(c.post("/api/reminders/build").json()["reminders"]) == 1   # idempotent

        t1 = c.post("/api/reminders/tick").json()["fired"]
        assert t1 and "Gentle" in t1[0]["message"]
        t2 = c.post("/api/reminders/tick").json()["fired"]
        assert "Letting Sarah know" in t2[0]["message"]

        assert c.post("/api/qa", json={"question": "what did the doctor say about my pills?"}).json()["citation"] == "09:30"
        assert c.post("/api/qa", json={"question": " "}).status_code == 400
        added = c.post(f"/api/reminders/{D}/add", json={"action": "Ask about niece's wedding"}).json()
        assert added["commitment_id"].startswith("m")

        assert c.get(f"/api/caregiver/{D}").status_code == 404
        assert "digest" in c.post(f"/api/digest/{D}").json()
        cg = c.get(f"/api/caregiver/{D}").json()
        assert "segments" not in cg and cg["repeated_topics"]["medication"] == 2

        assert c.post(f"/api/reminders/{D}/{cid}/ack").json()["acknowledged"] == cid
        assert c.post(f"/api/reminders/{D}/nope/ack").status_code == 404
        assert c.get("/").status_code == 200   # SPA served
