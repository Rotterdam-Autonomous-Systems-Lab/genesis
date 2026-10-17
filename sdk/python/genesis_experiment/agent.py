"""Two separate process entry points. Each creates and retains only its own signer."""
import json
import os
import secrets
import sys
import time
from pathlib import Path

from eth_account import Account
from web3 import Web3

from .chain import Chain
from .protocol import (Inconclusive, PRICE, Rejected, SERVICE, check_terms, exact,
                       hex_value, integer, normalize, read, tuple_for, wait, wire, write)


def agreement_envelope(signing, message, sig_a, sig_b=None):
    result = {"primaryType": "Agreement", "domain": signing.domain, "message": message,
              "requesterSignature": sig_a}
    if sig_b is not None:
        result["providerSignature"] = sig_b
    return result


def open_agreement(signing, envelope, requester, provider, now, dual=False):
    fields = ["primaryType", "domain", "message", "requesterSignature"]
    if dual:
        fields.append("providerSignature")
    exact(envelope, fields)
    if envelope["primaryType"] != "Agreement" or envelope["domain"] != signing.domain:
        raise Rejected("agreement domain")
    terms = check_terms(envelope["message"], requester, provider, now)
    signing.verify("Agreement", envelope["message"], envelope["requesterSignature"], requester)
    if dual:
        signing.verify("Agreement", envelope["message"], envelope["providerSignature"], provider)
    return terms


def result_acceptance(chain, result_envelope, terms, agreement_id, nonce):
    """Requester-only decision path: recompute before constructing any Acceptance."""
    result = chain.signing.open(result_envelope, "Result", terms["provider"])
    if result["agreementId"] != agreement_id:
        raise Rejected("result agreement")
    # Provider uses sum(); requester deliberately uses separate direct arithmetic.
    expected = terms["x"] + terms["y"]
    if result["value"] != expected:
        raise Rejected("invalid computation")
    return wire("Acceptance", agreementId=agreement_id,
                resultDigest=chain.signing.digest("Result", result_envelope["message"]),
                authorizationNonce=nonce, runId=chain.manifest["runId"])


def provider(chain, folder, config, end):
    s = chain.signing
    requester = wait(folder / "requester-ready.json", end)["address"]
    requester = Web3.to_checksum_address(hex_value(requester, 20))
    advertisement = wire("Advertisement", provider=chain.account.address, serviceId=SERVICE,
                         price=PRICE, expiresAt=chain.w3.eth.get_block("latest")["timestamp"] + 60,
                         runId=s.run_id)
    write(folder / "discovery.json", {"offers": [s.envelope(chain.account, "Advertisement", advertisement)]})
    proposal = wait(folder / "proposal.json", end)
    terms = open_agreement(s, proposal, requester, chain.account.address,
                           chain.w3.eth.get_block("latest")["timestamp"])
    agreement_id = s.digest("Agreement", proposal["message"])
    signed = agreement_envelope(s, proposal["message"], proposal["requesterSignature"],
                                s.sign(chain.account, "Agreement", proposal["message"]))
    write(folder / "agreement.json", signed)
    request = wait(folder / "compute.json", end)
    exact(request, ("agreementId",))
    if request["agreementId"] != agreement_id:
        raise Rejected("unknown request")
    chain.preflight()
    record = chain.record(agreement_id)
    if record[2] != 1 or tuple(Web3.to_hex(v) if isinstance(v, bytes) else v for v in record[0]) != tuple_for("Agreement", proposal["message"]):
        raise Rejected("unfunded/altered computation")
    if config["scenario"] == "provider_killed":
        wait(folder / "never.json", end)  # harness terminates this process after funding
    value = sum((terms["x"], terms["y"]))
    if config["scenario"] == "invalid_result":
        value += 1  # explicit adversarial fixture, never selected by a wire message
    result = wire("Result", agreementId=agreement_id, value=value, runId=s.run_id)
    evidence = s.envelope(chain.account, "Result", result)
    write(folder / "result.json", evidence)
    try:
        acceptance = wait(folder / "acceptance.json", min(end, time.monotonic() + 3))
    except Inconclusive:
        return {"outcome": "no_acceptance", "agreementId": agreement_id}
    a = s.open(acceptance, "Acceptance", requester)
    if (a["agreementId"] != agreement_id or a["authorizationNonce"] != record[1]
            or a["resultDigest"] != s.digest("Result", result)):
        raise Rejected("acceptance binding")
    receipt = chain.transact(chain.contract.functions.settle(agreement_id, tuple_for("Result", result),
        evidence["signature"], tuple_for("Acceptance", acceptance["message"]), acceptance["signature"]),
        "Settled", {"agreementId": agreement_id, "resultDigest": a["resultDigest"], "price": PRICE})
    if chain.record(agreement_id)[2] != 2 or chain.contract.functions.credits(chain.account.address).call() != PRICE:
        raise Inconclusive("settlement state")
    chain.transact(chain.contract.functions.withdraw(), "Withdrawn", {"account": chain.account.address, "amount": PRICE})
    if chain.contract.functions.credits(chain.account.address).call() != 0:
        raise Inconclusive("withdrawal state")
    return {"outcome": "settled", "agreementId": agreement_id, "settlementTx": Web3.to_hex(receipt["transactionHash"])}


