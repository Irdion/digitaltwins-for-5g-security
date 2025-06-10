import os, json, logging
from flask import Flask, request, Response
import redis
from prometheus_flask_exporter import PrometheusMetrics

logging.basicConfig(level=logging.INFO)

# Configuration via environment
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_KEY  = os.getenv('REDIS_KEY', 'diffs')

# Initialize Flask and Redis
app = Flask(__name__)
metrics = PrometheusMetrics(app)
app.logger.setLevel(logging.INFO)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route('/diff', methods=['POST'])
def receive_diff():
    payload = request.get_json(force=True)
    r.lpush('diffs', json.dumps(payload))
    r.ltrim('diffs', 0, 999)
    r.publish('diffs', json.dumps(payload))
    app.logger.info(f"Received diff payload: {payload}")
    # return the stored object with a 200:
    return (json.dumps(payload), 200, {'Content-Type':'application/json'})
    

@app.route('/diffs/latest', methods=['GET','OPTIONS'])
def get_latest_diffs():
    if request.method == 'OPTIONS':
        return ('', 200)
    # Get the most recent N diffs
    count = int(request.args.get('count', 20))
    items = r.lrange(REDIS_KEY, 0, count - 1)
    # Decode JSON
    diffs = [json.loads(it.decode('utf-8')) for it in items]
    return Response(json.dumps(diffs), mimetype='application/json')

for rule in app.url_map.iter_rules():
    print(f"Route: {rule.methods} -> {rule}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
