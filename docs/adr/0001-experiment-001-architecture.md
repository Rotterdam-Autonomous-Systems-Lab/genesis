# ADR 0001 — Local Experiment 001 Architecture

Status: **Accepted for local escrow-only implementation by Task 003A**. Scope: Experiment 001 only. Date: 2026-10-17. Originally Proposed in Task 002B; Task 003A separately authorizes the Solidity component and explicitly preserves requester veto. Python agents, full experiment integration, public deployment, and final Genesis architecture are not authorized by this decision.

## Context

Genesis needs an initial bounded demonstration of separate agents reaching an authorized, independently verifiable economic outcome. Its broader mission remains research into a possible independent permissionless network. A local fixture must make consent, authority, verification, timing, refunds, and failure behavior explicit without inventing cryptography or conflating requester assertions with proof.

## Proposed decision

Use Python processes with independent ephemeral EOA signers, narrowly scoped non-upgradeable Solidity escrow, Foundry tests, and a loopback-only Anvil chain with synthetic ETH. Use standard EIP-712 typed messages for offers, dual-signed terms, first-use authorization, provider results, and requester Acceptance. Choose one bounded sum-of-two-uint64 service. Require both requester Acceptance and an on-chain recomputation check before settlement. Use single-use requester nonces, immutable terms, pull withdrawals, strict deadlines, and requester refund after timeout.

The precise proposal is in [Experiment 001 architecture](../architecture/EXPERIMENT_001_ARCHITECTURE.md); the [experiment specification](../experiments/EXPERIMENT_001.md) defines evaluation, and [security invariants](../SECURITY_INVARIANTS.md) define required tests.

## Alternatives considered

| Alternative | Assessment for this experiment |
| --- | --- |
| Pure off-chain payments/mock ledger | Smaller, but does not test independent contract enforcement or escrow state transitions. |
| Requester-signed verification boolean only | Rejected: the contract cannot infer that off-chain verification occurred, and a false signed claim could release payment. |
| Provider can settle directly on any correct result | Would improve provider recourse, but omits the required requester post-result release authorization in this experiment. Deferred. |
| Arbitrary computation with oracle, fraud proofs, or validity proofs | Adds trust, timing, or proof machinery beyond the bounded first experiment. Deferred. |
| ERC-20 payment or native Genesis token | Unnecessary token/dependency surface for synthetic local escrow. Deferred; no native asset decision. |
| Production/public testnet, existing network integration, or independent L1 now | Unnecessary operational/security exposure and premature architecture commitment. Deferred. |
| Custom signature scheme or novel consensus | Unjustified, outside scope, and unsupported by research evidence. |

## Security rationale

Contract arithmetic plus signed requester consent separates validity from willingness to pay. A signed invalid Result/Acceptance cannot satisfy the computation predicate. EIP-712 domain binding is combined with explicit nonce and run state; typed signing alone is not replay protection. No arbitrary execution, relayers, token callbacks, upgrades, admins, or pre-deadline cancellation is proposed. See the linked threat model and invariants for assumptions and adversarial tests.

## Trade-offs and limits

Repeated addition is intentionally trivial and inefficient as outsourced work. A malicious A can withhold Acceptance after valid service; timeout refunds A and provides no compensation to B. This does not solve fair exchange or disputes. Public inputs provide no confidentiality. Shared-host/RPC control is trusted; EOAs provide only key control. Funding revocation affects unused authorizations only, so a mined funding obligation survives later revocation and funding expiry. Single-node Anvil provides no decentralized finality or consensus evidence.

## Reversibility

These are proposed, reversible choices for an isolated experiment. Future experiments can replace the service, signing model, payment design, execution environment, and tooling through reviewed ADRs. **Using Anvil/Ethereum tooling for this experiment does not commit Genesis to Ethereum as its final network architecture.** No independent-network, tokenomics, governance, or consensus choice is made here.

## Review gates and open questions

No BLOCKING OPEN DECISION remains in the defined security semantics. Task 003A authorizes the escrow component with the documented fairness limitation preserved. Exact escrow tool/dependency pins are recorded in [DEPENDENCIES.md](../../DEPENDENCIES.md); [coverage](../experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) records local tests and remaining integration requirements. This acceptance is scoped authorization, not an independent security audit or completion of the full experiment review gate. Python dependencies, independent review, and full integration remain pending.

Broader research questions remain open: fair exchange without requester veto, verification of nontrivial or physical services, bounded delegation independent of the main key, secure key recovery, real permissionless discovery, and the role of future chain/native-asset/consensus designs. They are not blockers to specifying this bounded experiment.
