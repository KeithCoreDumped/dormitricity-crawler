import os, json, requests

BASE = os.environ.get("WORKERS_BASE", "https://example.com")

def claim(job_id: str, token: str):
    r = requests.post(f"{BASE}/orchestrator/claim",
        headers={"Authorization": f"Bearer {token}", "Content-Type":"application/json"},
        data=json.dumps({"job_id": job_id})
    )
    if r.status_code == 204: return None
    r.raise_for_status()
    return r.json()

def ingest(payload: dict, token: str):
    r = requests.post(f"{BASE}/ingest",
        headers={"Authorization": f"Bearer {token}", "Content-Type":"application/json"},
        data=json.dumps(payload)
    )
    r.raise_for_status()
