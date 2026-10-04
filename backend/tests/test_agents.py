import re

from agents.commitment_agent import _resolve_deadline, extract_commitments
from agents.digest_agent import FORBIDDEN, build_state_pack, write_digest
from agents.qa_agent import answer_question
from agents.repetition_agent import detect_repetition
from ingest.simulator import load_simulated_day
from reminders import engine

DAY = load_simulated_day()


def test_repetition_flags_medication_and_doctor():
    rep = detect_repetition(DAY)
    assert rep["flagged"] and rep["repeated_topics"]["medication"] == 2


def test_commitment_extraction_ignores_worry():
    cs = extract_commitments(DAY)
    assert len(cs) == 1
    assert cs[0].action == "call the pharmacy to order the refill"
    assert cs[0].deadline == "2026-10-08" and cs[0].source_time == "10:05"


def test_commitment_id_is_stable():
    assert extract_commitments(DAY)[0].commitment_id == extract_commitments(DAY)[0].commitment_id


def test_deadline_resolution():
    assert _resolve_deadline("TODAY", "relative", "2026-10-08") == "2026-10-08"
    assert _resolve_deadline("TODAY+1", "relative", "2026-10-08") == "2026-10-09"
    assert _resolve_deadline(None, "none", "2026-10-08") is None


def test_repetition_boosts_pharmacy_reminder_and_escalates():
    cs = [c.model_dump() for c in extract_commitments(DAY)]
    r = engine.create_reminders(cs, detect_repetition(DAY))[0]
    assert r["priority"] == 1
    from datetime import datetime
    now = datetime.fromisoformat("2026-10-08T19:00")
    assert "Gentle" in engine.fire(r, now)["message"]
    assert "Letting Sarah know" in engine.fire(r, now)["message"]
    assert r["status"] == "escalated" and engine.due_reminders([r], now) == []


def test_qa_grounded_refusal_and_medical_boundary():
    a = answer_question(DAY, "what did the doctor say about my pills?")
    assert a["citation"] == "09:30"
    b = answer_question(DAY, "when is my niece's wedding?")
    assert b["citation"] is None and b["offer_reminder"]
    c = answer_question(DAY, "can I take ibuprofen with my pills?")
    assert c["citation"] is None


def test_digest_dignity():
    reminders = engine.create_reminders([c.model_dump() for c in extract_commitments(DAY)], detect_repetition(DAY))
    assert not FORBIDDEN.search(write_digest(DAY, build_state_pack(DAY, reminders)))
