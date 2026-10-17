#!/usr/bin/env bash
set -euo pipefail
expected=8692e926198056d0228c1e166b1b6c34a5bed66c
for tool in forge anvil; do
  actual="$($tool --version | sed -n 's/^Commit SHA: //p')"
  [[ "$actual" == "$expected" ]] || { echo "$tool must be Foundry v1.0.0 ($expected)" >&2; exit 1; }
done
