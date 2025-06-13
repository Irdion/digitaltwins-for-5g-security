# digitaltwins-for-5g-security
# 5G NRF Comparison Framework

A containerized testbed for side-by-side evaluation of two 5G NRF implementations (Open5GS & Free5GC), featuring:

* **Envoy proxy** with embedded Lua fan-out filter
* **Diff-Worker** to ingest paired requests/responses
* **Diff-Service** to apply schema validation, YAML-driven comparison rules, and verdict assignment
* **React & Material-UI Dashboard** for live testing and JSON diff visualization
* **Locust injector** for load-generation, with ground-truth labeling in Redis
* **Latency plotting** scripts for performance analysis

---

## 📦 Repository Structure

```
/
├── compose/                      # Docker Compose files for the core stack
├── dashboard/                    # React dashboard (Vite, MUI, react-json-view)
├── diff-worker/                  # Flask ingestor: POST /diff → Redis queue
├── diff-service/                 # Flask processor: Redis subscriber → diff logic → SSE
├── injector/                     # Flask HTTP/2 client to drive Envoy + fetch diffs
├── evaluation_system/            # Docker Compose and configuration files for the evaluation system 
├── results/                      # Evaluation results and helper scripts
├── open5gs/                      # Scripts & Dockerfiles to build Open5GS NRF
├── free5gc/                      # Scripts & Dockerfiles to build Free5GC NRF
├── system_setup.sh               # Bootstrap: network, build, up/down, dashboard launch
└── README.md                     # ← you are here
```

---

## 🚀 Quick Start

### Prerequisites

* Docker & Docker Compose
* Node.js **≥16** & npm (for dashboard)
* Python 3.9+ (for scripts)

### 1. Bootstrap Everything

```bash
# Create network, build images, start core services & dashboard
./system_setup.sh run
```

### 2. Generate Traffic

* **Dashboard**: open your browser at [http://localhost:5173](http://localhost:5173)
* **API**: send SSE-backed test calls via `/api/test` (JSON wrapper)
* **Locust**: open your browser at [http://localhost:8089](http://localhost:8089) or also via the CLI 

  ```bash
  cd locust
  locust -f locustfile.py --host=http://injector:7100
  ```
  
### 3. Tear Down

```bash
./system_setup.sh down
```

---

## 🔧 Configuration

All services read settings from environment variables or mounted YAML/JSON files:

| Service      | Key                                    | Default                | Description                        |
| ------------ | -------------------------------------- | ---------------------- | ---------------------------------- |
| Envoy proxy  | —                                      | —                      | Config in `compose/.../envoy.yaml` |
| diff-service | `REDIS_HOST`, `REDIS_PORT`             | `redis:6379`           | Redis connection                   |
| diff-worker  | `NUMERIC_TOLERANCE`                    | `1e-6`                 | Epsilon for numeric comparisons    |
|              | `STRICT_OPTIONAL`                      | `false`                | Fill missing optional fields?      |
|              | `MAX_DIFF_VOLUME`                      | `50`                   | Threshold for “SUSPICIOUS” verdict |
| injector     | `ENVOY_HOST`, `ENVOY_PORT`             | `proxy:8080`           | Envoy service to forward SBI calls |
|              | `DIFF_WORKER_HOST`, `DIFF_WORKER_PORT` | `diff_worker:9000`     | Diff ingestion API                 |
| locust       | `TARGET_HOST`                          | `http://injector:7100` | Injector endpoint                  |
|              | `ATTACK_RATE`                          | `0.25`                 | Fraction of tampered requests      |
| dashboard    | `VITE_PORT`                            | `5173`                 | Dev server port                    |

To override any value, export the variable before running `system_setup.sh` or your service directly.

---

## 🎯 Contributing

1. Fork the repo & create your feature branch
2. Write code, add tests, update docs
3. Open a Pull Request


