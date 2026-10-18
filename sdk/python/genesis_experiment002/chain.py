"""Operator-authorized fee policy, canonical reconciliation, no external destinations."""

import time
from functools import wraps
import requests
from web3 import Web3
from web3.exceptions import TransactionNotFound
from genesis_experiment.chain import Chain as EvidenceChain, connect
from genesis_experiment.protocol import Inconclusive, Rejected
from .protocol import Signing
from .limits import bound_rpc, check_deadline

GAS = 2_000_000
FEE = 3_000_000_000
PRIORITY = 1_000_000_000
RESERVATION = GAS * FEE
ATTEMPTS = {"deployer": 1, "requester": 8, "provider": 8}
METHODS = {
    "requester": {"fund", "revokeUnused", "refund", "withdraw"},
    "provider": {"claim", "withdraw"},
    "deployer": {"constructor"},
}


class Budget:
    def __init__(self, role):
        if role not in ATTEMPTS:
            raise Rejected("role")
        self.role = role
        self.used = 0
        self.reserved = 0

    def charge(
        self, method, value, principal, balance, gas=GAS, fee=FEE, priority=PRIORITY
    ):
        if any(
            type(x) is not int or x < 0
            for x in (value, principal, balance, gas, fee, priority)
        ):
            raise Rejected("budget integers")
        closing = (
            (2 if self.role == "requester" else 1)
            if method not in ("refund", "withdraw", "constructor")
            else 0
        )
        if (
            method not in METHODS[self.role]
            or gas == 0
            or gas > GAS
            or fee > FEE
            or priority > PRIORITY
            or priority > fee
            or self.used >= ATTEMPTS[self.role] - closing
            or self.reserved + RESERVATION > ATTEMPTS[self.role] * RESERVATION
            or value != (principal if method == "fund" else 0)
            or not 0 < principal <= 10**15
            or balance < value + gas * fee
        ):
            raise Rejected("operator budget rejected before signing")
        self.used += 1
        self.reserved += RESERVATION


