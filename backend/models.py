from pydantic import BaseModel, Field


class Commitment(BaseModel):
    commitment_id: str
    date: str
    source_time: str = ""
    speaker: str = "user"
    raw_text: str
    action: str
    deadline: str | None = None
    deadline_type: str = "none"     # explicit | relative | vague | none
    confidence: float = Field(ge=0.0, le=1.0)
    status: str = "pending"         # pending | fired | done


class Reminder(BaseModel):
    commitment_id: str
    date: str
    action: str
    deadline: str | None = None
    priority: int = 2               # 1 = repetition-boosted, 2 = normal
    fire_count: int = 0
    max_fires: int = 3
    last_fired_at: str | None = None
    status: str = "scheduled"       # scheduled | fired | acknowledged | escalated
    escalation_level: int = 0       # 0 gentle, 1 family warning, 2 notify family


class QARequest(BaseModel):
    question: str
    date: str | None = None


class AddReminderRequest(BaseModel):
    action: str
