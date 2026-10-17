"""Trusted, bounded test harness. No agent private keys enter this process."""
import argparse
import hashlib
import platform
from importlib.metadata import version
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from eth_account import Account
from web3 import Web3

from .chain import Chain, connect
from .protocol import Inconclusive, PRICE, integer, read, wait, write

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "out/Experiment001Escrow.sol/Experiment001Escrow.json"
SCENARIOS = ("success", "invalid_result", "requester_refusal", "provider_killed")


def anvil_path():
    bundled = ROOT / "internal/tools/foundry/anvil"
    path = str(bundled) if bundled.exists() else shutil.which("anvil")
    if not path or "8692e926198056d0228c1e166b1b6c34a5bed66c" not in subprocess.check_output([path, "--version"], text=True):
        raise Inconclusive("pinned Anvil v1.0.0 required")
    return path


def stop(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)


class Fixture:
    def __enter__(self):
        self.processes = []
        self.temp = tempfile.TemporaryDirectory(prefix="experiment-001-", dir=ROOT / "internal")
        self.folder = Path(self.temp.name)
        try:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            self.rpc = f"http://127.0.0.1:{port}"
            self.node = subprocess.Popen([anvil_path(), "--host", "127.0.0.1", "--port", str(port),
                "--chain-id", "31337", "--accounts", "0", "--silent"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.processes.append(self.node)
            end = time.monotonic() + 8
            while True:
                try:
                    self.w3 = connect(self.rpc)
                    break
                except Exception:
                    if time.monotonic() >= end or self.node.poll() is not None:
                        raise Inconclusive("Anvil startup failed")
                    time.sleep(0.05)
            self.artifact = json.loads(ARTIFACT.read_text())
            self.deployer = Account.create()
            self.balance(self.deployer.address)
            deploy = Chain(self.rpc, self.deployer, self.artifact)
            self.run_id = "0x" + secrets.token_hex(32)
            constructor = self.w3.eth.contract(abi=self.artifact["abi"], bytecode=self.artifact["bytecode"]["object"]).constructor(self.run_id)
            receipt = deploy.transact(constructor)
            address = receipt["contractAddress"]
            self.manifest = {"contract": address, "runId": self.run_id,
                "codeHash": Web3.to_hex(Web3.keccak(self.w3.eth.get_code(address)))}
            self.contract = self.w3.eth.contract(address=address, abi=self.artifact["abi"])
            self.deployment = deploy.evidence()
            return self
        except Exception:
            self.__exit__(None, None, None)
            raise

    def balance(self, address):
        self.rpc_call("anvil_setBalance", [address, hex(10**20)])

    def rpc_call(self, method, params):
        response = self.w3.provider.make_request(method, params)
        if "error" in response:
            raise Inconclusive("fixture RPC failed")
        return response["result"]

    def advance(self, timestamp):
        self.rpc_call("evm_setNextBlockTimestamp", [timestamp])
        self.rpc_call("evm_mine", [])

    def __exit__(self, *args):
        for process in reversed(self.processes):
            stop(process)
        self.temp.cleanup()


def run(scenario="success", x="7", y="11"):
    if scenario not in SCENARIOS:
        raise ValueError("unknown fixture")
    integer(x, 64)
    integer(y, 64)
    started = time.monotonic()
    with Fixture() as fixture:
        folder = fixture.folder
        end = started + 60
        write(folder / "config.json", {"rpc": fixture.rpc, "artifact": str(ARTIFACT),
            "manifest": fixture.manifest, "scenario": scenario, "x": x, "y": y})
        # Minimal child environment: no credentials, proxy configuration or key-bearing vars.
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(ROOT / "sdk/python"),
               "PYTHONDONTWRITEBYTECODE": "1"}
        agents = {}
        for role in ("provider", "requester"):
            process = subprocess.Popen([sys.executable, "-m", "genesis_experiment.agent", role, str(folder)],
                env=env, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            agents[role] = process
            fixture.processes.append(process)
        ready = {role: wait(folder / (role + "-ready.json"), end) for role in agents}
        if (ready["requester"]["address"] == ready["provider"]["address"]
                or ready["requester"]["pid"] == ready["provider"]["pid"]):
            raise Inconclusive("distinct processes and identities required")
        for role in agents:
            fixture.balance(ready[role]["address"])
        write(folder / "go.json", {})
        killed = False
        advanced = False
        while time.monotonic() < end:
            errors = list(folder.glob("*-error.json"))
            if errors:
                raise Inconclusive("agent failed: " + ",".join(p.stem + ":" + read(p)["error"] + ":" + read(p)["reason"] for p in errors))
            if scenario == "provider_killed" and not killed and (folder / "compute.json").exists():
                stop(agents["provider"])
                killed = True
            if not advanced and (folder / "refund-wait.json").exists():
                fixture.advance(int(read(folder / "refund-wait.json")["deadline"]))
                advanced = True
            if (folder / "requester-report.json").exists():
                break
            time.sleep(0.025)
        else:
            raise Inconclusive("run budget exceeded")
        requester = read(folder / "requester-report.json")
        expected = "settled" if scenario == "success" else "refunded"
        if requester["outcome"] != expected:
            raise Inconclusive("unexpected outcome")
        for role, process in agents.items():
            if role == "provider" and killed:
                continue
            process.wait(timeout=max(0.1, end - time.monotonic()))
            if process.returncode != 0:
                raise Inconclusive("agent nonzero exit")
        provider = read(folder / "provider-report.json") if not killed else {"outcome": "terminated", "receipts": []}
        record = fixture.contract.functions.getAgreement(requester["agreementId"]).call()
        expected_state = 2 if scenario == "success" else 3
        if (record[2] != expected_state or fixture.contract.functions.totalLocked().call() != 0
                or fixture.contract.functions.totalCredits().call() != 0
                or fixture.contract.functions.totalDeposited().call() != PRICE
                or fixture.contract.functions.totalWithdrawn().call() != PRICE
                or fixture.w3.eth.get_balance(fixture.manifest["contract"]) != 0):
            raise Inconclusive("terminal accounting mismatch")
        if scenario != "success" and (folder / "acceptance.json").exists():
            raise Inconclusive("unexpected acceptance")
        result = {"scenario": scenario, "outcome": expected, "state": str(expected_state),
            "manifest": fixture.manifest,
            "versions": {"python": platform.python_version(), "web3": version("web3"),
                "eth-account": version("eth-account"), "foundryCommit": "8692e926198056d0228c1e166b1b6c34a5bed66c",
                "solidity": "0.8.28+commit.7893614a", "chainId": "31337",
                "requirementsSha256": hashlib.sha256((ROOT / "sdk/python/requirements.lock").read_bytes()).hexdigest()},
            "rejectionCount": "0" if scenario == "success" else "1",
            "agents": ready, "requester": requester,
            "provider": provider, "deployment": fixture.deployment,
            "inputs": {"x": x, "y": y}, "expectedResult": str(int(x) + int(y)),
            "principal": str(PRICE), "messageCount": str(len(list(folder.glob("*.json")))),
            "elapsedSeconds": str(round(time.monotonic() - started, 3))}
        if len(requester["receipts"]) + len(provider["receipts"]) + len(fixture.deployment) > 16:
            raise Inconclusive("run transaction budget")
    result["childrenStopped"] = all(p.poll() is not None for p in fixture.processes)
    if not result["childrenStopped"]:
        raise Inconclusive("child leaked")
    return result


def main():
    parser = argparse.ArgumentParser(description="Local synthetic-fund Experiment 001 only")
    parser.add_argument("--scenario", choices=SCENARIOS, default="success")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.scenario), indent=2))
    except Exception as exc:
        print(json.dumps({"outcome": "inconclusive", "error": type(exc).__name__}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
