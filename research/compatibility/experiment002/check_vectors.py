"""Check public vectors with pinned Cast, Python and Anvil's ecrecover precompile.

Compatibility tooling only: no Experiment 002 protocol implementation, keys,
transactions or contract deployment. Requires the existing local pinned tools.
"""

import json
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

from eth_account import Account
from eth_account.messages import encode_typed_data

ROOT = Path(__file__).resolve().parents[3]
FOUNDRY_COMMIT = "8692e926198056d0228c1e166b1b6c34a5bed66c"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    vectors = json.loads(
        (ROOT / "docs/experiments/EXPERIMENT_002_SIGNING_VECTORS.json").read_text()
    )
    cast = str(ROOT / "internal/tools/foundry/cast")
    anvil = str(ROOT / "internal/tools/foundry/anvil")
    started = time.monotonic()
    end = started + 90
    for tool in (cast, anvil):
        version = subprocess.check_output([tool, "--version"], text=True, timeout=5)
        assert FOUNDRY_COMMIT in version, "unexpected Foundry binary version"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def cli(*args):
        remaining = end - time.monotonic()
        assert remaining > 0, "compatibility check time budget"
        return subprocess.check_output(
            [cast, *args], text=True, timeout=min(5, remaining)
        ).strip()

    def typed_hash(name, fields, values):
        schema = name + "(" + ",".join(f["type"] + " " + f["name"] for f in fields) + ")"
        arguments = [cli("keccak", schema)]
        types = ["bytes32"]
        for field in fields:
            value = values[field["name"]]
            kind = field["type"]
            if kind == "string":
                value = cli("keccak", value)
                kind = "bytes32"
            types.append(kind)
            arguments.append(str(value))
        encoded = cli("abi-encode", "f(" + ",".join(types) + ")", *arguments)
        return cli("keccak", encoded)

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    node = subprocess.Popen(
        [anvil, "--host", "127.0.0.1", "--port", str(port), "--chain-id", "31337",
         "--accounts", "0", "--silent"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    def rpc(method, params):
        assert method in {"eth_chainId", "eth_accounts", "eth_call"}
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}", data=body.encode(),
            headers={"Content-Type": "application/json"},
        )
        with opener.open(request, timeout=3) as response:
            result = json.load(response)
        assert "error" not in result, "compatibility RPC error"
        return result["result"]

    try:
        startup = time.monotonic() + 8
        while True:
            try:
                assert rpc("eth_chainId", []) == "0x7a69"
                break
            except (OSError, AssertionError):
                if time.monotonic() > startup:
                    raise
                time.sleep(0.05)
        assert rpc("eth_accounts", []) == []
        artifacts = [
            artifact for fixture in vectors["fixtures"]
            for artifact in (fixture["terms"], fixture["authorization"], fixture["claim"])
        ] + list(vectors["additionalArtifacts"].values())
        domains = {}
        signature_count = 0
        for artifact in artifacts:
            typed = artifact["typedData"]
            key = json.dumps(typed["domain"], sort_keys=True)
            if key not in domains:
                domains[key] = typed_hash(
                    "EIP712Domain", typed["types"]["EIP712Domain"], typed["domain"]
                )
            struct = typed_hash(
                typed["primaryType"], typed["types"][typed["primaryType"]], typed["message"]
            )
            digest = cli("keccak", "0x1901" + domains[key][2:] + struct[2:])
            assert domains[key] == artifact["domainSeparator"]
            assert struct == artifact["structHash"] and digest == artifact["digest"]
            for role, signature in artifact["signatures"].items():
                raw = bytes.fromhex(signature[2:])
                data = ("0x" + digest[2:] + int(raw[64]).to_bytes(32, "big").hex()
                        + raw[:32].hex() + raw[32:64].hex())
                recovered = rpc("eth_call", [
                    {"to": "0x" + "0" * 39 + "1", "data": data}, "latest"
                ])
                assert "0x" + recovered[-40:] == vectors[role]
                python_address = Account.recover_message(
                    encode_typed_data(full_message=typed), signature=signature
                ).lower()
                assert python_address == vectors[role]
                signature_count += 1
        print(json.dumps({
            "digests_checked_with_cast": len(artifacts),
            "signatures_checked_with_anvil_ecrecover_and_python": signature_count,
            "transactions_sent": 0,
            "contracts_deployed": 0,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }))
    finally:
        node.terminate()
        try:
            node.wait(timeout=2)
        except subprocess.TimeoutExpired:
            node.kill()
            node.wait(timeout=2)
        assert node.poll() is not None


if __name__ == "__main__":
    main()
