"""Repetition detector: topics the user asks about more than once in a day."""
import logging
import re
from collections import Counter

log = logging.getLogger("echomind.repetition")

STOP = {"the", "a", "an", "my", "i", "to", "of", "and", "is", "it", "what", "did", "do", "say", "said",
        "about", "me", "was", "or", "how", "many", "you", "for", "on", "in", "have", "that", "this",
        "remind", "good", "morning", "today", "was", "were", "are", "does", "when", "who", "where"}

# Related words collapse into one topic so "pills" and "pharmacy" count as the same concern.
TOPIC_GROUPS = {
    "medication": {"pill", "pills", "medication", "medicine", "prescription", "pharmacy", "refill",
                   "dose", "dosage", "tablet", "tablets"},
    "doctor": {"doctor", "dr", "chen", "appointment", "clinic"},
}
_GROUPED = set().union(*TOPIC_GROUPS.values())


def keywords(text: str) -> set[str]:
    words = set(re.findall(r"[a-z']+", text.lower()))
    kws = {w for w in words - STOP if len(w) > 2 and w not in _GROUPED}
    for label, group in TOPIC_GROUPS.items():
        if words & group:
            kws.add(label)
    return kws


def detect_repetition(day: dict, min_repeats: int = 2) -> dict:
    user_lines = [s["text"] for s in day["segments"] if s["speaker"] == "user"]
    questions = [t for t in user_lines
                 if "?" in t or t.lower().startswith(("what", "how", "when", "remind"))]
    counter: Counter = Counter()
    for q in questions:
        counter.update(keywords(q))
    repeated = {w: c for w, c in counter.items() if c >= min_repeats}
    log.info("Repetition scan: %d questions, repeated: %s", len(questions), repeated)
    return {"repeated_topics": repeated, "flagged": bool(repeated)}
