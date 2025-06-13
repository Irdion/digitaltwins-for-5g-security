from locust import HttpUser, task, between
import os, json, random, uuid, time, redis


TARGET_HOST  = os.getenv("TARGET_HOST", "http://injector:7100")
ATTACK_RATE  = float(os.getenv("ATTACK_RATE", "0.25"))
REDIS_URL    = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Shared Redis connection for ground-truth labels
r = redis.Redis.from_url(REDIS_URL)

def build_nf_profile(nf_id: str) -> dict:
    """Return a small but valid NRF registration body."""
    return {
        "nfInstanceId": nf_id,
        "nfType": "AMF",
        "nfStatus": "REGISTERED",
        "heartBeatTimer": 120,
        "ipv4Addresses": [f"198.51.100.{random.randint(1,254)}"],
    }


class NRFUser(HttpUser):
    """
    Simulates an NRF client registering instances,
    with a configurable fraction of tampered requests.
    """
    host = TARGET_HOST          
    wait_time = between(0.05, 0.25)

    @task(3)
    def register(self):
        """
        Generate a new NF profile, optionally mark it as malicious,
        store the ground-truth in Redis, and send to the injector service.
        """
        nf_id = str(uuid.uuid4())
        profile = build_nf_profile(nf_id)

        malicious = random.random() < ATTACK_RATE

        headers = {"Content-Type": "application/json"}
        if malicious:
            headers["X-Tamper"] = "1"
        
        r.hset("truth", nf_id, int(malicious))
        r.hset("truth_ts", nf_id, time.time())

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



