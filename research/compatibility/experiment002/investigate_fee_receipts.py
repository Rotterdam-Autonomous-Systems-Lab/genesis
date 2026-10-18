"""Independent raw-JSON-RPC fee investigation; ephemeral loopback fixtures only.

No agent code, Web3 receipt conversion, public RPC, key files or raw-tx logging.
Default exit 2 preserves the strict blocked gate when any contradiction exists.
"""
import argparse
import hashlib
import json
import platform
import re
import secrets
import socket
import subprocess
import time
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

from eth_account import Account
from eth_utils import keccak, to_checksum_address

from fee_evidence import EvidenceContradiction, measurements, require_reconciled

ROOT = Path(__file__).resolve().parents[3]
PIN = "8692e926198056d0228c1e166b1b6c34a5bed66c"
GAS, FEE, PRIORITY = 2_000_000, 3_000_000_000, 1_000_000_000
ARTIFACT = ROOT / "out/FeeWitness.sol/FeeWitness.json"
CASES = (
    ("zero", 0, PRIORITY, False), ("one-gwei", 10**9, PRIORITY, False),
    ("below-tip-clamp", 2*10**9-1, PRIORITY, False), ("at-tip-clamp", 2*10**9, PRIORITY, False),
    ("above-tip-clamp", 2*10**9+1, PRIORITY, False), ("original-inclusion-base", 2_625_000_000, PRIORITY, False),
    ("at-fee-cap", FEE, PRIORITY, False), ("above-fee-cap", FEE+1, PRIORITY, False),
    ("zero-tip-at-cap", FEE, 0, False), ("revert-unclamped", 10**9, PRIORITY, True),
    ("revert-clamped", 2_625_000_000, PRIORITY, True),
)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("RPC redirect refused")


class RpcFailure(Exception):
    def __init__(self, code):
        self.code = code


