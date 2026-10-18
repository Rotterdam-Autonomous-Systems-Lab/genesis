"""Install only checksum-pinned Anvil beside existing tools; HTTPS setup only."""
import argparse
import hashlib
import json
import os
import subprocess
import tarfile
from pathlib import Path

from anvil_candidate import ROOT, profile, candidate_path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url, target, seconds):
    subprocess.run(["curl", "--disable", "--fail", "--silent", "--show-error", "--location",
        "--proto", "=https", "--proto-redir", "=https", "--max-time", str(seconds),
        url, "-o", str(target)], check=True, timeout=seconds+5)


def install(archive=None):
    data, target = profile()
    directory = ROOT / data["installDirectory"]
    if not directory.resolve().is_relative_to((ROOT / "internal").resolve()):
        raise RuntimeError("installation must remain inside ignored internal directory")
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / "anvil"
    if destination.exists():
        return candidate_path()  # Fail closed on existing wrong bytes; never overwrite another tool.
    source = directory / "upstream-source.rs"
    download(data["source"]["url"], source, 20)
    if digest(source) != data["source"]["sha256"]:
        raise RuntimeError("source identity mismatch")
    archive_path = Path(archive) if archive else directory / "upstream.tar.gz"
    if archive is None:
        download(target["archiveUrl"], archive_path, 180)
    if digest(archive_path) != target["archiveSha256"]:
        raise RuntimeError("archive integrity mismatch; no extraction/execution")
    with tarfile.open(archive_path) as bundle:
        member = bundle.getmember("anvil")
        if not member.isfile() or not 0 < member.size < 200_000_000:
            raise RuntimeError("unexpected archive member")
        binary = bundle.extractfile(member).read()
    if hashlib.sha256(binary).hexdigest() != target["binarySha256"]:
        raise RuntimeError("binary integrity mismatch; no execution")
    temporary = directory / "anvil-install.tmp"
    try:
        with temporary.open("xb") as stream:
            stream.write(binary)
        temporary.chmod(0o755)
        os.link(temporary, destination)  # Atomic no-clobber installation; no tar path extraction.
    finally:
        temporary.unlink(missing_ok=True)
    result = candidate_path()  # Source/version and shared-library load check after integrity checks.
    (directory / "installation.json").write_text(json.dumps({"commit":data["commit"],
        "sourceSha256":digest(source),"archiveSha256":digest(archive_path),
        "binarySha256":digest(destination),"hardfork":data["hardfork"]},sort_keys=True,indent=2)+"\n")
    return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--archive")
    args=parser.parse_args()
    print(install(args.archive))