def fail_closed(method):
    @wraps(method)
    def checked(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (
            Inconclusive,
            requests.RequestException,
            OSError,
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            self.halted = True
            raise Inconclusive(
                "unavailable or contradictory run evidence; signer stopped"
            ) from None

    return checked


class Chain(EvidenceChain):
    def __init__(
        self, url, account, artifact, role, principal, manifest=None, deadline=None
    ):
        # Reuse read-only transport/evidence code, never Experiment 001's signer/schema.
        self.halted = False
        self.deadline = (
            deadline
            if deadline is not None
            else (manifest or {}).get("deadlineMonotonic", time.monotonic() + 120)
        )
        check_deadline(self.deadline)
        if self.deadline > time.monotonic() + 120:
            raise Inconclusive("run deadline exceeds fixed budget")
        self.w3 = connect(url)
        bound_rpc(self.w3, self.deadline)
        check_deadline(self.deadline)
        self.account = account
        self.artifact = artifact
        self.role = role
        self.principal = principal
        self.budget = Budget(role)
        self.receipts = []
        self.intents = []
        self.observations = {}
        self.submissions = 0
        self.pending_hash = None
        self.funding_intent = None
        self.manifest = manifest
        self.contract = None
        if manifest:
            self.contract = self.w3.eth.contract(
                address=manifest["contract"], abi=artifact["abi"]
            )
            self.signing = Signing(
                manifest["contract"].lower(), manifest["runId"], self.deadline
            )
            self.preflight()

    @fail_closed
    def preflight(self):
        check_deadline(self.deadline)
        if self.halted:
            raise Inconclusive("evidence latch stopped signer")
        super().preflight()
        check_deadline(self.deadline)

    @fail_closed
    def transact(self, function, event=None, expected=None, value=0):
        if self.halted or self.pending_hash is not None:
            raise Inconclusive("unresolved prior transaction")
        self.preflight()
        method = getattr(function, "fn_name", "constructor")
        if method != "constructor" and function.address != self.contract.address:
            raise Rejected("wrong target")
        if self.w3.eth.get_block("latest")["baseFeePerGas"] > FEE:
            raise Rejected("base fee exceeds fixed cap")
        # One exact funding intent per run; retries cannot introduce new principal.
        if method == "fund":
            intent = function._encode_transaction_data()
            if self.funding_intent is not None and intent != self.funding_intent:
                raise Rejected(
                    "different funding intent exceeds single-principal policy"
                )
            self.funding_intent = intent
        self.budget.charge(
            method, value, self.principal, self.w3.eth.get_balance(self.account.address)
        )
        self.submissions = self.budget.used
        nonce = self.w3.eth.get_transaction_count(self.account.address, "pending")
        data = (
            function.data_in_transaction
            if method == "constructor"
            else function._encode_transaction_data()
        )
        tx = function.build_transaction(
            {
                "from": self.account.address,
                "nonce": nonce,
                "chainId": 31337,
                "value": value,
                "gas": GAS,
                "maxFeePerGas": FEE,
                "maxPriorityFeePerGas": PRIORITY,
                "type": 2,
            }
        )
        if any(
            k in tx
            for k in (
                "gasPrice",
                "accessList",
                "maxFeePerBlobGas",
                "blobVersionedHashes",
            )
        ):
            raise Rejected("unsupported transaction form")
        allowed = {
            "from",
            "nonce",
            "chainId",
            "value",
            "gas",
            "maxFeePerGas",
            "maxPriorityFeePerGas",
            "type",
            "data",
            "to",
        }
        if (
            set(tx) - allowed
            or tx["chainId"] != 31337
            or tx["value"] != value
            or tx["gas"] != GAS
            or tx["maxFeePerGas"] != FEE
            or tx["maxPriorityFeePerGas"] != PRIORITY
            or tx["type"] != 2
            or tx["from"] != self.account.address
            or tx["nonce"] != nonce
            or tx["data"] != data
            or (method == "constructor" and tx.get("to") not in (None, b"", ""))
            or (method != "constructor" and tx["to"] != self.contract.address)
        ):
            raise Rejected("final transaction differs from operator policy")
        check_deadline(self.deadline)
        signed = self.account.sign_transaction(tx)
        digest = Web3.keccak(signed.raw_transaction)
        self.pending_hash = (
            digest  # before possibly ambiguous broadcast; never persist raw bytes
        )
        self.intents.append(
            {
                "hash": Web3.to_hex(digest),
                "method": method,
                "nonce": nonce,
                "value": str(value),
                "chainTimestamp": self.w3.eth.get_block("latest")["timestamp"],
                "monotonicSeconds": time.monotonic(),
                "sender": self.account.address,
                "target": tx.get("to") or None,
                "dataHash": Web3.to_hex(Web3.keccak(hexstr=tx["data"])),
                "gas": GAS,
                "maxFeePerGas": FEE,
                "maxPriorityFeePerGas": PRIORITY,
            }
        )
        check_deadline(self.deadline)
        try:
            returned = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            if returned != digest:
                raise Inconclusive("wrong broadcast hash")
        except (requests.RequestException, OSError):
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
            raise Inconclusive("unknown broadcast outcome; signer stopped")
        self.canonical_receipt(receipt, digest)
        if receipt["gasUsed"] > GAS or receipt["effectiveGasPrice"] > FEE:
            raise Inconclusive("canonical fee exceeds policy")
        self.receipts.append(receipt)
        self.preflight()
        if receipt["status"] != 1:
            self.pending_hash = None
            raise Rejected("canonical transaction reverted; reservation retained")
        if event:
            self.check_event(receipt, event, expected or {})
        self.pending_hash = None
        return receipt

    @fail_closed
    def canonical_receipt(self, receipt, expected_hash):
        check_deadline(self.deadline)
        super().canonical_receipt(receipt, expected_hash)
        # Closed fixture: exactly one transaction per block, no top-ups after setup.
        # Reconcile principal flows, not just zero-value diagnostic transactions.
        try:
            tx = self.w3.eth.get_transaction(expected_hash)
            block = self.w3.eth.get_block(receipt["blockNumber"])
            parent = self.w3.eth.get_block(block["number"] - 1)
            if block["parentHash"] != parent["hash"] or len(block["transactions"]) != 1:
                raise Inconclusive("non-isolated fee evidence")
            current = self.w3.eth.get_transaction_receipt(expected_hash)
            fields = (
                "transactionHash",
                "blockHash",
                "blockNumber",
                "transactionIndex",
                "status",
                "logs",
                "gasUsed",
                "effectiveGasPrice",
                "from",
                "to",
                "contractAddress",
                "cumulativeGasUsed",
            )
            if any(current[field] != receipt[field] for field in fields):
                raise Inconclusive("current receipt changed")
            if (
                tx["hash"] != expected_hash
                or tx["blockNumber"] != receipt["blockNumber"]
                or tx["transactionIndex"] != receipt["transactionIndex"]
                or receipt["transactionIndex"] != 0
                or tx["from"] != receipt["from"]
                or tx["to"] != receipt["to"]
            ):
                raise Inconclusive("transaction identity/inclusion mismatch")
            for intent in self.intents:
                if intent["hash"] == Web3.to_hex(expected_hash):
                    if (
                        tx["from"] != intent["sender"]
                        or tx["to"] != intent["target"]
                        or tx["nonce"] != intent["nonce"]
                        or tx["value"] != int(intent["value"])
                        or tx["gas"] != intent["gas"]
                        or tx["maxFeePerGas"] != intent["maxFeePerGas"]
                        or tx["maxPriorityFeePerGas"] != intent["maxPriorityFeePerGas"]
                        or Web3.to_hex(Web3.keccak(tx["input"])) != intent["dataHash"]
                    ):
                        raise Inconclusive(
                            "observed transaction differs from signed intent"
                        )
            maximum, priority = tx["maxFeePerGas"], tx["maxPriorityFeePerGas"]
            expected = min(maximum, block["baseFeePerGas"] + priority)
            block_receipts = self.w3.eth.get_block_receipts(block["number"])
            if (
                tx["type"] != 2
                or tx["chainId"] != 31337
                or not 0 < tx["gas"] <= GAS
                or not 0 <= priority <= min(PRIORITY, maximum)
                or maximum > FEE
                or block["baseFeePerGas"] > maximum
                or not 0 < receipt["gasUsed"] <= tx["gas"]
                or receipt["effectiveGasPrice"] != expected
                or tx["gasPrice"] != expected
                or tx["blockHash"] != block["hash"]
                or len(block_receipts) != 1
                or block_receipts[0]["transactionHash"] != expected_hash
                or block_receipts[0]["effectiveGasPrice"] != expected
            ):
                raise Inconclusive("canonical fee fields disagree")
            if any(block_receipts[0][field] != receipt[field] for field in fields):
                raise Inconclusive("block receipt changed")
            incoming = 0
            if self.contract and receipt["status"] == 1:
                topic = Web3.keccak(text="Withdrawn(address,uint256)")
                for log in receipt["logs"]:
                    if (
                        log["address"] == self.contract.address
                        and log["topics"][0] == topic
                    ):
                        if len(log["topics"]) != 2 or len(log["data"]) != 32:
                            raise Inconclusive("malformed withdrawal evidence")
                        owner = Web3.to_checksum_address(log["topics"][1][-20:])
                        if owner != tx["from"]:
                            raise Inconclusive("unexpected withdrawal owner")
                        incoming += int.from_bytes(log["data"], "big")
            before = self.w3.eth.get_balance(tx["from"], parent["number"])
            after = self.w3.eth.get_balance(tx["from"], block["number"])
            outgoing = tx["value"] if receipt["status"] == 1 else 0
            charged = before - after - outgoing + incoming
            if (
                charged != receipt["gasUsed"] * expected
                or not 0 <= charged <= RESERVATION
            ):
                raise Inconclusive("wallet/principal/receipt fee contradiction")
            self.observations[Web3.to_hex(expected_hash)] = {
                "hash": Web3.to_hex(expected_hash),
                "blockHash": Web3.to_hex(receipt["blockHash"]),
                "block": str(receipt["blockNumber"]),
                "timestamp": str(block["timestamp"]),
                "gasUsed": str(receipt["gasUsed"]),
                "status": str(receipt["status"]),
                "effectiveGasPrice": str(receipt["effectiveGasPrice"]),
                "fee": str(charged),
            }
        except (KeyError, TypeError, ValueError, TransactionNotFound) as exc:
            raise Inconclusive("fee evidence unavailable/malformed") from exc

    @fail_closed
    def record(self, agreement_id):
        check_deadline(self.deadline)
        anchor = self.w3.eth.get_block("latest")
        first = self.contract.functions.getRecord(agreement_id).call(
            block_identifier=anchor["number"]
        )
        second = self.contract.functions.getRecord(agreement_id).call(
            block_identifier=anchor["number"]
        )
        for receipt in self.receipts:
            self.canonical_receipt(receipt, receipt["transactionHash"])
            for name, state in (("Claimed", 2), ("Refunded", 3)):
                topic = Web3.keccak(
                    text=(
                        "Claimed(bytes32,address,uint256,uint256,uint256)"
                        if state == 2
                        else "Refunded(bytes32,address,uint256,uint256)"
                    )
                )
                for log in receipt["logs"]:
                    if (
                        log["address"] == self.contract.address
                        and log["topics"][0] == topic
                    ):
                        args = getattr(self.contract.events, name)().process_log(log)[
                            "args"
                        ]
                        if Web3.to_hex(args["agreementId"]) == Web3.to_hex(
                            Web3.to_bytes(hexstr=agreement_id)
                            if isinstance(agreement_id, str)
                            else agreement_id
                        ):
                            if first[2] != state or first[3] != (
                                args["value"] if state == 2 else 0
                            ):
                                raise Inconclusive(
                                    "record contradicts observed terminal event"
                                )
        if (
            first != second
            or self.w3.eth.get_block(anchor["number"])["hash"] != anchor["hash"]
        ):
            raise Inconclusive("contradictory pinned record")
        return first

    def evidence(self):
        result = super().evidence()
        for item, receipt in zip(result, self.receipts):
            item["effectiveGasPrice"] = str(receipt["effectiveGasPrice"])
            item["fee"] = str(receipt["gasUsed"] * receipt["effectiveGasPrice"])
        return result
