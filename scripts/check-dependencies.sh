#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if command -v sha256sum >/dev/null; then sha256sum --check dependencies.sha256
else shasum -a 256 --check dependencies.sha256; fi
