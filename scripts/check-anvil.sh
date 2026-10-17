#!/usr/bin/env bash
# Local node availability check only: no contract creation or transaction submission.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p internal
anvil --host 127.0.0.1 --port 18545 --chain-id 31337 --accounts 0 --silent >internal/anvil-smoke.log 2>&1 &
anvil_pid=$!
trap 'kill "$anvil_pid" 2>/dev/null || true; wait "$anvil_pid" 2>/dev/null || true' EXIT
for attempt in {1..30}; do
  kill -0 "$anvil_pid" 2>/dev/null || { echo "Anvil failed to start (possibly port in use)" >&2; exit 1; }
  response="$(curl --noproxy '*' --proto '=http' -s --max-time 1 -H 'Content-Type: application/json' \
    --data '{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}' http://127.0.0.1:18545 || true)"
  if [[ "$(jq -r '.result // empty' <<<"$response")" == "0x7a69" ]]; then
    kill -0 "$anvil_pid"
    echo 'Loopback-only Anvil smoke check passed (no transactions or deployments).'
    exit 0
  fi
  sleep 0.2
done
echo 'Local Anvil check timed out' >&2
exit 1
