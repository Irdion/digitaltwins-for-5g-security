# injector/app.py
import os
import json
from flask import Flask, request, Response
import httpx
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

# Configuration: Envoy address (service name in Docker Compose) + port
ENVOY_HOST = os.getenv("ENVOY_HOST", "proxy")
ENVOY_PORT = int(os.getenv("ENVOY_PORT", 8080))
API_ROOT   = f"http://{ENVOY_HOST}:{ENVOY_PORT}"

DW_HOST = os.getenv("DIFF_WORKER_HOST", "diff_worker")
DW_PORT = int(os.getenv("DIFF_WORKER_PORT", 9000))
DIFF_URL       = f"http://{DW_HOST}:{DW_PORT}/diffs/latest?count=1"

app = Flask(__name__)
metrics = PrometheusMetrics(app) 
CORS(app)
# HTTP/2 client via httpx
client = httpx.Client(http2=True, base_url=API_ROOT)

@app.route('/api/test', methods=['POST'])
def api_test():
    """
    Run an arbitrary HTTP/2 request through Envoy.
    Expects JSON payload:
      {
        "method": "GET",
        "path": "/nnrf-nfm/v1/nf-instances?nf-type=UPF&limit=10",
        "headers": {"Accept": "application/json"},
        "body": null
      }
    Returns JSON:
      {
        "status": 200,
        "headers": { ... },
        "body": "..."
      }
    """
    data    = request.get_json(force=True)
    method  = data.get('method', 'GET')
    path    = data['path']
    headers = data.get('headers', {})
    body    = data.get('body', None)

    # Forward the request through Envoy
    resp = client.request(method, path, headers=headers, content=body)

    result = {
        'status':  resp.status_code,
        'headers': dict(resp.headers),
        'body':    resp.text,
    }

    try:
        diff_resp = httpx.get(DIFF_URL, timeout=5.0)
        diffs = diff_resp.json()
        result["diff"] = diffs[0] if isinstance(diffs, list) and diffs else None
    except Exception as e:
        result["diff_error"] = str(e)

    return Response(json.dumps(result), status=200, mimetype="application/json")

if __name__ == '__main__':
    # App listens on port 7100 for dashboard to drive tests
    app.run(host='0.0.0.0', port=7100)
