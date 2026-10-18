"""Bounded local reproduction of the Task 009 fee-receipt blocker.

Exit 2 means a canonical fee-evidence contradiction was observed; never treats it
as successful Experiment 002 acceptance. No public endpoint or key persistence.
Build the contract first. Uses the existing pinned dependency baseline.
"""
import json
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path

from eth_account import Account
from web3 import Web3

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "sdk/python"))
from genesis_experiment.chain import connect  # noqa: E402
from genesis_experiment.runner import anvil_path, stop  # noqa: E402

GAS = 2_000_000
MAX_FEE = 3_000_000_000
PRIORITY = 1_000_000_000
RESERVATION = GAS * MAX_FEE


def probe():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    node = subprocess.Popen(
        [anvil_path(), "--host", "127.0.0.1", "--port", str(port),
         "--chain-id", "31337", "--accounts", "0", "--silent"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    started = time.monotonic()
    try:
        for _ in range(160):
            try:
                w3 = connect(f"http://127.0.0.1:{port}")
                break
            except Exception:
                if node.poll() is not None:
                    raise RuntimeError("local node startup failed") from None
                time.sleep(0.05)
        else:
            raise RuntimeError("local node startup timeout")

        def rpc(method, params):
            result = w3.provider.make_request(method, params)
            if "error" in result:
                raise RuntimeError("local fixture RPC failed")
            return result["result"]

        artifact = json.loads((ROOT / "out/Experiment002Escrow.sol/Experiment002Escrow.json").read_text())
        deployer, requester = Account.create(), Account.create()
        # Only initial allowances. No top-ups or peer-controlled fee fields.
        rpc("anvil_setBalance", [deployer.address, hex(RESERVATION)])
        rpc("anvil_setBalance", [requester.address, hex(8 * RESERVATION)])

        def transaction(account, function):
            tx = function.build_transaction({
                "from": account.address, "nonce": w3.eth.get_transaction_count(account.address),
                "chainId": 31337, "type": 2, "value": 0, "gas": GAS,
                "maxFeePerGas": MAX_FEE, "maxPriorityFeePerGas": PRIORITY,
            })
            if w3.eth.get_balance(account.address) < RESERVATION:
                raise RuntimeError("insufficient synthetic fee allowance")
            signed = account.sign_transaction(tx)
            digest = Web3.keccak(signed.raw_transaction)
            returned = w3.eth.send_raw_transaction(signed.raw_transaction)
            if returned != digest:
                raise RuntimeError("broadcast hash mismatch")
            receipt = w3.eth.wait_for_transaction_receipt(digest, timeout=4, poll_latency=.05)
            block = w3.eth.get_block(receipt["blockNumber"])
            if receipt["status"] != 1 or block["hash"] != receipt["blockHash"] or digest not in block["transactions"]:
                raise RuntimeError("noncanonical or failed diagnostic transaction")
            return receipt

        constructor = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"]["object"]).constructor("0x" + secrets.token_hex(32))
        deployment = transaction(deployer, constructor)
        escrow = w3.eth.contract(address=deployment["contractAddress"], abi=artifact["abi"])
        rpc("anvil_setNextBlockBaseFeePerGas", [hex(MAX_FEE)])
        rpc("evm_mine", [])
        balance_before = w3.eth.get_balance(requester.address)
        receipt = transaction(requester, escrow.functions.revokeUnused(9009))
        balance_after = w3.eth.get_balance(requester.address)
        tx = w3.eth.get_transaction(receipt["transactionHash"])
        block = w3.eth.get_block(receipt["blockNumber"])
        actual_fee = balance_before - balance_after  # no principal/other transfers in this isolated action
        reported_fee = receipt["gasUsed"] * receipt["effectiveGasPrice"]
        expected_price = min(tx["maxFeePerGas"], block["baseFeePerGas"] + tx["maxPriorityFeePerGas"])
        contradiction = (actual_fee != reported_fee or receipt["effectiveGasPrice"] != expected_price)
        return {
            "classification": "BLOCKED: fee evidence contradiction" if contradiction else "no discrepancy observed; review still required",
            "contradiction": contradiction, "chainId": 31337,
            "deploymentGasUsed": deployment["gasUsed"], "status": receipt["status"],
            "gasUsed": receipt["gasUsed"], "signedMaxFeePerGas": tx["maxFeePerGas"],
            "signedMaxPriorityFeePerGas": tx["maxPriorityFeePerGas"],
            "blockBaseFeePerGas": block["baseFeePerGas"],
            "receiptEffectiveGasPrice": receipt["effectiveGasPrice"],
            "expectedEIP1559Price": expected_price, "actualBalanceDebit": actual_fee,
            "reportedFee": reported_fee, "worstCaseReservation": RESERVATION,
            "actualFeeWithinReservation": actual_fee <= RESERVATION,
            "elapsedSeconds": round(time.monotonic() - started, 3),
        }
    finally:
        stop(node)
        if node.poll() is None:
            raise RuntimeError("diagnostic child cleanup failed")


def main():
    try:
        evidence = probe()
    except Exception:
        # Do not serialize RPC exception bodies, which may contain raw transactions.
        print(json.dumps({"classification": "inconclusive diagnostic failure"}))
        return 3
    evidence["childrenStopped"] = True
    print(json.dumps(evidence, sort_keys=True))
    return 2 if evidence["contradiction"] else 0


if __name__ == "__main__":
    sys.exit(main())
