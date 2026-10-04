"""Reminder engine: stateful reminders with fire / escalate / acknowledge."""
import hashlib
import logging
from datetime import datetime

from agents.repetition_agent import keywords

log = logging.getLogger("echomind.engine")

NUDGES = [
    "Gentle reminder: {action}",
    "Still pending: {action}. Want help with it?",
    "This seems important to you. {action}. Should I let Sarah know?",
]


def _parse(ts: str | None) -> datetime | None:
    if not ts or ts == "none":
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return None


def _get(c, key):
    return c[key] if isinstance(c, dict) else getattr(c, key)


def create_reminders(commitments: list, repetition: dict) -> list:
    boost_words = set(repetition.get("repeated_topics", {}))
    reminders = []
    for c in commitments:
        r = {"commitment_id": _get(c, "commitment_id"), "date": _get(c, "date"),
             "action": _get(c, "action"), "deadline": _get(c, "deadline"),
             "priority": 2, "fire_count": 0, "max_fires": 3, "last_fired_at": None,
             "status": "scheduled", "escalation_level": 0}
        overlap = boost_words & keywords(r["action"])
        if overlap:
            r["priority"], r["max_fires"] = 1, 5
            log.info("BOOSTED reminder '%s' (matched: %s)", r["action"], overlap)
        reminders.append(r)
    return reminders


def manual_reminder(date: str, action: str) -> dict:
    cid = "m" + hashlib.sha1(f"{date}|{action.lower()}".encode()).hexdigest()[:7]
    return {"commitment_id": cid, "date": date, "action": action, "deadline": None, "priority": 2,
            "fire_count": 0, "max_fires": 3, "last_fired_at": None, "status": "scheduled",
            "escalation_level": 0}


def due_reminders(reminders: list, now: datetime | None = None) -> list:
    now = now or datetime.now()
    due = []
    for r in reminders:
        if r["status"] in ("acknowledged", "escalated") or r["fire_count"] >= r["max_fires"]:
            continue
        dl = _parse(r.get("deadline"))
        if dl is None or dl <= now:
            due.append(r)
    return due


def fire(r: dict, now: datetime | None = None) -> dict:
    now = now or datetime.now()
    r["fire_count"] += 1
    r["last_fired_at"] = now.strftime("%Y-%m-%dT%H:%M")
    r["status"] = "fired"
    if r["fire_count"] >= 2:
        r["escalation_level"] = 1 if r["priority"] == 2 else 2
        if r["escalation_level"] >= 2:
            r["status"] = "escalated"
    msg = NUDGES[min(r["fire_count"] - 1, len(NUDGES) - 1)].format(action=r["action"])
    if r["escalation_level"] == 1:
        msg += " (Family will be told if this stays open.)"
    elif r["escalation_level"] == 2:
        msg = f"⚠️ {r['action']}: this has come up before. Letting Sarah know now."
    log.info("FIRED #%d [%s] %s", r["fire_count"], r["status"], msg)
    return {"reminder": r, "message": msg}


def acknowledge(r: dict) -> dict:
    r["status"] = "acknowledged"
    return r
