#!/usr/bin/env bash
set -euo pipefail
expected=e144b82070619b6e10485c38734b4d4d45aebe04
for tool in forge anvil; do
  actual="$($tool --version | sed -n 's/^Commit SHA: //p')"
  [[ "$actual" == "$expected" ]] || { echo "$tool must be Foundry v1.0.0 ($expected)" >&2; exit 1; }
done
