#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE=${1:-run} 
echo "➤ Creating Docker network if needed…"
NETWORK_NAME=nrf_net
SUBNET=10.55.55.0/24
BRIDGE=br-nrf

create_network() {
if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  docker network create \
    --driver bridge \
    --subnet "$SUBNET" \
    -o "com.docker.network.bridge.name=$BRIDGE" \
    "$NETWORK_NAME"
  echo "  → Created network $NETWORK_NAME"
else
  echo "  → Network $NETWORK_NAME exists"
fi
}

build_images() {
echo "➤ Building Open5GS NRF image…"
(
  cd "$PROJECT_ROOT/open5gs"
  make base-open5gs
  docker compose -f compose-files/basic/docker-compose.yaml \
    --env-file .env build nrf db
)

echo "➤ Building Free5GC NRF image…"
(
  cd "$PROJECT_ROOT/free5gc"
  if [ ! -d base/free5gc ]; then
    pushd base
    git clone --recursive https://github.com/free5gc/free5gc.git
    popd
  fi
  make nrf
  docker compose -f docker-compose-build.yaml build free5gc-nrf
)
}


start_core(){
  docker compose -f compose/digital-twin-stack-compose.yaml up -d
}

start_eval() {
  docker compose -f compose/digital-twin-stack-compose.yaml -f evaluation_system/evaluation-system-compose.yaml up -d 
}

stop_all() {
  docker compose -f compose/digital-twin-stack-compose.yaml -f evaluation_system/evaluation-system-compose.yaml down --remove-orphans
  pkill -f "npm run dev"
}

start_dashboard() {
  echo "➤ Starting dashboard (npm dev)…"
  (
    cd "$PROJECT_ROOT/dashboard"
    # Install dependencies if not already present
    if [ ! -d node_modules ]; then
      npm ci
    fi
    # Launch in background, redirect logs
    nohup npm run dev \
      > "$PROJECT_ROOT/dashboard/dashboard.log" 2>&1 &

    sleep 3

    # Try to open in the default browser
    URL="http://localhost:${DASHBOARD_PORT:-5173}"
    if command -v xdg-open >/dev/null 2>&1; then
      xdg-open "$URL" >/dev/null 2>&1 && echo "  → Opened dashboard at $URL"
    elif command -v open >/dev/null 2>&1; then
      open "$URL"        && echo "  → Opened dashboard at $URL"
    else
      echo "  → Dashboard running at $URL (please open in your browser)"
    fi
  )
}


case $MODE in 
  run)
    create_network
    build_images
    start_core
    start_dashboard
    ;;
  eval) 
    create_network
    build_images
    start_core
    start_eval
    start_dashboard
    ;;
  down)
    stop_all
    ;;
  *)
    echo \"Usage: $0 {run|eval|down}\"
    exit 1
    ;;
esac

echo "➤ Containers on $NETWORK_NAME:"
docker ps --filter "network=$NETWORK_NAME" \
          --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
