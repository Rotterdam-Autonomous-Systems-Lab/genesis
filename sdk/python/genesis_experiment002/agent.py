"""Separate-process agents. Private keys are generated here and never exported."""

import json
import hashlib
import os
import secrets
import sys
import time
from pathlib import Path
from eth_account import Account
from web3 import Web3
from genesis_experiment.protocol import (
    Inconclusive as ChainInconclusive,
    Rejected as ChainRejected,
)
from .chain import Chain
from .protocol import (
    Inconclusive,
    Rejected,
    SERVICE,
    POLICY,
    PRICE,
    Signing,
    check_terms,
    normalize,
    tuple_for,
    wait,
    wire,
    write,
    read,
)


def observe(chain, terms, agreement_id, state):
    record = chain.record(agreement_id)
    if (
        tuple(Web3.to_hex(v) if isinstance(v, bytes) else v for v in record[0])
        != tuple_for("Terms", terms)
        or record[1] != 0
        or record[2] != state
        or chain.contract.functions.nonceStatus(
            Web3.to_checksum_address(terms["requester"]), 0
        ).call()
        != 1
    ):
        raise Inconclusive("record/nonce evidence mismatch")
    return record


def run(role, folder):
    end = time.monotonic() + 120
    account = Account.create()  # only this process can access its key
    write(
        folder / (role + "-ready.json"),
        {"address": account.address, "pid": os.getpid()},
    )
    config = wait(
        folder / "operator.json", end
    )  # trusted supervisor, outside peer transport
    artifact_bytes = Path(config["artifact"]).read_bytes()
    artifact = json.loads(artifact_bytes)
    manifest = config["manifest"]
    if (
        manifest["artifactHash"] != hashlib.sha256(artifact_bytes).hexdigest()
        or manifest["principal"] != PRICE
        or manifest["gas"] != 2_000_000
        or manifest["maxFeePerGas"] != 3_000_000_000
        or manifest["maxPriorityFeePerGas"] != 1_000_000_000
        or manifest["attempts"] != {"deployer": 1, "requester": 8, "provider": 8}
        or manifest["wallSeconds"] != 120
        or manifest["cleanupSeconds"] != 15
        or manifest["chainId"] != 31337
        or manifest["rpcTimeout"] != 1
        or manifest["nodeCommit"] != "b272ce3366987406406e9eb1b82596653a3ad628"
        or manifest["hardfork"] != "cancun"
        or manifest["compilerMetadataHash"]
        != hashlib.sha256(artifact["rawMetadata"].encode()).hexdigest()
    ):
        raise Rejected("operator policy mismatch")
    own = config["roles"][role]
    if own["address"] != account.address or own["pid"] != os.getpid():
        raise Rejected("operator identity mismatch")
    chain = Chain(config["rpc"], account, artifact, role, PRICE, manifest)
    node_info = chain.w3.provider.make_request("anvil_nodeInfo", [])["result"]
    if (
        node_info["hardFork"].lower() != "cancun"
        or node_info["forkConfig"]["forkUrl"] is not None
    ):
        raise Rejected("unexpected node environment")
    signing = chain.signing
    a, b = (config["roles"][r]["address"] for r in ("requester", "provider"))
    now = lambda: chain.w3.eth.get_block("latest")["timestamp"]
    scenario = config["scenario"]
    if role == "provider":
        ad = wire(
            "Advertisement",
            provider=b,
            serviceId=SERVICE,
            policyId=POLICY,
            price=PRICE,
            offerExpiresAt=now() + 120,
            runId=manifest["runId"],
        )
        write(
            folder / "advertisement.json",
            signing.envelope(
                "advertisement",
                ad,
                {"provider": signing.sign(account, "Advertisement", ad)},
            ),
        )
        proposal = wait(folder / "proposal.json", end)
        signing.open(proposal, "termsProposal", {"requester": a})
        terms = proposal["message"]
        parsed = check_terms(terms, a, b, now())
        if now() >= int(ad["offerExpiresAt"]) or parsed["price"] != PRICE:
            raise Rejected("offer mismatch/expired")
        write(
            folder / "terms.json",
            signing.envelope(
                "terms",
                terms,
                {
                    **proposal["signatures"],
                    "provider": signing.sign(account, "Terms", terms),
                },
            ),
        )
        funding = wait(folder / "funded.json", end)
        agreement_id = signing.digest("Terms", terms)
        digest = Web3.to_bytes(hexstr=funding["hash"])
        receipt = chain.w3.eth.get_transaction_receipt(digest)
        chain.canonical_receipt(receipt, digest)
        if receipt["status"] != 1:
            raise Inconclusive("funding failed")
        chain.receipts.append(receipt)
        funding_observed = time.monotonic()
        chain.check_event(
            receipt,
            "Funded",
            {
                "agreementId": agreement_id,
                "requester": a,
                "provider": b,
                "authorizationNonce": 0,
                "price": PRICE,
            },
        )
        observe(chain, terms, agreement_id, 1)
        wait(folder / "compute-go.json", end)
        value = sum((parsed["x"], parsed["y"]))
        if scenario == "invalid_result":
            value += 1
        claim = wire(
            "Claim",
            requester=a,
            provider=b,
            agreementId=agreement_id,
            authorizationNonce=0,
            value=value,
            runId=manifest["runId"],
        )
        envelope = signing.envelope(
            "claim", claim, {"provider": signing.sign(account, "Claim", claim)}
        )
        if scenario == "malformed_evidence":
            envelope["unexpected"] = True
        if scenario == "outsider_evidence":
            envelope["signatures"]["provider"] = "0x" + "00" * 65
        if scenario == "oversized_evidence":
            (folder / "claim.json").write_bytes(b"x" * 16385)
        elif scenario == "truncated_evidence":
            (folder / "claim.json").write_bytes(b'{"kind":')
        elif scenario == "duplicate_evidence":
            (folder / "claim.json").write_bytes(b'{"kind":"claim","kind":"claim"}')
        else:
            write(folder / "claim.json", envelope)
        wait(folder / "claim-go.json", end)
        rejected = False
        try:
            chain.transact(
                chain.contract.functions.claim(
                    tuple_for("Claim", claim),
                    bytes.fromhex(envelope["signatures"]["provider"][2:]),
                ),
                "Claimed",
                {
                    "agreementId": agreement_id,
                    "provider": b,
                    "authorizationNonce": 0,
                    "value": value,
                    "price": PRICE,
                },
            )
        except ChainRejected:
            if scenario not in ("invalid_result", "late_funding"):
                raise
            observe(chain, terms, agreement_id, 1)
            if chain.contract.functions.credits(b).call() != 0:
                raise Inconclusive("invalid paid")
            rejected = True
        write(folder / "claim-attempted.json", {"rejected": rejected})
        if not rejected:
            record = observe(chain, terms, agreement_id, 2)
            if (
                record[3] != parsed["x"] + parsed["y"]
                or chain.contract.functions.credits(b).call() != PRICE
            ):
                raise Inconclusive("claim accounting")
            wait(folder / "withdraw-go.json", end)
            before = chain.w3.eth.get_balance(b)
            r = chain.transact(
                chain.contract.functions.withdraw(),
                "Withdrawn",
                {"owner": b, "amount": PRICE},
            )
            if (
                chain.w3.eth.get_balance(b)
                != before + PRICE - r["gasUsed"] * r["effectiveGasPrice"]
                or chain.contract.functions.credits(b).call() != 0
            ):
                raise Inconclusive("withdrawal delta")
        write(
            folder / "provider-done.json",
            {
                "receipts": chain.evidence(),
                "intents": chain.intents,
                "budget": chain.budget.reserved,
                "rejected": rejected,
                "fundingObservedMonotonic": funding_observed,
            },
        )
    else:
        offer = wait(folder / "advertisement.json", end)
        ad = signing.open(offer, "advertisement", {"provider": b})
        if (
            ad["serviceId"] != SERVICE
            or ad["policyId"] != POLICY
            or ad["runId"] != manifest["runId"]
            or ad["price"] != PRICE
            or now() >= ad["offerExpiresAt"]
        ):
            raise Rejected("advertisement policy")
        terms = wire(
            "Terms",
            requester=a,
            provider=b,
            serviceId=SERVICE,
            policyId=POLICY,
            x=config["x"],
            y=config["y"],
            price=PRICE,
            fundBefore=config["fundBefore"],
            claimBefore=config["claimBefore"],
            salt="0x" + secrets.token_hex(32),
            runId=manifest["runId"],
        )
        check_terms(terms, a, b, now())
        write(
            folder / "proposal.json",
            signing.envelope(
                "termsProposal",
                terms,
                {"requester": signing.sign(account, "Terms", terms)},
            ),
        )
        dual = wait(folder / "terms.json", end)
        signing.open(dual, "terms", {"requester": a, "provider": b})
        if dual["message"] != terms or now() >= ad["offerExpiresAt"]:
            raise Rejected("altered/expired terms")
        agreement_id = signing.digest("Terms", terms)
        auth = wire(
            "Authorization",
            requester=a,
            provider=b,
            agreementId=agreement_id,
            nonce=0,
            maxAmount=2 * PRICE,
            expiresAt=terms["fundBefore"],
            runId=manifest["runId"],
        )
        auth_sig = signing.sign(account, "Authorization", auth)
        write(
            folder / "authorization.json",
            signing.envelope("authorization", auth, {"requester": auth_sig}),
        )
        wait(folder / "fund-go.json", end)
        receipt = chain.transact(
            chain.contract.functions.fund(
                tuple_for("Terms", terms),
                tuple_for("Authorization", auth),
                bytes.fromhex(dual["signatures"]["requester"][2:]),
                bytes.fromhex(dual["signatures"]["provider"][2:]),
                bytes.fromhex(auth_sig[2:]),
            ),
            "Funded",
            {
                "agreementId": agreement_id,
                "requester": a,
                "provider": b,
                "authorizationNonce": 0,
                "price": PRICE,
            },
            PRICE,
        )
        observe(chain, terms, agreement_id, 1)
        write(
            folder / "funded.json",
            {
                "agreementId": agreement_id,
                "hash": Web3.to_hex(receipt["transactionHash"]),
            },
        )
        if scenario == "requester_offline":
            return
        if scenario != "provider_crash_before":
            wait(folder / "observe-go.json", end)
            try:
                claim_envelope = wait(folder / "claim.json", end)
                claim = signing.open(claim_envelope, "claim", {"provider": b})
                if (
                    claim["requester"] != a
                    or claim["provider"] != b
                    or claim["agreementId"] != agreement_id
                    or claim["authorizationNonce"] != 0
                ):
                    raise Rejected("claim binding")
                verified = claim["value"] == int(terms["x"]) + int(terms["y"])
                if not verified and scenario != "invalid_result":
                    raise Rejected("incorrect result")
                observation = {
                    "value": str(claim["value"]),
                    "verified": verified,
                    "postFundingSignatures": 0,
                }
            except Rejected:
                # Bad evidence gives no authority. Retain only a safe local classification.
                observation = {
                    "verified": False,
                    "rejectedEvidence": True,
                    "postFundingSignatures": 0,
                }
            write(folder / "observed.json", observation)
        wait(folder / "finish-go.json", end)
        if (folder / "refund-go.json").exists():
            observe(chain, terms, agreement_id, 1)
            chain.transact(
                chain.contract.functions.refund(agreement_id),
                "Refunded",
                {
                    "agreementId": agreement_id,
                    "requester": a,
                    "authorizationNonce": 0,
                    "price": PRICE,
                },
            )
            before = chain.w3.eth.get_balance(a)
            r = chain.transact(
                chain.contract.functions.withdraw(),
                "Withdrawn",
                {"owner": a, "amount": PRICE},
            )
            if (
                chain.w3.eth.get_balance(a)
                != before + PRICE - r["gasUsed"] * r["effectiveGasPrice"]
                or chain.contract.functions.credits(a).call() != 0
            ):
                raise Inconclusive("refund withdrawal delta")
        else:
            record = observe(chain, terms, agreement_id, 2)
            if record[3] != int(terms["x"]) + int(terms["y"]):
                raise Inconclusive("independent requester verification")
        write(
            folder / "requester-done.json",
            {
                "receipts": chain.evidence(),
                "intents": chain.intents,
                "budget": chain.budget.reserved,
                "verified": not (folder / "refund-go.json").exists(),
                "postFundingSignatures": 0,
            },
        )


def main():
    role, directory = sys.argv[1:]
    folder = Path(directory)
    try:
        run(role, folder)
    except (Rejected, Inconclusive, ChainRejected, ChainInconclusive) as exc:
        # Fixed exception text only; never serialize RPC exceptions/raw transaction bodies.
        import traceback

        write(
            folder / (role + "-error.json"),
            {
                "classification": type(exc).__name__,
                "frames": [
                    f.name + ":" + str(f.lineno)
                    for f in traceback.extract_tb(exc.__traceback__)
                ],
            },
        )
        return 2
    except Exception as exc:
        import traceback

        write(
            folder / (role + "-error.json"),
            {
                "classification": type(exc).__name__,
                "frames": [
                    f.name + ":" + str(f.lineno)
                    for f in traceback.extract_tb(exc.__traceback__)
                ],
            },
        )
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
