#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/sdk/python"
exec internal/agent-venv/bin/python -m genesis_experiment.runner "$@"
