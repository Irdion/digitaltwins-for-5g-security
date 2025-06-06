"""locustfile.py – workload generator for 5GC‑NRF Diff‑Dashboard evaluation

This version implements the **header‑flag approach**
----------------------------------------------------
A Locust user marks a request as "malicious" with probability ATTACK_RATE
and signals that intent to the proxy chain by adding an HTTP header

    X-Tamper: 1

* The body itself is **not** modified here – the Lua filter inside Envoy will
  read the header and mutate *only* the duplicate that goes to Free5GC.
* Ground‑truth labels are written to Redis so that the analysis_service can
  compute precision/recall later.

Environment variables
~~~~~~~~~~~~~~~~~~~~~
TARGET_HOST   – URL of injector‑svc   (default: http://injector:7100)
ATTACK_RATE   – float 0‑1, probability of tampering (default: 0.0)
REDIS_URL     – Redis connection string (default: redis://redis:6379/0)

Run example
~~~~~~~~~~~
locust -f locust/locustfile.py \
       --headless -u 100 -r 10 -t 2m \
       --env TARGET_HOST=http://injector:7100 ATTACK_RATE=0.1
"""

from locust import HttpUser, task, between
import os, json, random, uuid, time, redis

# ---------------------------------------------------------------------------
# Configuration via environment variables
# ---------------------------------------------------------------------------
TARGET_HOST  = os.getenv("TARGET_HOST", "http://injector:7100")
ATTACK_RATE  = float(os.getenv("ATTACK_RATE", "0.0"))
REDIS_URL    = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Redis connection (single global – fine for Locust workers)
r = redis.Redis.from_url(REDIS_URL)

# ---------------------------------------------------------------------------
# Helper: build minimal NF profile
# ---------------------------------------------------------------------------

def build_nf_profile(nf_id: str) -> dict:
    """Return a small but valid NRF registration body."""
    return {
        "nfInstanceId": nf_id,
        "nfType": "AMF",
        "nfStatus": "REGISTERED",
        "heartBeatTimer": 120,
        "ipv4Addresses": [f"198.51.100.{random.randint(1,254)}"],
    }

# ---------------------------------------------------------------------------
# Locust user
# ---------------------------------------------------------------------------

class NRFUser(HttpUser):
    host = TARGET_HOST          # Locust base URL
    wait_time = between(0.05, 0.25)

    @task(3)
    def register(self):
        # 1) generate NF profile
        nf_id = str(uuid.uuid4())
        profile = build_nf_profile(nf_id)

        # 2) decide whether this run should be tampered
        malicious = random.random() < ATTACK_RATE

        # 3) build headers (flag only, body unchanged)
        headers = {"Content-Type": "application/json"}
        if malicious:
            headers["X-Tamper"] = "1"

        # 4) send to injector-svc via JSON wrapper
        self.client.post(
            "/api/test",
            json={
                "method": "PUT",
                "path": f"/nnrf-nfm/v1/nf-instances/{nf_id}",
                "headers": headers,
                "body": json.dumps(profile),
            },
            name="/nnrf/register",
        )

        # 5) ground‑truth label in Redis (1 = tampered, 0 = benign)
        r.hset("truth", nf_id, int(malicious))
        r.hset("truth_ts", nf_id, time.time())