class LocalNode:
    def __init__(self, candidate=False):
        self.candidate = candidate

    def __enter__(self):
        self.process = None
        self.started = time.monotonic()
        import shutil
        self.binary = str(ROOT / "internal/tools/foundry/anvil")
        if not Path(self.binary).exists():
            self.binary = shutil.which("anvil")
        expected_pin = PIN
        if self.candidate:
            from anvil_candidate import candidate_path, profile
            self.binary = candidate_path()
            expected_pin = profile()[0]["commit"]
        self.version = subprocess.check_output([self.binary, "--version"], text=True, timeout=3).strip()
        if expected_pin not in self.version:
            raise RuntimeError("exact pinned Anvil required")
        self.binary_hash = hashlib.sha256(Path(self.binary).read_bytes()).hexdigest()
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0)); port = sock.getsockname()[1]
        self.url = f"http://127.0.0.1:{port}"
        self.opener = build_opener(ProxyHandler({}), NoRedirect())
        self.process = subprocess.Popen([self.binary, "--host", "127.0.0.1", "--port", str(port),
            "--chain-id", "31337", "--accounts", "0", "--silent"] + (["--hardfork", "cancun"] if self.candidate else []), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    if self.rpc("eth_chainId", []) != "0x7a69":
                        raise RuntimeError("wrong chain")
                    if self.candidate:
                        info = self.rpc("anvil_nodeInfo", [])
                        if info["hardFork"].lower() != "cancun" or info["forkConfig"]["forkUrl"] is not None:
                            raise RuntimeError("candidate hardfork/fork policy mismatch")
                        self.reported_hardfork = info["hardFork"]
                    return self
                except (OSError, RpcFailure):
                    if self.process.poll() is not None:
                        raise RuntimeError("node startup failed") from None
                    time.sleep(.05)
            raise RuntimeError("node startup timeout")
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def rpc(self, method, params):
        if time.monotonic() - self.started > 30:
            raise RuntimeError("diagnostic wall limit")
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        request = Request(self.url, data=body, headers={"Content-Type": "application/json"})
        with self.opener.open(request, timeout=1) as response:
            raw = response.read(262145)
        if len(raw) > 262144:
            raise RuntimeError("RPC response limit")
        result = json.loads(raw)
        if "error" in result:
            # Never forward arbitrary RPC exception bodies/raw transaction fields.
            raise RpcFailure(result["error"]["code"])
        return result["result"]

    def send(self, account, data, to=None, priority=PRIORITY):
        tx = {"chainId":31337, "type":2, "nonce":0, "gas":GAS, "value":0,
              "maxFeePerGas":FEE, "maxPriorityFeePerGas":priority, "data":data}
        if to is not None:
            tx["to"] = to_checksum_address(to)
        signed = account.sign_transaction(tx)
        digest = "0x" + keccak(signed.raw_transaction).hex()
        returned = self.rpc("eth_sendRawTransaction", ["0x" + signed.raw_transaction.hex()])
        if returned != digest:
            raise RuntimeError("broadcast hash differs")
        return digest

    def receipt(self, digest, seconds=3):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            result = self.rpc("eth_getTransactionReceipt", [digest])
            if result is not None:
                return result
            time.sleep(.025)
        return None

    def __exit__(self, *args):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.wait(timeout=2)
        self.stopped = self.process is None or self.process.poll() is not None
        if not self.stopped:
            raise RuntimeError("child cleanup failed")


def run_case(case, repeat, candidate=False):
    name, base, priority, should_revert = case
    with LocalNode(candidate) as node:
        deployer, requester = Account.create(), Account.create()
        for account, balance in ((deployer, GAS*FEE), (requester, 8*GAS*FEE)):
            node.rpc("anvil_setBalance", [account.address, hex(balance)])
        artifact = json.loads(ARTIFACT.read_text())
        deployed = node.receipt(node.send(deployer, artifact["bytecode"]["object"]))
        if deployed is None or deployed["status"] != "0x1":
            raise RuntimeError("witness deployment failed")
        parent = node.rpc("eth_getBlockByNumber", ["latest", False])
        parent_tag = parent["number"]
        before = node.rpc("eth_getBalance", [requester.address, parent_tag])
        admin = node.rpc("anvil_setNextBlockBaseFeePerGas", [hex(base)])
        error_code = None
        digest = None
        try:
            digest = node.send(requester, "0x"+keccak(text="fail()" if should_revert else "observe()")[:4].hex(), deployed["contractAddress"], priority)
        except RpcFailure as exc:
            error_code = exc.code
        receipt = node.receipt(digest, .3 if base>FEE else 3) if digest else None
        common = {"case":name, "repeat":repeat, "requestedBaseFee":base, "requestedPriorityFee":priority,
            "anvilSetNextBlockBaseFeePerGas":{"params":[hex(base)],"result":admin}, "rpcErrorCode":error_code,
            "anvilVersion":node.version, "anvilBinarySha256":node.binary_hash,
            "clientVersion":node.rpc("web3_clientVersion",[]), "chainId":node.rpc("eth_chainId",[])}
        if candidate:
            common["reportedHardfork"] = node.reported_hardfork
        if receipt is None:
            after = node.rpc("eth_getBalance",[requester.address,"latest"])
            common.update({"classification":"not included", "balanceBefore":before,"balanceAfter":after,
                "nonceAfter":node.rpc("eth_getTransactionCount",[requester.address,"latest"]),
                "receipt":None, "transactionHash":digest})
            if base<=FEE or before!=after or common["nonceAfter"]!="0x0":
                raise RuntimeError("unexpected non-inclusion/accounting")
        else:
            tx = node.rpc("eth_getTransactionByHash",[digest])
            block = node.rpc("eth_getBlockByHash",[receipt["blockHash"],False])
            block_receipts = node.rpc("eth_getBlockReceipts",[receipt["blockNumber"]])
            matching = [r for r in block_receipts if r["transactionHash"]==digest]
            if len(matching)!=1 or receipt["status"] != ("0x0" if should_revert else "0x1"):
                raise RuntimeError("missing/incorrect receipt")
            # Exactly one diagnostic call in block; no value, incoming transfers or coinbase reward to sender.
            if len(block["transactions"])!=1 or block["miner"].lower()==requester.address.lower():
                raise RuntimeError("wallet delta isolation violated")
            fields = ("hash","type","chainId","from","to","nonce","value","gas","gasPrice","maxFeePerGas","maxPriorityFeePerGas","blockHash","blockNumber")
            common.update({"transaction":{k:tx[k] for k in fields},
                "receipt":{k:receipt[k] for k in ("transactionHash","blockHash","blockNumber","transactionIndex","type","status","gasUsed","effectiveGasPrice")},
                "block":{k:block[k] for k in ("hash","parentHash","number","baseFeePerGas","gasUsed","transactions")},
                "balanceBefore":before, "balanceAfter":node.rpc("eth_getBalance",[requester.address,receipt["blockNumber"]]),
                "parentNumber":parent_tag,"parentHash":parent["hash"],
                "blockReceiptEffectiveGasPrice":matching[0]["effectiveGasPrice"],
                "nonceAfter":node.rpc("eth_getTransactionCount",[requester.address,receipt["blockNumber"]])})
            if (tx["type"]!="0x2" or int(tx["maxFeePerGas"],16)!=FEE or int(tx["maxPriorityFeePerGas"],16)!=priority
                    or tx["from"].lower()!=requester.address.lower() or int(tx["chainId"],16)!=31337
                    or int(tx["gas"],16)!=GAS or int(tx["value"],16)!=0 or int(tx["nonce"],16)!=0
                    or int(block["baseFeePerGas"],16)!=base):
                raise RuntimeError("signed fields changed")
            if not should_revert:
                logs=receipt["logs"]
                topic="0x"+keccak(text="FeeObserved(uint256,uint256)").hex()
                if len(logs)!=1 or logs[0]["address"].lower()!=deployed["contractAddress"].lower() or logs[0]["topics"]!=[topic] or not re.fullmatch(r"0x[0-9a-f]{128}",logs[0]["data"]):
                    raise RuntimeError("invalid execution witness")
                common["witnessGasPrice"]=hex(int(logs[0]["data"][2:66],16))
                common["witnessBaseFee"]=hex(int(logs[0]["data"][66:],16))
            common["measurements"]=measurements(common)
            try:
                require_reconciled(common)
                common["classification"]="reconciled"
            except EvidenceContradiction:
                common["classification"]="BLOCKED: contradictory RPC fee evidence"
            # Canonical anchors and the execution/debit oracle remain mandatory, even in defect cases.
            if node.rpc("eth_getBlockByNumber",[block["number"],False])["hash"]!=block["hash"] or block["parentHash"]!=parent["hash"]:
                raise RuntimeError("chain evidence changed")
            values=common["measurements"]
            if values["actualDebit"]!=values["expectedFee"] or values["actualDebit"]>values["maxReservation"]:
                raise RuntimeError("actual fee-cap/accounting violation")
            if not should_revert and (int(common["witnessGasPrice"],16)!=values["expectedPrice"] or int(common["witnessBaseFee"],16)!=base):
                raise RuntimeError("execution witness disagrees with fee model")
    common["childrenStopped"]=node.stopped
    return common


def collect(repeats=2, candidate=False):
    if type(repeats) is not int or not 1<=repeats<=2:
        raise ValueError("bounded repeats 1 or 2 required")
    started=time.monotonic()
    results=[run_case(case,repeat,candidate) for repeat in range(repeats) for case in CASES]
    return {"scope":"Task 010 raw-RPC characterization; not Experiment 002 acceptance", "host":platform.platform(),
        "foundryCommit":(__import__("anvil_candidate").profile()[0]["commit"] if candidate else PIN),
        "nodeProfile":"verified candidate / Cancun" if candidate else "original baseline", "artifactSha256":hashlib.sha256(ARTIFACT.read_bytes()).hexdigest(),
        "results":results,"elapsedSeconds":round(time.monotonic()-started,3)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--repeats",type=int,choices=(1,2),default=2)
    parser.add_argument("--candidate",action="store_true",help="Use the separately checksum/source-pinned candidate, not PATH")
    args=parser.parse_args()
    try:
        evidence=collect(args.repeats,args.candidate)
    except Exception:
        print(json.dumps({"classification":"inconclusive diagnostic failure"}));return 3
    print(json.dumps(evidence,indent=2,sort_keys=True))
    return 2 if any(r["classification"].startswith("BLOCKED") for r in evidence["results"]) else 0


if __name__=="__main__":
    raise SystemExit(main())
