#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "➤ Creating Docker network if needed…"
NETWORK_NAME=nrf_net
SUBNET=10.55.55.0/24
BRIDGE=br-nrf
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


docker compose -f compose/digital-twin-stack-compose.yaml up -d

echo "➤ Containers on $NETWORK_NAME:"
docker ps --filter "network=$NETWORK_NAME" \
          --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
