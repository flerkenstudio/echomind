"""S3-triggered: audio lands in audio/<date>/<file> -> Transcribe -> day JSON in DynamoDB.

UNTESTED against real AWS. Transcribe output goes under transcripts-out/ (NOT audio/) so the
output file can't re-trigger this function.
"""
import json
import os
import time
import uuid

import boto3

s3 = boto3.client("s3")
transcribe = boto3.client("transcribe")
table = boto3.resource("dynamodb").Table(os.environ["DDB_DAYS"])


def _to_day(date: str, data: dict) -> dict:
    items = data["results"]["items"]
    labels = data["results"].get("speaker_labels", {}).get("segments", [])
    segments = []
    for seg in labels:
        words = [i["alternatives"][0]["content"] for i in items
                 if i["type"] == "pronunciation" and seg["start_time"] <= i["start_time"] <= seg["end_time"]]
        if words:
            secs = int(float(seg["start_time"]))
            segments.append({"time": f"{secs // 3600:02d}:{secs % 3600 // 60:02d}",
                             "speaker": "user" if seg["speaker_label"] == "spk_0" else seg["speaker_label"],
                             "text": " ".join(words), "location": "unknown", "tags": []})
    if not segments:
        segments = [{"time": "00:00", "speaker": "user",
                     "text": data["results"]["transcripts"][0]["transcript"], "location": "unknown", "tags": []}]
    return {"date": date, "user": "Martha", "segments": segments}


def handler(event, _):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]      # audio/2026-10-08/day.wav
    date = key.split("/")[1]
    job = f"echomind-{date}-{uuid.uuid4().hex[:8]}"
    transcribe.start_transcription_job(
        TranscriptionJobName=job, Media={"MediaFileUri": f"s3://{bucket}/{key}"},
        OutputBucketName=bucket, OutputKey=f"transcripts-out/{job}.json", LanguageCode="en-US",
        Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": 4})
    for _ in range(50):
        st = transcribe.get_transcription_job(TranscriptionJobName=job)["TranscriptionJob"]
        if st["TranscriptionJobStatus"] == "COMPLETED":
            data = json.loads(s3.get_object(Bucket=bucket, Key=f"transcripts-out/{job}.json")["Body"].read())
            day = _to_day(date, data)
            table.put_item(Item={"date": date, "user": day["user"], "segment_count": len(day["segments"]), "day": day})
            return {"ok": True, "date": date}
        if st["TranscriptionJobStatus"] == "FAILED":
            raise RuntimeError(st.get("FailureReason", "transcription failed"))
        time.sleep(5)
    raise TimeoutError("transcription timed out")
