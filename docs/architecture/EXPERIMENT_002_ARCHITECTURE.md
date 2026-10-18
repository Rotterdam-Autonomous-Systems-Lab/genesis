# Experiment 002 Architecture

**2026-10-18 — Accepted bounded local design after Task 008 review; unimplemented.** See [ADR 0002](../adr/0002-experiment-002-fair-exchange.md), [experiment](../experiments/EXPERIMENT_002.md) and [prior-art comparison](../../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md).

## Mechanism and components

Propose a separate contingent escrow with a fixed public sum-u64 predicate. Upfront signed terms replace post-result requester approval. The provider needs no new A signature after funding. **This intentionally differs from Experiment 001**, whose Acceptance rule, contract, agents, tests and publication stay unchanged. Experiment 001's SI-11 requester-signature requirement must not be claimed unchanged for Experiment 002; use the separate properties/test IDs below.

Chain-neutral requirements are authenticated terms, single-use authority, canonical ordered state, deterministic verification, locked principal, time-bounded claims/refunds and isolated credits. A future independent network or alternative architecture must be evaluated against these requirements; EVM compatibility is not presumed. For a controlled local prototype, propose Python agents, established Ethereum signing libraries, Solidity/Foundry and temporary Anvil. No dependency adoption, production chain or consensus choice follows.

| Component | Responsibility / trust boundary |
| --- | --- |
| Requester A | Checks fixed service/policy, exact peer, inputs, caps/deadlines; signs terms and one authority; alone funds/refunds. Independently checks outputs when online, without a settlement veto. |
| Provider B | Signs matching advertisement/terms; verifies canonical funding; computes and signs result; alone submits claim and withdraws its credit. Cannot sign A's authority. |
| Bounded public local transport | Signed messages only, exact schemas, regular files, atomic no-clobber publication, size/time limits; no shared in-memory protocol state or key access. |
| New escrow | Stores immutable terms and authority nonce; directly verifies result; exclusive terminal state and own-credit pull withdrawals. No upgrade/admin/oracle/Acceptance path. |
| Trusted harness/ledger | Deploys, manages synthetic balances/time/faults, checks canonical receipts/state and independent result, records public evidence, terminates children. Not a real decentralized ledger or hostile-host boundary. |

## Proposed signature and binding contract

Use established EIP-712/ECDSA libraries, not custom signature algorithms. Candidate domain: name `GenesisExperiment002`, version `1`, chainId `31337` for the local fixture, verifyingContract equal to the fresh deployment. Reject wrong domain or code/run identity. Exact ordered candidate type definitions:

```text
Advertisement(address provider,bytes32 serviceId,bytes32 policyId,uint256 price,uint64 offerExpiresAt,bytes32 runId)
Terms(address requester,address provider,bytes32 serviceId,bytes32 policyId,uint64 x,uint64 y,uint256 price,uint64 fundBefore,uint64 claimBefore,bytes32 salt,bytes32 runId)
Authorization(address requester,address provider,bytes32 agreementId,uint256 nonce,uint256 maxAmount,uint64 expiresAt,bytes32 runId)
Claim(address requester,address provider,bytes32 agreementId,uint256 authorizationNonce,uint256 value,bytes32 runId)
```

B signs Advertisement; A and B sign Terms. A signs Authorization. B signs Claim. `agreementId` is the EIP-712 Terms digest. The fixed `serviceId` is keccak256 of UTF-8 `genesis.sum-u64.v1`; `policyId` is keccak256 of UTF-8 `genesis.exp002.direct-sum-u64.v1`. The latter means **preauthorized direct verification without post-result requester approval**, and is checked against an immutable constant. Do not reuse the Experiment 001 domain, agreements, Acceptance or signatures. A/B validate the signed Advertisement, fixed service/policy/run and unexpired offer before agreeing/funding. The contract enforces the dual-signed Terms, not the discovery advertisement; those Terms independently bind all settlement conditions. Freeze matching cross-language digest vectors before implementation starts.

Only 65-byte EOA signatures in the established low-s, v=27/28 encoding are proposed; malformed, high-s, compact, zero/recovered-wrong-address signatures are rejected. A and B must be nonzero and distinct. Use exact typed integer widths and canonical decimal strings on the wire, reject unknown/duplicate fields, floats, negatives and out-of-range values. Wire JSON is not itself the digest. Contract-wallet signatures are deferred, not silently accepted. Every field mutation must have a regression test.

## Authority, timing and state

| Action | Exact proposed behavior |
| --- | --- |
| Fund | Caller A only; dual valid Terms signatures and matching A Authorization; fixed service/policy/run; `0 < price <= maxAmount <= 10^15`; transferred value exactly price. Require `now < expiresAt <= fundBefore < claimBefore`, unused nonce and new agreement. Store immutable terms and consumed nonce atomically; no provider work before canonical funding. |
| Revoke | Caller A revokes its unused nonce. Nonce status Unused -> Revoked or Unused -> Consumed; no reset. Revoke-before-fund prevents funding. Fund-before-revoke consumes authority and later revoke of that nonce reverts; it cannot undo the funded obligation. |
| Claim | Caller B only, Funded, matching signed Claim and consumed nonce, `now < claimBefore`; check value exactly `uint256(x) + uint256(y)` from stored terms. Credit exactly price to B, mark Settled atomically. A approval, silence or local refusal is irrelevant. No arbitrary verifier callback. |
| Refund | Caller A only, Funded, `now >= claimBefore`; credit exactly price to A, mark Refunded atomically. Claim at equality fails. No early funded cancellation, partial refund, requester dispute veto or provider penalty. |
| Withdraw | Caller receives only its accumulated credit; zero credit rejected, credit zeroed before transfer; checked transfer failure reverts credit change; established reentrancy guard. No alternate payout address or administrator withdrawal. |

