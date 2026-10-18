"""Disposable local fixture. Operator funding/limits are not peer-controlled."""

import argparse
import hashlib
import json
import os
import resource
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from eth_account import Account
from web3 import Web3
from genesis_experiment.runner import stop
from genesis_experiment.chain import connect
from genesis_experiment.protocol import Inconclusive, Rejected
from .chain import Chain, ATTEMPTS, RESERVATION, METHODS
from .protocol import PRICE, integer, read, write, tuple_for

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/compatibility/experiment002"))
from anvil_candidate import candidate_path, profile

ARTIFACT = ROOT / "out/Experiment002Escrow.sol/Experiment002Escrow.json"
BAD_MESSAGES = (
    "malformed_evidence",
    "oversized_evidence",
    "truncated_evidence",
    "outsider_evidence",
    "duplicate_evidence",
)
SCENARIOS = BAD_MESSAGES + (
    "success",
    "requester_refusal",
    "requester_offline",
    "invalid_result",
    "provider_crash_before",
    "provider_crash_after",
    "early_disclosure",
    "no_actor",
    "requester_crash_before",
    "provider_crash_after_claim",
    "late_funding",
    "reorg",
)


class Fixture:
    def __enter__(self):
        self.processes = []
        self.started = time.monotonic()
        self.peak_rss = 0
        self.temp = tempfile.TemporaryDirectory(
            prefix="experiment-002-", dir=ROOT / "internal"
        )
        self.folder = Path(self.temp.name)
        try:
            with socket.socket() as s:
                s.bind(("127.0.0.1", 0))
                port = s.getsockname()[1]
            self.rpc = f"http://127.0.0.1:{port}"
            self.node = subprocess.Popen(
                [
                    candidate_path(),
                    "--hardfork",
                    "cancun",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--chain-id",
                    "31337",
                    "--accounts",
                    "0",
                    "--silent",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.processes.append(self.node)
            for _ in range(160):
                try:
                    self.w3 = connect(self.rpc)
                    break
                except Exception:
                    if self.node.poll() is not None:
                        raise Inconclusive("node startup")
                    time.sleep(0.05)
            else:
                raise Inconclusive("node startup timeout")
            node_info = self.rpc_call("anvil_nodeInfo", [])
            if (
                node_info["hardFork"].lower() != "cancun"
                or node_info["forkConfig"]["forkUrl"] is not None
            ):
                raise Inconclusive("wrong node environment")
            self.artifact = json.loads(ARTIFACT.read_text())
            self.run_id = "0x" + secrets.token_hex(32)
            self.deployer = Account.create()
            self.rpc_call("anvil_setBalance", [self.deployer.address, hex(RESERVATION)])
            deploy = Chain(self.rpc, self.deployer, self.artifact, "deployer", PRICE)
            constructor = self.w3.eth.contract(
                abi=self.artifact["abi"], bytecode=self.artifact["bytecode"]["object"]
            ).constructor(self.run_id)
            # Independently execute creation against nonce-zero local state, before signing.
            expected_runtime = self.w3.eth.call(
                {
                    "from": self.deployer.address,
                    "data": constructor.data_in_transaction,
                    "gas": 2_000_000,
                }
            )
            receipt = deploy.transact(constructor)
            address = receipt["contractAddress"]
            runtime = self.w3.eth.get_code(address)
            if runtime != expected_runtime:
                raise Inconclusive("compiled creation/runtime mismatch")
            self.manifest = {
                "contract": address,
                "runId": self.run_id,
                "codeHash": Web3.to_hex(Web3.keccak(runtime)),
                "artifactHash": hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(),
                "chainId": 31337,
                "principal": PRICE,
                "gas": 2_000_000,
                "maxFeePerGas": 3_000_000_000,
                "maxPriorityFeePerGas": 1_000_000_000,
                "nodeCommit": profile()[0]["commit"],
                "hardfork": "cancun",
                "compilerMetadataHash": hashlib.sha256(
                    self.artifact["rawMetadata"].encode()
                ).hexdigest(),
                "attempts": ATTEMPTS,
                "rpcTimeout": 1,
                "wallSeconds": 120,
                "cleanupSeconds": 15,
            }
            self.contract = self.w3.eth.contract(
                address=address, abi=self.artifact["abi"]
            )
            self.deployment = deploy.evidence()
            self.deployment_intents = deploy.intents
            self.deployment_block = receipt["blockNumber"]
            self.budget = deploy.budget
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def rpc_call(self, method, params):
        response = self.w3.provider.make_request(method, params)
        if "error" in response:
            raise Inconclusive("fixture RPC error")
        return response["result"]

    def advance(self, timestamp):
        self.rpc_call("evm_setNextBlockTimestamp", [timestamp])
        self.rpc_call("evm_mine", [])

    def guard(self):
        if time.monotonic() - self.started >= 120:
            raise Inconclusive("wall budget exhausted")
        # Cooperative watchdog, sampling can overshoot; no hostile-host containment claim.
        pids = [os.getpid()] + [p.pid for p in self.processes if p.poll() is None]
        output = subprocess.check_output(
            ["ps", "-o", "rss=", "-p", ",".join(map(str, pids))], text=True, timeout=1
        )
        self.peak_rss = max(self.peak_rss, sum(int(v) for v in output.split()) * 1024)
        if self.peak_rss > 2 * 1024**3:
            raise Inconclusive("RSS watchdog threshold")

    def wait(self, name, parse=True):
        path = self.folder / name
        while not path.exists():
            self.guard()
            for role in ("requester", "provider"):
                if (self.folder / (role + "-error.json")).exists():
                    raise Inconclusive(
                        "agent rejected/failed: "
                        + role
                        + " "
                        + str(read(self.folder / (role + "-error.json")))
                    )
            time.sleep(0.025)
        return read(path) if parse else None

    def __exit__(self, *args):
        start = time.monotonic()
        for p in reversed(self.processes):
            stop(p)
        self.children_stopped = all(p.poll() is not None for p in self.processes)
        self.cleanup_seconds = time.monotonic() - start
        self.exit_status = [p.returncode for p in self.processes]
        self.temp.cleanup()
        if not self.children_stopped or self.cleanup_seconds > 15:
            raise Inconclusive("cleanup budget")


def audit_ledger(f, ready, agreement_id, config):
    """Independent closed-ledger audit, including receipts of terminated agents."""
    audit = Chain(f.rpc, f.deployer, f.artifact, "deployer", PRICE, f.manifest)
    names = {
        f.deployer.address: "deployer",
        **{v["address"]: r for r, v in ready.items()},
    }
    balances = {
        "deployer": RESERVATION,
        "requester": 8 * RESERVATION + PRICE,
        "provider": 8 * RESERVATION,
    }
    fees = {role: 0 for role in balances}
    attempts = {role: 0 for role in balances}
    gas = {}
    times = {}
    funded_count = 0
    for number in range(f.deployment_block, f.w3.eth.block_number + 1):
        block = f.w3.eth.get_block(number)
        for digest in block["transactions"]:
            receipt = f.w3.eth.get_transaction_receipt(digest)
            tx = f.w3.eth.get_transaction(digest)
            audit.canonical_receipt(receipt, digest)
            if tx["from"] not in names:
                raise Inconclusive("unauthorized fixture sender")
            role = names[tx["from"]]
            method = (
                "constructor"
                if tx["to"] is None
                else f.contract.decode_function_input(tx["input"])[0].fn_name
            )
            if method not in METHODS[role] or (
                method != "constructor" and tx["to"] != f.contract.address
            ):
                raise Inconclusive("unauthorized fixture target/method")
            fee = receipt["gasUsed"] * receipt["effectiveGasPrice"]
            balances[role] -= fee
            fees[role] += fee
            attempts[role] += 1
            if (
                attempts[role] > ATTEMPTS[role]
                or fees[role] > ATTEMPTS[role] * RESERVATION
            ):
                raise Inconclusive("cumulative fee budget exceeded")
            gas.setdefault(method, []).append(receipt["gasUsed"])
            times.setdefault(method, []).append(
                {
                    "timestamp": block["timestamp"],
                    "hash": Web3.to_hex(digest),
                    "status": receipt["status"],
                    "claimSlack": config["claimBefore"] - block["timestamp"],
                }
            )
            if receipt["status"] == 0:
                continue
            if method == "fund":
                funded_count += 1
                if funded_count != 1 or tx["value"] != PRICE:
                    raise Inconclusive("principal budget exceeded")
                audit.check_event(
                    receipt,
                    "Funded",
                    {
                        "agreementId": agreement_id,
                        "requester": ready["requester"]["address"],
                        "provider": ready["provider"]["address"],
                        "authorizationNonce": 0,
                        "price": PRICE,
                    },
                )
                balances[role] -= PRICE
            elif method == "withdraw":
                audit.check_event(
                    receipt, "Withdrawn", {"owner": tx["from"], "amount": PRICE}
                )
                balances[role] += PRICE
            elif method == "claim":
                audit.check_event(
                    receipt,
                    "Claimed",
                    {
                        "agreementId": agreement_id,
                        "provider": ready["provider"]["address"],
                        "authorizationNonce": 0,
                        "value": int(config["x"]) + int(config["y"]),
                        "price": PRICE,
                    },
                )
            elif method == "refund":
                audit.check_event(
                    receipt,
                    "Refunded",
                    {
                        "agreementId": agreement_id,
                        "requester": ready["requester"]["address"],
                        "authorizationNonce": 0,
                        "price": PRICE,
                    },
                )
    for address, role in names.items():
        if f.w3.eth.get_balance(address) != balances[role]:
            raise Inconclusive("whole-run wallet reconciliation failed")
    terms = read(f.folder / "terms.json")["message"]
    record = f.contract.functions.getRecord(agreement_id).call()
    if (
        tuple(Web3.to_hex(v) if isinstance(v, bytes) else v for v in record[0])
        != tuple_for("Terms", terms)
        or record[1] != 0
    ):
        raise Inconclusive("whole-run agreement reconciliation failed")
    if f.contract.functions.nonceStatus(ready["requester"]["address"], 0).call() != 1:
        raise Inconclusive("whole-run nonce mismatch")
    locked = f.contract.functions.lockedPrincipal().call()
    credits = sum(
        f.contract.functions.credits(v["address"]).call() for v in ready.values()
    )
    if (
        locked + credits != f.w3.eth.get_balance(f.contract.address)
        or credits != f.contract.functions.totalCredits().call()
    ):
        raise Inconclusive("whole-run liabilities mismatch")
    return {
        "balances": balances,
        "fees": fees,
        "attempts": attempts,
        "gasUsed": gas,
        "inclusion": times,
        "reservedFees": {r: attempts[r] * RESERVATION for r in attempts},
        "principalFundings": funded_count,
    }


def run(scenario="success", x="7", y="11"):
    if scenario not in SCENARIOS:
        raise ValueError("scenario")
    integer(x, 64)
    integer(y, 64)
    started = time.monotonic()
    cpu_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    self_before = resource.getrusage(resource.RUSAGE_SELF)
    with Fixture() as f:
        folder = f.folder
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(ROOT / "sdk/python"),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        agents = {}
        for role in ("provider", "requester"):
            p = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "genesis_experiment002.agent",
                    role,
                    str(folder),
                ],
                env=env,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            agents[role] = p
            f.processes.append(p)
        ready = {r: f.wait(r + "-ready.json") for r in agents}
        if (
            ready["requester"]["address"] == ready["provider"]["address"]
            or ready["requester"]["pid"] == ready["provider"]["pid"]
        ):
            raise Inconclusive("independence")
        for r in agents:
            f.rpc_call(
                "anvil_setBalance",
                [
                    ready[r]["address"],
                    hex(8 * RESERVATION + (PRICE if r == "requester" else 0)),
                ],
            )
        t0 = f.w3.eth.get_block("latest")["timestamp"]
        config = {
            "rpc": f.rpc,
            "artifact": str(ARTIFACT),
            "deploymentIntents": f.deployment_intents,
            "manifest": f.manifest,
            "roles": ready,
            "scenario": scenario,
            "x": x,
            "y": y,
            "fundBefore": t0 + 120,
            "claimBefore": t0 + (121 if scenario == "late_funding" else 300),
        }
        manifest_hash = hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        write(folder / "operator.json", config)
        f.wait("authorization.json")
        if scenario == "requester_crash_before":
            stop(agents["requester"])
            result = {
                "scenario": scenario,
                "outcome": "unfunded",
                "state": f.contract.functions.getRecord(
                    read(folder / "authorization.json")["message"]["agreementId"]
                ).call()[2],
                "agents": ready,
                "deployment": f.deployment,
                "attempted": 0,
            }
        else:
            if scenario == "late_funding":
                f.advance(config["fundBefore"] - 1)
            write(folder / "fund-go.json", {})
            funded = f.wait("funded.json")
            agreement_id = funded["agreementId"]
            snapshot = f.rpc_call("evm_snapshot", []) if scenario == "reorg" else None
            adjustments = []
            if scenario == "provider_crash_before":
                stop(agents["provider"])
            else:
                write(folder / "compute-go.json", {})
                f.wait("claim.json", parse=False)
                write(folder / "observe-go.json", {})
                (
                    f.wait("observed.json")
                    if scenario in BAD_MESSAGES + ("early_disclosure",)
                    else None
                )
            if scenario in BAD_MESSAGES + ("provider_crash_after", "early_disclosure"):
                stop(agents["provider"])
            if scenario == "no_actor":
                # Retain keys inside suspended processes; supervisor observes absence of action.
                import signal

                for p in agents.values():
                    os.kill(p.pid, signal.SIGSTOP)
                f.advance(config["claimBefore"] + 1)
                adjustments.append(config["claimBefore"] + 1)
                if f.contract.functions.getRecord(agreement_id).call()[2] != 1:
                    raise Inconclusive("automatic closure observed")
                for p in agents.values():
                    os.kill(p.pid, signal.SIGCONT)
                stop(agents["provider"])
            refund = scenario in BAD_MESSAGES + (
                "invalid_result",
                "provider_crash_before",
                "provider_crash_after",
                "early_disclosure",
                "no_actor",
                "late_funding",
            )
            if scenario == "requester_offline":
                agents["requester"].wait(timeout=3)
            if scenario == "late_funding":
                f.advance(config["claimBefore"])
                adjustments.append(config["claimBefore"])
            if not refund or scenario in ("invalid_result", "late_funding"):
                write(folder / "claim-go.json", {})
                f.wait("claim-attempted.json")
            if scenario == "reorg":
                f.rpc_call("evm_revert", [snapshot])
                write(folder / "withdraw-go.json", {})
                f.wait("provider-error.json")
                result = {
                    "scenario": scenario,
                    "outcome": "inconclusive",
                    "state": f.contract.functions.getRecord(agreement_id).call()[2],
                    "agents": ready,
                    "deployment": f.deployment,
                }
            else:
                if refund:
                    f.advance(config["claimBefore"] + 2)
                    adjustments.append(config["claimBefore"] + 2)
                    write(folder / "refund-go.json", {})
                else:
                    if scenario == "provider_crash_after_claim":
                        stop(agents["provider"])
                    else:
                        write(folder / "withdraw-go.json", {})
                        f.wait("provider-done.json")
                write(folder / "finish-go.json", {})
                if scenario != "requester_offline":
                    f.wait("requester-done.json")
                record = f.contract.functions.getRecord(agreement_id).call()
                expected_state = 3 if refund else 2
                if record[2] != expected_state or (
                    not refund and record[3] != int(x) + int(y)
                ):
                    raise Inconclusive("independent harness state/result")
                # Reconcile every public report against canonical fee/transaction evidence.
                reports = {
                    r: read(folder / (r + "-done.json"))
                    for r in agents
                    if (folder / (r + "-done.json")).exists()
                }
                transactions = []
                seen = set()
                for report in reports.values():
                    for item in report["receipts"]:
                        if item["hash"] in seen:
                            continue
                        seen.add(item["hash"])
                        digest = Web3.to_bytes(hexstr=item["hash"])
                        receipt = f.w3.eth.get_transaction_receipt(digest)
                        audit = Chain(
                            f.rpc, f.deployer, f.artifact, "deployer", PRICE, f.manifest
                        )
                        audit.canonical_receipt(receipt, digest)
                        audit.receipts = [receipt]
                        if audit.evidence()[0] != item:
                            raise Inconclusive("mutated agent receipt report")
                        transactions.append(item)
                result = {
                    "scenario": scenario,
                    "outcome": "refunded" if refund else "settled",
                    "state": record[2],
                    "value": str(record[3]),
                    "expectedValue": str(int(x) + int(y)),
                    "agents": ready,
                    "reports": reports,
                    "transactions": transactions,
                    "deployment": f.deployment,
                    "timeAdjustments": adjustments,
                    "principal": PRICE,
                    "providerCredit": f.contract.functions.credits(
                        ready["provider"]["address"]
                    ).call(),
                    "lockedPrincipal": f.contract.functions.lockedPrincipal().call(),
                    "totalCredits": f.contract.functions.totalCredits().call(),
                    "resultObserved": (
                        read(folder / "observed.json")
                        if (folder / "observed.json").exists()
                        else None
                    ),
                    "fundingSlack": config["claimBefore"]
                    - int(
                        f.w3.eth.get_block(
                            f.w3.eth.get_transaction_receipt(funded["hash"])[
                                "blockNumber"
                            ]
                        )["timestamp"]
                    ),
                }
        if scenario not in ("reorg", "requester_crash_before"):
            result["ledger"] = audit_ledger(f, ready, agreement_id, config)
        f.guard()
        result.update(
            {
                "deploymentIntents": f.deployment_intents,
                "manifest": f.manifest,
                "operatorHash": manifest_hash,
                "peakRSSBytes": f.peak_rss,
                "logicalCPUs": os.cpu_count(),
                "payloadBytes": {
                    p.name: p.stat().st_size for p in folder.glob("*.json")
                },
                "agreementId": read(folder / "authorization.json")["message"][
                    "agreementId"
                ],
                "elapsedSeconds": round(time.monotonic() - started, 3),
            }
        )
    cpu_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    self_after = resource.getrusage(resource.RUSAGE_SELF)
    result.update(
        {
            "childrenStopped": f.children_stopped,
            "childExitStatus": f.exit_status,
            "cleanupSeconds": f.cleanup_seconds,
            "childCPUSeconds": cpu_after.ru_utime
            + cpu_after.ru_stime
            - cpu_before.ru_utime
            - cpu_before.ru_stime,
            "supervisorCPUSeconds": self_after.ru_utime
            + self_after.ru_stime
            - self_before.ru_utime
            - self_before.ru_stime,
        }
    )
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", choices=SCENARIOS, default="success")
    p.add_argument("--x", default="7")
    p.add_argument("--y", default="11")
    args = p.parse_args()
    print(json.dumps(run(args.scenario, args.x, args.y), sort_keys=True))


if __name__ == "__main__":
    main()
