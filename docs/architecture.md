# Architecture

```
Transcript source (simulator now, Bee/S3+Transcribe later)
        │  POST /api/ingest
        ▼
  Store (LocalStore JSON  |  AWSStore: DynamoDB + S3)
        │
        ├─► Commitment agent ──► Reminder engine (fire → escalate → ack)
        ├─► Repetition detector (deterministic) ──► boosts reminder priority
        ├─► Q&A agent (grounded, citation validated against transcript)
        └─► Digest agent (dignity audit) ──► Caregiver pack (signals, no raw transcript)
                         ▲
                  LLM: Amazon Bedrock (Claude)  |  offline mock (USE_MOCK_LLM=true)
```

Deterministic guards on top of the LLM: citation validation, forbidden-word audit on the digest,
confidence floor on commitments, rule-based repetition detection.
