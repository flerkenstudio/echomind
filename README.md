# 🐝 EchoMind — Memory that listens

A companion for people with early memory decline. **Martha gets memories. Sarah gets signals.**

EchoMind is a two-part system designed to support memory care. It discreetly processes daily conversations to provide gentle reminders and answers for the patient, while generating insightful digests for caregivers without exposing raw private transcripts.

## 🌟 Key Features
- **Commitment Agent**: Detects promises ("I'll call the pharmacy this afternoon") and turns them into actionable reminders.
- **Repetition Detector**: Identifies topics asked about repeatedly (e.g., pills, doctor appointments) and boosts reminder priorities.
- **Q&A Agent**: Answers patient questions based strictly on the day's transcript, validating responses with timestamp citations and refusing gracefully when unsure.
- **Digest Agent**: Generates a warm, end-of-day summary with a dignity audit (never uses words like "forgot", "failed", or "missed").
- **Caregiver View**: Highlights patterns and pending items for caregivers, ensuring privacy by never exposing the raw transcript.

## 🏗️ Architecture
```text
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
Deterministic guards are placed on top of the LLM: citation validation, forbidden-word audit on the digest, confidence floor on commitments, and rule-based repetition detection.

## 🚀 Getting Started

The project consists of a Python backend (FastAPI) and a React frontend (Vite).

### Backend Setup (No AWS needed)
Requires **Python 3.10+**.

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
uvicorn main:app --reload
```
The backend will run on `http://localhost:8000`. The default `.env` uses `USE_MOCK_LLM=true` and `USE_LOCAL_STORE=true`, meaning everything runs offline. Data is saved in the `local_data/` folder.

### Frontend Setup
Requires **Node.js 18+**.

```bash
cd frontend
npm install
npm run dev
```
The frontend will run on `http://localhost:5173`. Open this URL in your browser to interact with the UI.

### Demo Flow
With both servers running, you can simulate a day's worth of data:
```bash
python scripts/demo_flow.py
```
**What to try in the UI:** 
- **Home**: View digests and pharmacy reminders. Acknowledge reminders, or simulate checking in to see escalation.
- **Ask**: Ask questions like "what did the doctor say about my pills?" or "when is my niece's wedding?"
- **Family**: View caregiver signals and insights.

## ☁️ Advanced Setup

### Using Real Amazon Bedrock
1. Go to AWS Console → Bedrock → **Model access** and enable a Claude model in your region.
2. Ensure your AWS credentials are configured (`aws configure`).
3. In `backend/.env`, set `USE_MOCK_LLM=false` and `BEDROCK_MODEL_ID` to your enabled model ID.
4. Restart the backend; the terminal should print `LLM (bedrock) health: ✅ OK`.

### Using DynamoDB + S3 (Optional)
If you wish to use AWS storage instead of local JSON files:
```bash
aws dynamodb create-table --table-name echomind-days --attribute-definitions AttributeName=date,AttributeType=S --key-schema AttributeName=date,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1
aws dynamodb create-table --table-name echomind-digests --attribute-definitions AttributeName=date,AttributeType=S --key-schema AttributeName=date,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-east-1
for t in commitments reminders; do aws dynamodb create-table --table-name echomind-$t --attribute-definitions AttributeName=date,AttributeType=S AttributeName=commitment_id,AttributeType=S --key-schema AttributeName=date,KeyType=HASH AttributeName=commitment_id,KeyType=RANGE --billing-mode PAY_PER_REQUEST --region us-east-1; done
```
Set `USE_LOCAL_STORE=false` in your `.env`.

## 🧪 Testing
```bash
cd backend 
python -m pytest tests -v
```

## 📁 Project Structure
- `backend/` - FastAPI server, AI agents, data models, and AWS integrations.
- `frontend/` - React frontend built with Vite.
- `data/` - Simulated interaction data for testing.
- `docs/` - Architecture and planning documentation.
- `scripts/` - Utilities and demonstration scripts.

## ⚠️ Notes & Limitations
- The **mock LLM** is a tiny rule-based stub that only understands the simulated day. For real usage and high quality, Amazon Bedrock (Claude) is required.
- `template.yaml` and `lambdas/transcribe.py` (SAM deploy, S3→Transcribe) are untested against real AWS.
- This is a hackathon prototype, not a medical device. It should never be used to provide medical advice.
