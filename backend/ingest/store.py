"""Persistence layer: DynamoDB + S3 (AWSStore) or JSON files (LocalStore)."""
import json
import logging
import os
from abc import ABC, abstractmethod
from decimal import Decimal
from pathlib import Path

import config  # noqa: F401  (loads .env)
from config import ROOT_DIR, env_bool

log = logging.getLogger("echomind.store")


class StoreError(Exception):
    pass


def _clean(o):
    """DynamoDB returns Decimal; convert so JSON/engine code works normally."""
    if isinstance(o, Decimal):
        return int(o) if o == o.to_integral_value() else float(o)
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(v) for v in o]
    return o


class BaseStore(ABC):
    @abstractmethod
    def store_day(self, day: dict) -> str: ...
    @abstractmethod
    def get_day_record(self, date: str) -> dict | None: ...
    @abstractmethod
    def save_commitments(self, date: str, commitments: list) -> int: ...
    @abstractmethod
    def get_commitments(self, date: str, status: str | None = None) -> list: ...
    @abstractmethod
    def save_reminders(self, date: str, reminders: list) -> int: ...
    @abstractmethod
    def get_reminders(self, date: str) -> list: ...
    @abstractmethod
    def save_digest_state(self, date: str, state: dict, digest: str) -> None: ...
    @abstractmethod
    def get_digest_state(self, date: str) -> tuple: ...

    @property
    def kind(self) -> str:
        return type(self).__name__


def _record(day: dict) -> dict:
    return {"date": day["date"], "user": day.get("user", "unknown"),
            "segment_count": len(day.get("segments", [])), "day": day}


# ---------------- AWS ----------------
class AWSStore(BaseStore):
    def __init__(self):
        import boto3
        region = os.getenv("AWS_REGION", "us-east-1")
        ddb = boto3.resource("dynamodb", region_name=region)
        self.table = ddb.Table(os.getenv("DDB_TABLE", "echomind-days"))
        self.ctable = ddb.Table(os.getenv("DDB_COMMITMENTS", "echomind-commitments"))
        self.rtable = ddb.Table(os.getenv("DDB_REMINDERS", "echomind-reminders"))
        self.dtable = ddb.Table(os.getenv("DDB_DIGESTS", "echomind-digests"))
        self.s3 = boto3.client("s3", region_name=region)
        self.bucket = os.getenv("S3_BUCKET", "")

    def store_day(self, day):
        from botocore.exceptions import ClientError
        date = day["date"]
        if self.bucket:
            try:
                self.s3.put_object(Bucket=self.bucket, Key=f"transcripts/{date}.json",
                                   Body=json.dumps(day, indent=2).encode(), ContentType="application/json")
            except ClientError as e:
                raise StoreError(f"S3 upload failed: {e}") from e
        try:
            self.table.put_item(Item={"date": date, "user": day.get("user", "unknown"),
                                      "segment_count": len(day.get("segments", [])), "day": day})
        except ClientError as e:
            raise StoreError(f"DynamoDB write failed: {e}") from e
        return date

    def get_day_record(self, date):
        item = self.table.get_item(Key={"date": date}).get("Item")
        if not item or "day" not in item:
            return None
        return _clean({"date": item["date"], "user": item.get("user", "unknown"),
                       "segment_count": item.get("segment_count", 0), "day": item["day"]})

    def save_commitments(self, date, commitments):
        with self.ctable.batch_writer() as bw:
            for c in commitments:
                d = c.model_dump()
                d["confidence"] = Decimal(str(d["confidence"]))
                d["deadline"] = d["deadline"] or "none"
                bw.put_item(Item=d)
        return len(commitments)

    def get_commitments(self, date, status=None):
        from boto3.dynamodb.conditions import Attr, Key
        kw = {"KeyConditionExpression": Key("date").eq(date)}
        if status:
            kw["FilterExpression"] = Attr("status").eq(status)
        return _clean(self.ctable.query(**kw).get("Items", []))

    def save_reminders(self, date, reminders):
        with self.rtable.batch_writer() as bw:
            for r in reminders:
                bw.put_item(Item={k: v for k, v in r.items()})
        return len(reminders)

    def get_reminders(self, date):
        from boto3.dynamodb.conditions import Key
        return _clean(self.rtable.query(KeyConditionExpression=Key("date").eq(date)).get("Items", []))

    def save_digest_state(self, date, state, digest):
        self.dtable.put_item(Item={"date": date, "payload": json.dumps({"state": state, "digest": digest})})

    def get_digest_state(self, date):
        item = self.dtable.get_item(Key={"date": date}).get("Item")
        if not item:
            return None, None
        d = json.loads(item["payload"])
        return d["state"], d["digest"]


# ---------------- Local ----------------
class LocalStore(BaseStore):
    def __init__(self):
        self.dir = Path(os.getenv("LOCAL_DATA_DIR") or ROOT_DIR / "local_data")
        self.dir.mkdir(parents=True, exist_ok=True)

    def _p(self, prefix: str, date: str) -> Path:
        return self.dir / f"{prefix}_{date}.json"

    def _read(self, prefix, date, default):
        p = self._p(prefix, date)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

    def _write(self, prefix, date, data):
        self._p(prefix, date).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def store_day(self, day):
        self._write("day", day["date"], day)
        return day["date"]

    def get_day_record(self, date):
        day = self._read("day", date, None)
        return _record(day) if day else None

    def save_commitments(self, date, commitments):
        self._write("commitments", date, [c.model_dump() for c in commitments])
        return len(commitments)

    def get_commitments(self, date, status=None):
        return [i for i in self._read("commitments", date, []) if not status or i["status"] == status]

    def save_reminders(self, date, reminders):
        self._write("reminders", date, reminders)
        return len(reminders)

    def get_reminders(self, date):
        return self._read("reminders", date, [])

    def save_digest_state(self, date, state, digest):
        self._write("digest", date, {"state": state, "digest": digest})

    def get_digest_state(self, date):
        d = self._read("digest", date, None)
        return (d["state"], d["digest"]) if d else (None, None)


def get_store() -> BaseStore:
    if env_bool("USE_LOCAL_STORE", True):
        return LocalStore()
    try:
        s = AWSStore()
        s.table.table_status  # fails fast if table/creds missing
        return s
    except Exception as e:  # noqa: BLE001
        log.warning("AWSStore unavailable (%s) - falling back to LocalStore", e)
        return LocalStore()
