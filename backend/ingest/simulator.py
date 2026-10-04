import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "simulated_day.json"


def load_simulated_day(date: str | None = None) -> dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        day = json.load(f)
    if date:
        day["date"] = date
    return day


def transcript_as_text(day: dict) -> str:
    return "\n".join(f"[{s['time']}] {s['speaker']}: {s['text']}" for s in day["segments"])
