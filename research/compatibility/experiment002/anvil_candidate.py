"""Explicit isolated candidate pin; checksum before execution, no PATH replacement."""
import hashlib
import json
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = Path(__file__).with_name("anvil-candidate.json")


def profile():
    data = json.loads(MANIFEST.read_text())
    key = platform.system().lower() + "-" + platform.machine().lower()
    if key not in data["platforms"]:
        raise RuntimeError("unsupported candidate platform")
    return data, data["platforms"][key]


def candidate_path():
    data, target = profile()
    path = ROOT / data["installDirectory"] / "anvil"
    if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != target["binarySha256"]:
        raise RuntimeError("candidate missing or checksum mismatch; no execution")
    version = subprocess.check_output([str(path), "--version"], text=True, timeout=3)
    if "Commit SHA: " + data["commit"] not in version or data["version"] not in version:
        raise RuntimeError("candidate source/version mismatch")
    return str(path)