Agreement state: `None -> Funded -> Settled OR Refunded`, terminal forever. Nonce namespace is requester plus deployment/run context; concurrency across agreements must not alias identities or consumed authority. An invalid claim reverts without changing funded state or burning a second authority. A failed transaction does not consume a successful on-chain state transition; retry uses the same intent and reconciles the actual nonce/receipt. Refund does not restore spending authority. Deadline validity uses canonical block timestamp, not OS clock; no grace period, “sent before deadline” rule or inferred timestamps.

## Accounting and delivery

Maintain aggregate funded principal and outstanding credits. `balance >= locked principal + outstanding credits`; sum of all per-record obligations/credits equals aggregate accounting. Unexpected forced transfers are surplus, cannot credit a participant, alter price or enable payout; no surplus recovery is included. Exact balance equality is inappropriate in an EVM environment with forced transfers. Successful withdrawals reduce credits and contract balance by the same principal; transaction gas is separate. Mixed concurrent settle/refund/withdraw orders must preserve conservation.

Persist the accepted public value keyed by agreement, with an event binding agreement/nonce/provider/value/price. On-chain stored value plus accepted terms supplies delivery evidence in this public task, assuming accessible canonical data. The requester/harness recomputes independently; settlement trusts the fixed contract predicate, **not** a claimed off-chain check. An event without canonical receipt/state/credit verification cannot establish success. This public disclosure is not confidential or atomic delivery: mempool visibility can reveal value even when a claim is censored, expires or reverts.

## Recovery, bounds and keys

Keys are ephemeral and generated within each agent process; no shared private key, production wallet, environment-secret file or stored key artifact. Local shared host/RPC administrator remains trusted. Transactions are locally signed; do not use RPC-unlocked participant accounts. No production endpoints, proxy/redirect/CCIP fallback, unrestricted shell execution or model/API calls.

Reuse the reviewed bounded-transport pattern only after checking its applicability; proposed maximum message size 16 KiB, per-call timeout 5 seconds, run wall-clock budget 120 seconds, finite polling. Fresh run identity, code hash, chain ID and loopback destination checked before signing/sending. Never silently accept different terms or re-sign an altered result after a retry.

Record transaction intent and hash before waiting. A timeout after possible broadcast means **pending/unknown**, not failure or permission to sign a new transaction/nonce. Reconcile canonical receipt, block hash, agreement state, nonce state, credits and balance; resend only an identical signed transaction if appropriate. Unresolved uncertainty blocks additional sends in that client. Snapshot/revert or contradictory canonical evidence aborts the run as inconclusive; do not reinterpret an orphaned payment as final. Reorg handling after disclosure cannot claw back knowledge of the output.

Provider crash before claim leads to refund after deadline; crash after claim requires reconciliation, not duplicate settlement. Requester crash after canonical funding does not block provider claim, but lost keys can leave requester refunds uncollected. Claims submitted too late cannot demand payment by asserting earlier computation. A shutdown budget can stop the fixture before a refund is observable: report incompletion rather than overriding deadlines. Harness cleanup runs on success, failure and interruption.

## Review gates and open decisions

The proposed safety behavior above is concrete. **Implementation gate:** founder/design review must accept upfront predicate consent instead of a second Acceptance and explicitly accept public-output leakage, trusted local ledger and strict deadlines. This is a reversible experimental proposal, not a blocking contradiction in Experiment 001. The proposed schemas, dependency/security-maintenance review, tested installation commands and complete digest vectors must be reviewed/frozen in the implementation specification before code is authorized. No cryptographic or economic choices for a future Genesis network are made.

## Task 006 review disposition

[Design review](../experiments/EXPERIMENT_002_DESIGN_REVIEW.md): amend claims and retain **Proposed**, pending R1–R3. Refund and withdrawal are explicit transactions; deadline passage alone does not transition state or deliver funds. Late funding can leave insufficient provider time even when the signed times pass validation. Record observed funding-to-deadline slack, and report refused or incomplete work without bypassing deadlines. No minimum slack, grace period or funded early-cancel path is silently added.

A future independent L1 must supply its own secure authentication/domain rules, deterministic verification/resource accounting, canonical ordering, data availability and timing/finality assumptions. The requirements may transfer; EIP-712, addresses, EVM execution and Anvil clock/finality behavior are not selected for that L1. Repeated valid arithmetic is not unique useful work, a scarce security resource or a native-token reward criterion.

## Task 007 exact interface reference

Use the [final specification](../experiments/EXPERIMENT_002_FINAL_SPEC.md) for exact EIP-712/wire schemas, negotiation envelope, constructor/view/mutation/event interfaces and reconciliation rules. [Vector guide](../experiments/EXPERIMENT_002_SIGNING_VECTORS.md) supplies concrete signed payloads and timestamp/state expectations. The [dependency assessment](../experiments/EXPERIMENT_002_DEPENDENCY_REVIEW.md) has not approved a new tuple. Readiness is BLOCKED by B-DEP and B-FEE; no code is authorized. Service principal limits and transaction gas-cost limits are explicitly distinct.

## Task 008 accepted design constraints

[Blocker resolution](../experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md) and [bounded costs](../experiments/EXPERIMENT_002_BOUNDED_COST_MODEL.md) supersede prior readiness paragraphs. Use the [final specification revision 2](../experiments/EXPERIMENT_002_FINAL_SPEC.md), exact tested baseline, compiler/source restrictions and finite independently authorized signer budgets. ADR 0002 is Accepted for local design only; READY does not authorize code/deployment or select a future Genesis L1 architecture.
