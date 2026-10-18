"""Strict diagnostic oracle. Contradictory fees always reject; no normalization."""
import re

MAX_GAS = 2_000_000
MAX_FEE = 3_000_000_000
MAX_PRIORITY = 1_000_000_000


class EvidenceContradiction(ValueError):
    """Required RPC/execution/accounting evidence disagrees."""


def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r"0x(?:0|[1-9a-f][0-9a-f]*)", value):
        raise EvidenceContradiction("noncanonical RPC quantity")
    result = int(value, 16)
    if result >= 2**256:
        raise EvidenceContradiction("quantity width")
    return result


def measurements(evidence):
    """Only isolated zero-value diagnostic calls; never a general wallet-delta rule."""
    tx, receipt, block = (evidence[k] for k in ("transaction", "receipt", "block"))
    gas_limit, maximum, priority, base, used, reported = map(quantity, (
        tx["gas"], tx["maxFeePerGas"], tx["maxPriorityFeePerGas"], block["baseFeePerGas"],
        receipt["gasUsed"], receipt["effectiveGasPrice"],
    ))
    if (quantity(tx["type"]) != 2 or quantity(tx["value"]) != 0
            or not 0 < gas_limit <= MAX_GAS or not 0 <= priority <= min(MAX_PRIORITY, maximum)
            or maximum > MAX_FEE or used > gas_limit or base > maximum):
        raise EvidenceContradiction("transaction outside accepted diagnostic fee policy")
    expected = base + min(priority, maximum - base)  # EIP-1559 reference algorithm
    before, after = map(quantity, (evidence["balanceBefore"], evidence["balanceAfter"]))
    return {
        "expectedPrice": expected, "reportedPrice": reported, "reportedFee": used * reported,
        "expectedFee": used * expected, "actualDebit": before - after,
        "maxReservation": gas_limit * maximum,
        "receiptOverstatement": used * reported - (before - after),
    }


def require_reconciled(evidence):
    """Fail closed on a discrepancy. Never substitute expectedPrice for receipt data."""
    values = measurements(evidence)
    tx, receipt, block = (evidence[k] for k in ("transaction", "receipt", "block"))
    if (tx["hash"] != receipt["transactionHash"] or tx["blockHash"] != block["hash"]
            or receipt["blockHash"] != block["hash"]
            or receipt["blockNumber"] != block["number"]
            or tx["blockNumber"] != block["number"]
            or tx["hash"] not in block["transactions"]
            or evidence["parentHash"] != block["parentHash"]
            or quantity(evidence["parentNumber"]) + 1 != quantity(block["number"])
            or quantity(receipt["status"]) not in (0, 1)
            or values["reportedPrice"] != values["expectedPrice"]
            or values["reportedFee"] != values["actualDebit"]
            or not 0 <= values["actualDebit"] <= values["maxReservation"]
            or quantity(tx["gasPrice"]) != values["expectedPrice"]
            or quantity(evidence["blockReceiptEffectiveGasPrice"]) != values["expectedPrice"]):
        raise EvidenceContradiction("canonical fee evidence does not reconcile")
    if quantity(receipt["status"]) == 1:
        if (quantity(evidence["witnessGasPrice"]) != values["expectedPrice"]
                or quantity(evidence["witnessBaseFee"]) != quantity(block["baseFeePerGas"])):
            raise EvidenceContradiction("execution witness differs")
    return values
