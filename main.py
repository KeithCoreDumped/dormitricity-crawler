import os, time, sys, base64, json
from api_client import claim, ingest
from util import dorm_info
from legacy_backend import legacy_backend
from new_backend import new_backend

JOB_ID = os.environ.get("JOB_ID", "test_job_id")
TOKEN  = os.environ.get("TOKEN", "test_token")

def process_slice(idx: int, targets: list[dict], params: dict):
    """
    targets: [{"hashed_dir": "...", "canonical_id": "..."}]
    """
    results, fails = [], []
    lb = legacy_backend(cookies=params["cookies"])
    with new_backend(params["url"], True) as nb:
        def one_target(t):
            dorm = dorm_info(t["canonical_id"])
            if dorm.is_new_backend():
                kwh, ts = nb.query(dorm)
            else:
                kwh, ts = lb.query(dorm)
            return {
                "hashed_dir": t["hashed_dir"],
                "ts": int(ts.timestamp()), # in seconds
                "kwh": kwh,
                "ok": True
            }

        results = []
        fails = []

        for t in targets:
            try:
                results.append(one_target(t))
            except Exception as e:
                fails.append({"hashed_dir": t["hashed_dir"], "reason": str(e)})

    payload = {
        "job_id": JOB_ID, "slice_index": idx,
        "idempotency_key": f"{JOB_ID}:{idx}:{int(time.time())}",
        "readings": results, "failures": fails, "finished": True
    }
    ingest(payload, TOKEN)
    print(f"processed slice {idx}. {len(results)} succeeded, {len(fails)} failed, {len(targets)} in total")

def main(params: dict):
    while True:
        got = claim(JOB_ID, TOKEN)
        if not got:
            print("no more slices")
            break
        idx = got["slice_index"]
        targets = got["targets"]  # object array
        print(f"claimed slice {idx} ({len(targets)} targets)")
        process_slice(idx, targets, params)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        from secret import new_backend_url as url
        from secret import legacy_backend_cookies as cookies
        print("running local test")
        params = {
            "url": url,
            "cookies": cookies
        }
    else:
        params = json.loads(base64.b64decode(sys.argv[1]))
        
    main(params)
