import os
import json
import redis
import yaml
import time 
import logging 
from flask import Flask, Response, request, stream_with_context
from deepdiff import DeepDiff
from jsonschema import Draft7Validator
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Histogram

# --- Configuration ---
REDIS_HOST = os.getenv("REDIS_HOST", 'redis')
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
SCHEMA_PATH = "nf_profile_schema.json"
RULES_PATH = "comparison_rules.yaml"
TOLERANCE = float(os.getenv("NUMERIC_TOLERANCE", 1e-6))
STRICT_OPTIONAL = os.getenv("STRICT_OPTIONAL", "false").lower() == "true"
MAX_DIFF_VOLUME = int(os.getenv("MAX_DIFF_VOLUME", 50))

# --- Bootstrap ---
app = Flask(__name__)
metrics = PrometheusMetrics(app)
rdb = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
pubsub = rdb.pubsub()
pubsub.subscribe("diffs")
print(rdb.pubsub_channels())

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

VERDICT_LATENCY = Histogram(
    "verdict_latency_seconds",                   
    "Time from receiving a diff to emitting a verdict",
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5)  
)

# Load and compile JSON Schema
with open(SCHEMA_PATH) as f:
    SCHEMA = json.load(f)
validator = Draft7Validator(SCHEMA)
MANDATORY = set(SCHEMA.get("required", []))
ALL_FIELDS = set(SCHEMA.get("properties", {}).keys())

# Load rule configuration
with open(RULES_PATH) as f:
    RULES = yaml.safe_load(f)["rules"]

# --- Utility Functions ---
def get_value_by_path(data, path):
    keys = path.split(".")
    for key in keys:
        if isinstance(data, list):
            key = int(key)
        data = data.get(key) if isinstance(data, dict) else data[key]
    return data

def remove_vendor_extensions(obj, schema_props=SCHEMA.get("properties", {})):
    if isinstance(obj, dict):
        return {
            k: remove_vendor_extensions(v, schema_props.get(k, {}))
            for k, v in obj.items() if k in schema_props
        }
    if isinstance(obj, list):
        return [remove_vendor_extensions(i, schema_props.get("items", {})) for i in obj]
    return obj

def compare_field(val_a, val_b, rule):
    comp_type = rule["compare"]
    # Handle missing values early
    if val_a is None or val_b is None:
        return comp_type == "ignore"
    if comp_type == "exact":
        return val_a == val_b
    elif comp_type == "numeric_tolerance":
        try:
            return abs(float(val_a) - float(val_b)) <= rule.get("epsilon", TOLERANCE)
        except Exception:
            return False
    elif comp_type == "set_equality":
        try:
            return set(val_a) == set(val_b)
        except TypeError:
            return False
    elif comp_type == "ignore":
        return True
    return False

def assess_diff(reference, open5gs, free5gc):
    A = remove_vendor_extensions(open5gs)
    B = remove_vendor_extensions(free5gc)

    if not STRICT_OPTIONAL:
        for opt in set(ALL_FIELDS) - MANDATORY:
            if opt not in A:
                A[opt] = B.get(opt)
            if opt not in B:
                B[opt] = A.get(opt)

    diff_result = []
    verdict = "OK"

    for rule in RULES:
        path = rule["path"]
        try:
            val_a = get_value_by_path(A, path)
            val_b = get_value_by_path(B, path)
        except Exception:
            val_a = val_b = None

        if not compare_field(val_a, val_b, rule):
            severity = rule.get("severity", "low")
            diff_result.append({
                "path": path,
                "value_open5gs": val_a,
                "value_free5gc": val_b,
                "severity": severity,
                "reason": f"Field mismatch using {rule['compare']} comparison"
            })
            if severity == "critical":
                verdict = "CRITICAL"
            elif severity == "moderate" and verdict != "CRITICAL":
                verdict = "WARNING"

    if len(diff_result) > MAX_DIFF_VOLUME and verdict != "CRITICAL":
        verdict = "SUSPICIOUS"

    return verdict, diff_result

def safe_load(txt):
    """
    Parse JSON, but return {} on empty string or invalid JSON.
    """
    if not txt:
        return {}
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return {}
    

# --- SSE Endpoint for Analysis ---
@app.route("/analysis/latest", methods=['GET','OPTIONS'])
def stream_analysis():
    headers = {
        "Content-Type":  "text/event-stream",
        "Cache-Control":  "no-cache",
        "Connection":     "keep-alive"
    }
    def events():
        for msg in pubsub.listen():
            if msg["type"] != "message": continue

            t0 = time.perf_counter()               

            raw = json.loads(msg["data"])
            req     = safe_load(raw.get("request",  ""))
            o5gs    = safe_load(raw.get("open5gs",  ""))
            f5gc    = safe_load(raw.get("free5gc",  ""))
            verdict, report = assess_diff(req, o5gs, f5gc)

            VERDICT_LATENCY.observe(time.perf_counter() - t0)  

            out = {
                "nfInstanceId": req.get("nfInstanceId"),
                "verdict": verdict,
                "report": report,
                "timestamp": int(time.time())
            }
            rdb.publish("verdicts", json.dumps(out))
            logging.info("published verdict for %s", req.get("nfInstanceId"))
            yield f"data: {json.dumps(out)}\n\n"
        logging.info("These messages are being trasmitted:", msg)
    return Response(stream_with_context(events()), headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9100)