"""Deterministic stand-in for Bedrock so the whole app runs offline.

It only understands the simulated day well enough to demo/test the pipeline.
Real behaviour comes from Bedrock: set USE_MOCK_LLM=false.
"""
import json
import re

SPEAKERS = {"doctor_chen": "Dr. Chen", "daughter_sarah": "Sarah", "user": "you"}
GENERIC = {"the", "a", "an", "my", "i", "to", "of", "and", "is", "it", "what", "did", "do", "say",
           "said", "about", "me", "was", "or", "how", "many", "you", "for", "on", "in", "have",
           "that", "this", "when", "who", "where", "does", "can", "with", "are", "from", "then"}
MEDICAL_ADVICE = ("can i take", "safe to", "ibuprofen", "interact", "mix ", "together with")
LINE = re.compile(r"^\[(\d\d:\d\d)\] (\w+): (.*)$", re.M)


def respond(prompt: str, system: str) -> str:
    s = system.lower()
    if "extract commitments" in s:
        return _commitments(prompt)
    if "answer an elderly person" in s:
        return _qa(prompt)
    if "end-of-day digest" in s:
        return _digest()
    return "OK"


def _commitments(prompt: str) -> str:
    items = []
    pat = re.compile(r"\b(?:i'll|i will|i need to remember to|remind me to)\s+(.*)", re.I)
    for _, speaker, text in LINE.findall(prompt):
        if speaker != "user" or "?" in text:
            continue
        m = pat.search(text)
        if not m:
            continue
        action = re.sub(r"\b(this afternoon|this evening|tonight|today|tomorrow)\b", "", m.group(1), flags=re.I)
        action = re.sub(r"\s+", " ", action).strip(" .")
        deadline = "TODAY+1" if "tomorrow" in text.lower() else "TODAY"
        items.append({"raw_text": text, "action": action, "deadline": deadline,
                      "deadline_type": "relative", "confidence": 0.9})
    return json.dumps(items)


def _qa(prompt: str) -> str:
    question = prompt.split("Question:", 1)[-1].strip().lower()
    nf = {"answer": "That didn't come up today.", "citation": None, "offer_reminder": True,
          "offer_text": re.sub(r"[?.]", "", question)[:60] + " to ask family"}
    if any(t in question for t in MEDICAL_ADVICE):
        return json.dumps(nf)
    qwords = {w for w in re.findall(r"[a-z']+", question) if w not in GENERIC and len(w) > 2}
    best, best_score = None, 0
    for time, speaker, text in LINE.findall(prompt):
        if speaker == "user":
            continue
        score = len(qwords & set(re.findall(r"[a-z']+", text.lower())))
        if score > best_score:
            best, best_score = (time, speaker, text), score
    if best is None:
        return json.dumps(nf)
    time, speaker, text = best
    return json.dumps({"answer": f"At {time}, {SPEAKERS.get(speaker, speaker)} said: {text}",
                       "citation": time, "offer_reminder": False, "offer_text": None})


def _digest() -> str:
    return ("What a full day, Martha. Sarah called to check on you this afternoon, and that is a lovely "
            "thing to hold onto. Your pills question came up a couple of times today: Dr. Chen said at "
            "9:30 it is two pills daily, with food. The pharmacy call hasn't happened yet. "
            "Want me to remind you first thing in the morning?")
