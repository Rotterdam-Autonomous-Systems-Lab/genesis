"""Literal-loopback RPC, locally signed bounded transactions, canonical receipts."""
import os
import json
import time
from urllib.parse import urlsplit

import requests
from eth_account import Account
from web3 import Web3
from web3.exceptions import TransactionNotFound, BlockNotFound

from .protocol import Inconclusive, Rejected, Signing, hex_value


class LocalSession(requests.Session):
    def __init__(self):
        super().__init__()
        self.trust_env = False

    def request(self, method, url, **kwargs):
        kwargs["allow_redirects"] = False
        result = super().request(method, url, **kwargs)
        if 300 <= result.status_code < 400:
            raise Inconclusive("RPC redirect refused")
        return result


def connect(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or not parsed.port
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment):
        raise Rejected("literal loopback RPC required")
    if any(os.environ.get(name) for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")):
        raise Rejected("proxy configuration refused")
    w3 = Web3(Web3.HTTPProvider(url, session=LocalSession(), request_kwargs={"timeout": 1},
                              exception_retry_configuration=None))
    if w3.eth.chain_id != 31337:
        raise Rejected("wrong chain")
    return w3


class Chain:
    def __init__(self, url, account, artifact, manifest=None, journal=None):
        self.w3 = connect(url)
        self.account = account
        self.artifact = artifact
        self.receipts = []
        self.submissions = 0
        self.contract = None
        self.manifest = manifest
        self.journal = journal
        if manifest:
            self.contract = self.w3.eth.contract(address=manifest["contract"], abi=artifact["abi"])
            self.signing = Signing(manifest["contract"], manifest["runId"])
            self.preflight()

    def preflight(self):
        if self.w3.eth.chain_id != 31337:
            raise Inconclusive("chain changed")
        if self.manifest:
            code = self.w3.eth.get_code(self.manifest["contract"])
            if (not code or Web3.to_hex(Web3.keccak(code)) != self.manifest["codeHash"]
                    or Web3.to_hex(self.contract.functions.runId().call()) != self.manifest["runId"]):
                raise Inconclusive("deployment changed")
        for receipt in self.receipts:
            try:
                if self.w3.eth.get_block(receipt["blockNumber"])["hash"] != receipt["blockHash"]:
                    raise Inconclusive("canonical receipt replaced")
                current = self.w3.eth.get_transaction_receipt(receipt["transactionHash"])
                if current["blockHash"] != receipt["blockHash"]:
                    raise Inconclusive("receipt changed")
            except (TransactionNotFound, BlockNotFound) as exc:
                raise Inconclusive("receipt disappeared") from exc

    def transact(self, function, event=None, expected=None, value=0):
        self.preflight()
        if self.submissions >= 8:
            raise Rejected("transaction budget")
        self.submissions += 1
        # Sequential calls, no automatically allocated fresh authorization/transaction on failure.
        tx = function.build_transaction({"from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(self.account.address, "pending"),
            "chainId": 31337, "value": value, "gas": 2000000,
            "maxFeePerGas": 3000000000, "maxPriorityFeePerGas": 1000000000})
        signed = self.account.sign_transaction(tx)
        digest = Web3.keccak(signed.raw_transaction)
        if self.journal:
            # Journal public economic intent before ambiguous network delivery.
            # Never persist raw transactions, signatures, or private signing material.
            with self.journal.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"hash": Web3.to_hex(digest), "nonce": str(tx["nonce"]),
                    "value": str(value), "event": event, "expected": expected or {}}) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        try:
            returned = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            if returned != digest:
                raise Inconclusive("RPC returned wrong transaction hash")
        except (requests.RequestException, OSError):
            # A dropped send response is ambiguous. Reconcile this exact hash; never
            # re-fund with a fresh authorization. No rebroadcast needed on automining Anvil.
            pass
        end = time.monotonic() + 4
        receipt = None
        while time.monotonic() < end:
            try:
                receipt = self.w3.eth.get_transaction_receipt(digest)
                break
            except (TransactionNotFound, requests.RequestException, OSError):
                time.sleep(0.05)
        if receipt is None:
            raise Inconclusive("transaction outcome unknown")
        self.receipts.append(receipt)
        self.preflight()
        if receipt["status"] != 1:
            raise Rejected("transaction reverted")
        if event:
            logs = getattr(self.contract.events, event)().process_receipt(receipt)
            if len(logs) != 1 or logs[0]["address"] != self.contract.address:
                raise Inconclusive("missing escrow event")
            for key, val in (expected or {}).items():
                actual = logs[0]["args"][key]
                if isinstance(actual, bytes):
                    actual = Web3.to_hex(actual)
                if actual != val:
                    raise Inconclusive("unexpected event fields")
        return receipt

    def record(self, agreement_id):
        return self.contract.functions.getAgreement(agreement_id).call()

    def evidence(self):
        self.preflight()
        return [{"hash": Web3.to_hex(r["transactionHash"]), "blockHash": Web3.to_hex(r["blockHash"]),
                 "block": str(r["blockNumber"]), "timestamp": str(self.w3.eth.get_block(r["blockNumber"])["timestamp"]), "gasUsed": str(r["gasUsed"]), "status": str(r["status"])}
                for r in self.receipts]
