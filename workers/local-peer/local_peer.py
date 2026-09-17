import hashlib
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path

ROOT = Path(os.getenv("LOCAL_PEER_HOME", "./.local-peer"))
ROOT.mkdir(parents=True, exist_ok=True)
DB = ROOT / "peer.db"
SCHEMA = Path(__file__).with_name("schema.sql")

TERMINAL = {"REJECTED", "GAUNTLET_FAILED", "AVAILABLE", "ALLOCATED", "USED"}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.executescript(SCHEMA.read_text(encoding="utf-8"))
    return c


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def enqueue(job_id, capability_id, request):
    with connect() as c:
        t = now()
        c.execute("INSERT OR IGNORE INTO jobs(job_id,capability_id,state,request_json,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                  (job_id, capability_id, "PENDING", json.dumps(request, sort_keys=True), t, t))
        c.execute("INSERT OR IGNORE INTO reconciliation_log(operation_id,entity_type,entity_id,operation,payload_json,payload_sha256,created_at) VALUES(?,?,?,?,?,?,?)",
                  (str(uuid.uuid4()), "job", job_id, "UPSERT", json.dumps(request, sort_keys=True), digest(request), t))


def admit(job_id):
    with connect() as c:
        row = c.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row or row["state"] != "PENDING":
            return False
        cap = c.execute("SELECT * FROM capabilities WHERE capability_id=?", (row["capability_id"],)).fetchone()
        if not cap or cap["state"] != "AVAILABLE":
            c.execute("UPDATE jobs SET state='REJECTED',updated_at=? WHERE job_id=?", (now(), job_id))
            return False
        c.execute("UPDATE jobs SET state='ADMITTED',updated_at=? WHERE job_id=?", (now(), job_id))
        return True


def record_result(job_id, result):
    """Record semantic output only. This function deliberately cannot create VERIFIED economic state."""
    with connect() as c:
        row = c.execute("SELECT state FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row or row["state"] not in {"ADMITTED", "RUNNING"}:
            return False
        t = now()
        c.execute("UPDATE jobs SET state='TESTED',result_json=?,updated_at=? WHERE job_id=?",
                  (json.dumps(result, sort_keys=True), t, job_id))
        receipt = {
            "job_id": job_id,
            "type": "LOCAL_RESULT",
            "verification_state": "UNVERIFIED",
            "economic_truth": "NOT_ESTABLISHED",
            "result": result,
        }
        rid = str(uuid.uuid4())
        c.execute("INSERT INTO evidence_receipts(receipt_id,job_id,verification_state,receipt_json,created_at) VALUES(?,?,?,?,?)",
                  (rid, job_id, "UNVERIFIED", json.dumps(receipt, sort_keys=True), t))
        c.execute("INSERT INTO reconciliation_log(operation_id,entity_type,entity_id,operation,payload_json,payload_sha256,created_at) VALUES(?,?,?,?,?,?,?)",
                  (str(uuid.uuid4()), "job", job_id, "RESULT", json.dumps(receipt, sort_keys=True), digest(receipt), t))
        return True


def pending_reconciliation(limit=100):
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM reconciliation_log WHERE status='PENDING' ORDER BY created_at LIMIT ?", (limit,))]


if __name__ == "__main__":
    print(json.dumps({"status": "READY", "db": str(DB), "offline_capable": True}))
