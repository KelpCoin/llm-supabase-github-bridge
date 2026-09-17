import json
import os
import time
import urllib.error
import urllib.request

WORKER_ID = os.getenv("WORKER_ID", "bec-local-gpu-worker")
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
LM_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
LM_MODEL = os.getenv("LM_STUDIO_MODEL", "")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "5"))
LEASE_SECONDS = int(os.getenv("LEASE_SECONDS", "300"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_SECRET_KEY or SUPABASE_SERVICE_ROLE_KEY is required")


def http_json(url, method="GET", body=None, headers=None, timeout=60):
    payload = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else None


def supabase_rpc(name, args):
    return http_json(
        f"{SUPABASE_URL}/rest/v1/rpc/{name}",
        method="POST",
        body=args,
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        timeout=60,
    )


def choose_model():
    if LM_MODEL:
        return LM_MODEL
    data = http_json(f"{LM_BASE_URL}/models", timeout=20)
    models = data.get("data", []) if isinstance(data, dict) else []
    if not models:
        raise RuntimeError("LM Studio returned no models")
    return models[0]["id"]


def run_model(note, model):
    body = note.get("body") or ""
    system = (
        "You are the local semantic worker for BrownEye Cortex. "
        "Process only the supplied task. Return valid JSON. "
        "Never claim that money was paid, a buyer was acquired, a deployment happened, "
        "a message was sent, or a file was changed unless the supplied evidence explicitly proves it. "
        "Do not perform or propose irreversible external actions. "
        "If the task is ambiguous, return decision=UNKNOWN and explain the missing evidence."
    )
    user = {
        "worker_id": WORKER_ID,
        "note_id": note.get("note_id"),
        "subject": note.get("subject"),
        "note_type": note.get("note_type"),
        "correlation_id": note.get("correlation_id"),
        "lane": note.get("lane"),
        "silo_id": note.get("silo_id"),
        "body": body,
        "required_output": {
            "decision": "PROMOTE|MODIFY|KILL|UNKNOWN|COMPLETE",
            "confidence": "0..1",
            "evidence": "object",
            "reason": "string",
            "next_action": "string or null",
            "approval_required": "boolean",
        },
    }
    response = http_json(
        f"{LM_BASE_URL}/chat/completions",
        method="POST",
        body={
            "model": model,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user, ensure_ascii=True)},
            ],
        },
        headers={"Authorization": "Bearer lm-studio"},
        timeout=180,
    )
    content = response["choices"][0]["message"]["content"]
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"decision": "UNKNOWN", "confidence": 0, "evidence": {}, "reason": "Model did not return valid JSON", "raw": content}
    result["worker_id"] = WORKER_ID
    result["model"] = model
    result["external_action_taken"] = False
    result["revenue_claimed"] = False
    return result


def claim_one():
    rows = supabase_rpc(
        "claim_local_gpu_bridge_note",
        {"p_worker_id": WORKER_ID, "p_lease_seconds": LEASE_SECONDS},
    )
    if isinstance(rows, list) and rows:
        return rows[0]
    return None


def complete(note, result):
    try:
        source = json.loads(note.get("body") or "{}")
    except json.JSONDecodeError:
        source = {}
    result["source_job_id"] = source.get("source_job_id") or source.get("job_id")
    if source.get("cell_id"):
        result["cell_id"] = source["cell_id"]
    result["next_experiment"] = result.get("next_action")
    payload = json.dumps(
        {
            "schema_version": "BECK-LOCAL-GPU-RESULT-1.0",
            "source_job_id": result.get("source_job_id"),
            "cell_id": result.get("cell_id"),
            "note_id": note["note_id"],
            "worker_id": WORKER_ID,
            "result": result,
            "completed_at": time.time(),
        },
        ensure_ascii=True,
    )
    correlation = note.get("correlation_id") or note["note_id"]
    return supabase_rpc(
        "complete_control_bridge_note",
        {
            "p_note_id": note["note_id"],
            "p_worker_id": WORKER_ID,
            "p_response_body": payload,
            "p_response_subject": "BRIDGE_STAGE:" + str(correlation) + ":WORKER_A_RESULT",
            "p_response_note_type": "FINDING",
            "p_from_agent": WORKER_ID,
        },
    )


def main():
    model = choose_model()
    print(json.dumps({"status": "READY", "worker": WORKER_ID, "model": model}, ensure_ascii=True), flush=True)
    while True:
        try:
            note = claim_one()
            if not note:
                time.sleep(POLL_SECONDS)
                continue
            try:
                result = run_model(note, model)
                complete(note, result)
                print(json.dumps({"status": "COMPLETED", "note_id": note["note_id"]}, ensure_ascii=True), flush=True)
            except Exception as exc:
                print(json.dumps({"status": "WORK_FAILED", "note_id": note.get("note_id"), "error": str(exc)}, ensure_ascii=True), flush=True)
                time.sleep(POLL_SECONDS)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(json.dumps({"status": "BRIDGE_UNAVAILABLE", "error": str(exc)}, ensure_ascii=True), flush=True)
            time.sleep(max(POLL_SECONDS, 10))


if __name__ == "__main__":
    main()