def discover(chain, discovery, provider_address):
    exact(discovery, ("offers",))
    offers = discovery["offers"]
    if not isinstance(offers, list) or not 1 <= len(offers) <= 16:
        raise Rejected("discovery bound")
    selected = None
    for offer in offers:
        a = chain.signing.open(offer, "Advertisement", provider_address)
        if (a["provider"] != provider_address or a["serviceId"] != SERVICE or a["price"] != PRICE
                or chain.w3.eth.get_block("latest")["timestamp"] >= a["expiresAt"]):
            raise Rejected("offer policy")
        selected = a
    return selected


def requester(chain, folder, config, end):
    s = chain.signing
    provider_address = Web3.to_checksum_address(hex_value(wait(folder / "provider-ready.json", end)["address"], 20))
    discover(chain, wait(folder / "discovery.json", end), provider_address)
    now = chain.w3.eth.get_block("latest")["timestamp"]
    message = wire("Agreement", requester=chain.account.address, provider=provider_address,
        serviceId=SERVICE, x=integer(config["x"], 64), y=integer(config["y"], 64), price=PRICE,
        fundingDeadline=now + 60, settlementDeadline=now + 120,
        salt="0x" + secrets.token_hex(32), runId=s.run_id)
    write(folder / "proposal.json", agreement_envelope(s, message, s.sign(chain.account, "Agreement", message)))
    agreed = wait(folder / "agreement.json", end)
    if agreed["message"] != message:
        raise Rejected("counterparty altered terms")
    terms = open_agreement(s, agreed, chain.account.address, provider_address,
                           chain.w3.eth.get_block("latest")["timestamp"], dual=True)
    agreement_id = s.digest("Agreement", message)
    auth = wire("Authorization", requester=chain.account.address, provider=provider_address,
                agreementId=agreement_id, nonce=0, maxAmount=2 * PRICE,
                validUntil=terms["fundingDeadline"], runId=s.run_id)
    chain.transact(chain.contract.functions.fund(tuple_for("Agreement", message), agreed["requesterSignature"],
        agreed["providerSignature"], tuple_for("Authorization", auth), s.sign(chain.account, "Authorization", auth)),
        "Funded", {"agreementId": agreement_id, "requester": chain.account.address,
                   "provider": provider_address, "nonce": 0, "price": PRICE}, value=PRICE)
    record = chain.record(agreement_id)
    if (record[2] != 1 or tuple(Web3.to_hex(v) if isinstance(v, bytes) else v for v in record[0]) != tuple_for("Agreement", message) or record[1] != 0
            or chain.contract.functions.nonceStatus(chain.account.address, 0).call() != 1):
        raise Inconclusive("funding state")
    write(folder / "funded.json", {"agreementId": agreement_id, "deadline": str(terms["settlementDeadline"])})
    write(folder / "compute.json", {"agreementId": agreement_id})
    accepted = False
    reason = "requester_refusal"
    verifier_ms = "0"
    try:
        result = wait(folder / "result.json", min(end, time.monotonic() + 3))
        verify_started = time.monotonic()
        acceptance = result_acceptance(chain, result, terms, agreement_id, 0)
        verifier_ms = str(round((time.monotonic() - verify_started) * 1000, 3))
        if config["scenario"] != "requester_refusal":
            chain.preflight()
            if chain.w3.eth.get_block("latest")["timestamp"] >= terms["settlementDeadline"]:
                raise Rejected("late result")
            write(folder / "acceptance.json", s.envelope(chain.account, "Acceptance", acceptance))
            accepted = True
    except Rejected:
        reason = "invalid_result"
    except Inconclusive:
        reason = "provider_timeout"
    if accepted:
        report = wait(folder / "provider-report.json", end)
        if report["outcome"] != "settled" or chain.record(agreement_id)[2] != 2:
            raise Inconclusive("provider settlement missing")
        # Independently reconcile B's public receipts, not only its status string.
        for r in report["receipts"]:
            receipt = chain.w3.eth.get_transaction_receipt(r["hash"])
            if receipt["status"] != 1 or Web3.to_hex(receipt["blockHash"]) != r["blockHash"]:
                raise Inconclusive("provider receipt mismatch")
            if chain.w3.eth.get_block(receipt["blockNumber"])["hash"] != receipt["blockHash"]:
                raise Inconclusive("provider reorg")
        return {"outcome": "settled", "agreementId": agreement_id, "acceptanceSigned": True,
                "verifierMs": verifier_ms}
    write(folder / "refund-wait.json", {"deadline": str(terms["settlementDeadline"]), "reason": reason})
    # Only the trusted test harness advances chain time. An agent cannot cancel early.
    while chain.w3.eth.get_block("latest")["timestamp"] < terms["settlementDeadline"]:
        if time.monotonic() >= end:
            raise Inconclusive("refund deadline not reached")
        time.sleep(0.025)
    chain.transact(chain.contract.functions.refund(agreement_id), "Refunded", {"agreementId": agreement_id, "price": PRICE})
    if chain.record(agreement_id)[2] != 3 or chain.contract.functions.credits(chain.account.address).call() != PRICE:
        raise Inconclusive("refund state")
    chain.transact(chain.contract.functions.withdraw(), "Withdrawn", {"account": chain.account.address, "amount": PRICE})
    return {"outcome": "refunded", "agreementId": agreement_id, "acceptanceSigned": False,
            "reason": reason, "verifierMs": verifier_ms}


def main():
    role, directory = sys.argv[1:]
    if role not in ("requester", "provider"):
        raise SystemExit(2)
    folder = Path(directory)
    account = Account.create()  # never supplied by harness, argv, environment, or the other agent
    write(folder / (role + "-ready.json"), {"address": account.address, "pid": str(os.getpid())})
    try:
        end = time.monotonic() + 45
        config = wait(folder / "config.json", end)
        artifact = json.loads(Path(config["artifact"]).read_text())
        chain = Chain(config["rpc"], account, artifact, config["manifest"],
                      journal=folder / (role + "-transactions.jsonl"))
        wait(folder / "go.json", end)
        result = {"requester": requester, "provider": provider}[role](chain, folder, config, end)
        result.update({"address": account.address, "pid": str(os.getpid()), "receipts": chain.evidence()})
        write(folder / (role + "-report.json"), result)
    except Exception as exc:
        # Never serialize exceptions/locals: signing library errors may contain raw transactions.
        write(folder / (role + "-error.json"), {"error": type(exc).__name__, "reason": str(exc) if isinstance(exc, (Inconclusive, Rejected)) else "unavailable", "outcome": "inconclusive"})
        raise SystemExit(1)


if __name__ == "__main__":
    main()
