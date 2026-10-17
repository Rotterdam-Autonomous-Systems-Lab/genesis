#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
case "$(uname -s)-$(uname -m)" in
  Darwin-x86_64) platform=macosx-amd64; expected=81515b0e53deaa266d549545ccaac0a5a96e6d4e8201c77f673b2c710976d9ea ;;
  Linux-x86_64) platform=linux-amd64; expected=9a0fb7e0db2c0641dbae1c5cc645dc686820c83af516226abb1c0a2f76636f25 ;;
  *) echo "Unsupported compiler platform; no download attempted" >&2; exit 1 ;;
esac
checksum() {
  if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d ' ' -f 1
  else shasum -a 256 "$1" | cut -d ' ' -f 1; fi
}
mkdir -p internal/tools
if [[ -f internal/tools/solc ]] && [[ "$(checksum internal/tools/solc)" == "$expected" ]]; then
  chmod +x internal/tools/solc
  exit 0
fi
trap 'rm -f internal/tools/solc.part' EXIT
curl --proto '=https' --tlsv1.2 -L --fail --silent --show-error --max-time 240 \
  "https://raw.githubusercontent.com/ethereum/solc-bin/gh-pages/${platform}/solc-${platform}-v0.8.28+commit.7893614a" \
  -o internal/tools/solc.part
[[ "$(checksum internal/tools/solc.part)" == "$expected" ]] || { echo "Compiler checksum mismatch" >&2; exit 1; }
chmod +x internal/tools/solc.part
mv internal/tools/solc.part internal/tools/solc
