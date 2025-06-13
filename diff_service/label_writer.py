"""
Subscribe to verdicts channel, correlate with ground truth, 
and write CSV rows: nfInstanceId, malicious flag, verdict, timestamp.
"""

import csv, json, os, sys, time
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

rdb = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
sub = rdb.pubsub()
sub.subscribe("verdicts")

w = csv.writer(sys.stdout)
w.writerow(["nfInstanceId", "malicious", "verdict", "timestamp"])

for msg in sub.listen():
    if msg["type"] != "message":
        continue

    data = json.loads(msg["data"])
    nf_id   = data.get("nfInstanceId")
    verdict = data.get("verdict")

    # Look up ground truth; default to 0 (benign) if not present
    try:
        malicious = int(rdb.hget("truth", nf_id) or 0)
        ts        = int(float(rdb.hget("truth_ts", nf_id) or time.time()))
    except Exception:
        malicious, ts = 0, int(time.time())

    w.writerow([nf_id, malicious, verdict, ts])
    sys.stdout.flush()
