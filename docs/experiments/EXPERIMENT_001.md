# Experiment 001 — Bounded Verifiable Economic Interaction

Status: **local escrow (Task 003A) and separate-process Python integration (Task 003B) implemented and locally tested; Task 003C conditional experimental acceptance, independent review pending**. See [escrow coverage](EXPERIMENT_001_ESCROW_COVERAGE.md) for evidence and limitations. This experiment examines a narrow case of autonomous economic authority and verifiable coordination. It is an early engineering milestone toward Genesis's broader permissionless network research. [Architecture](../architecture/EXPERIMENT_001_ARCHITECTURE.md), [invariants](../SECURITY_INVARIANTS.md), and [ADR 0001](../adr/0001-experiment-001-architecture.md) define the proposed implementation contract.

## Objectives and non-goals

Demonstrate two separate software agents with separate keys discovering a service, agreeing to immutable terms, authorizing bounded synthetic spending, computing and independently verifying a deterministic result, and settling only when contract predicates and requester consent hold. Measure rejection behavior, state/accounting safety, and reproducibility.

No production network, real funds, native token, consensus invention, general service marketplace, AI framework, uncontrolled replication, public deployment, comprehensive prior-art claim, or final Genesis architecture is involved. Permissionless discovery, resource-contribution security, satellite coordination, and independent network design remain later research areas.

## Actors and trust boundaries

A is the requester; B is the provider. A owns only A's signer, B owns only B's signer. Both may lie, withhold messages, or act maliciously. Neither trusts the other's claimed result or intelligence. An untrusted local manifest and message files transport signed offers and terms. The escrow enforces payment predicates. The local operator, host, RPC, EVM, signature libraries, and computation specification are environment dependencies. Separate control means distinct signer/process ownership, not secure isolation against the shared host administrator.

Only A can fund/refund its escrow. Only B can settle. Credit owners can withdraw only their own credits. The deployer has no privileged escrow control. There is no trusted verification oracle.

## Preconditions and implementation gate

- Clean local fixture, literal-loopback Anvil chainId 31337, no public fork, new immutable runId and escrow address.
- Separate fresh ephemeral A/B keys with simulated balance and separate gas budgets; neither key is logged, shared, or committed.
- Locked dependency/compiler versions, compatible encoding vectors, reviewed threat model and invariant-to-test mapping.
- A bounded implementation task separately authorized after the [security-review gate](../ROADMAP.md#experiment-001-security-review-gate); this document authorizes no build or deployment.
- Fixed service, input ranges, price policy, deadline rules, signer ownership, and state machine from the architecture document.

## Inputs and outputs

Inputs: a signed B Advertisement; dual-signed Agreement; A-signed single-use Authorization; two uint64 operands; synthetic price and cap; chain/run identity; fixed deadlines. Outputs: B-signed Result, independently computed A result, A-signed Acceptance only on match, canonical transaction receipts, terminal escrow state, nonce statuses, credits/withdrawal receipts, and a redacted evidence manifest. Mismatches and aborted runs are first-class outputs.

Golden success fixture: x=7, y=11, expected=18, price=10^12 simulated wei, maxAmount=2*10^12 simulated wei. Amounts exclude gas. Repeat with boundary operands (0 and uint64 maximum) and invariant-specific adversarial fixtures.

## Identity, discovery, and agreement

Create independent ephemeral keys in the owning agent processes; allocate synthetic balances through the trusted harness. Addresses prove key control only. No external identity or provider trust score is assumed.

B signs the fixed service advertisement and places it in the bounded local discovery manifest. A validates schema, domain/runId, provider signature, expiry and policy. Discovery is deliberately local and centrally provisioned for this experiment; it does not demonstrate censorship resistance or Sybil resistance.

A chooses inputs, price, parties, unique salt, fundingDeadline and settlementDeadline, signs Agreement, and sends it to B. B either signs identical terms or rejects. There is no implicit negotiation result: a counteroffer is a new salt/digest requiring both signatures. The contract checks both signatures on funding, independent of the discovery transport.

## Spending, work, verification, and settlement

1. A creates Authorization binding requester, provider, agreementId, nonce, maximum principal, first-use expiry, and runId. A signs it, then submits fund itself with both term signatures and exact msg.value=price.
2. Escrow validates price <= maxAmount <= MAX_PRICE, signatures, participants, supported service, deadlines, runId, and unused nonce/record. It atomically consumes the nonce and enters Funded. Invalid funding changes no state.
3. After observing and reconciling Funded state, A sends the computation request identified by agreementId. B loads agreed inputs, computes their mathematical sum, signs Result and sends evidence to A. No arbitrary code is executed from a request.
4. A checks B's Result signature and bindings and independently recomputes x+y. On mismatch it creates no Acceptance. On match, A signs Acceptance bound to the result digest and stored authorization nonce.
5. B verifies A's Acceptance and calls settle before settlementDeadline. The contract independently verifies the signatures and exact arithmetic predicate, marks Settled, and credits price to B. No message boolean or oracle controls payout.
6. B calls withdraw to receive synthetic ETH. Settlement credit and withdrawal are distinct observable events; assert exact principal while recording gas separately.

The contract can verify this narrow service because inputs and arithmetic are public and cheap. A's Acceptance proves signing consent, not execution of a particular Python verifier. The on-chain predicate rejects wrong results even if A signs them. A correct result without A's receipt is insufficient for settlement.

## Sequence

```mermaid
sequenceDiagram
    participant D as Local manifest (untrusted)
    participant A as Agent A / requester
    participant B as Agent B / provider
    participant E as Local escrow on Anvil
    B->>D: Signed Advertisement
    A->>D: Discover service
    D-->>A: Advertisement and signature
    A->>A: Validate offer, policy, domain and run
    A->>B: Signed Agreement
    B->>B: Validate identical terms
    B-->>A: B Agreement signature
    A->>A: Sign bounded Authorization
    A->>E: fund terms, signatures, exact price
    E-->>A: Funded / nonce Consumed
    A->>B: Request agreed computation
    B->>B: Compute x + y
    B-->>A: Signed Result
    A->>A: Validate evidence and independently recompute
    alt Result matches
        A-->>B: Signed Acceptance
        B->>E: settle result and both evidence signatures
        E->>E: Verify consent, arithmetic, deadline and state
        E-->>B: Settled / credit price
        B->>E: withdraw own credit
        E-->>B: Simulated payment
    else Invalid or missing result / no Acceptance
        Note over A,E: No settlement; wait for chain deadline
        A->>E: refund at or after settlementDeadline
        E-->>A: Refunded / credit exact price
        A->>E: withdraw own credit
        E-->>A: Simulated refund
    end
```

## State transitions and failures

Off-chain lifecycle: Discovered -> TermsSigned -> FundedObserved -> ResultReceived -> Verified -> AcceptanceSigned -> SettledObserved -> WithdrawnObserved. Rejection or transport timeout is an off-chain outcome, not an escrow transition. An off-chain timeout cannot bypass the signed chain deadline.

On-chain lifecycle: None -> Funded -> Settled OR Refunded. Terminal records never reopen. Nonces: Unused -> Consumed OR Revoked. Failed calls revert; withdrawal does not alter terminal agreement state.

Before funding, either party may stop; A can revoke its unused nonce. After funding there is no early cancellation. Revocation cannot undo consumed funding. Failed work, missing evidence, disagreement, or a malicious requester withholding Acceptance results in no provider payout; A may refund at timestamp >= settlementDeadline. This is deterministic requester-consent escrow, not fair exchange or a provider-cost guarantee.

All first-use and settlement deadlines are strict `<`; equality rejects the relevant action. Refund starts at `>= settlementDeadline`. Chain execution order determines pending revocation/funding races; broadcasting revocation is not effectiveness. No partial payout or partial refund exists. Refund credits exact principal and excludes gas.

On ambiguous RPC delivery, reconcile receipt, canonical block hash, nonce, and record state before retrying; do not issue a new economic authorization. Re-broadcast the same transaction or same semantic replacement under transaction-nonce rules. Invalid settle/refund retries never double-credit. Failed withdrawals preserve credit. Chain reset/reorg detection, lost keys, or inability to reconcile ends the run as inconclusive. See architecture for bounded retries, run budgets, and key handling.

## Success and rejection criteria

Success requires all of: separate A/B signers; validated offer and both agreement signatures; exact bounded funding and one consumed nonce; B-signed result; A's independent comparison and signed Acceptance; independently checked on-chain arithmetic; one terminal settlement and exact provider credit; successful provider withdrawal; reproducible public-data evidence and no secret leakage. No success is claimed from logs alone.

Rejection fixtures must include forged/missing signatures, every mutated signed field, wrong domain/contract/run/participants, price over cap, wrong msg.value, repeated and revoked nonce, first-use and settlement expiry boundaries, incorrect result even with A Acceptance, missing Acceptance for a correct result, wrong caller, duplicate settle/refund, withdrawal callbacks/failure, and communication/RPC ambiguity. Assert unchanged state/credits on every rejected call. The refund path must terminate in Refunded and exact A credit, never B credit. Required coverage is enumerated by [security invariants](../SECURITY_INVARIANTS.md).

## Reproducibility and evidence

A clean-clone procedure must record exact tool versions, dependency hashes, compiler/EVM settings, fixture inputs, local chain configuration, contract bytecode hash/address, runId, public addresses, typed-message digests, canonical receipt/block hashes, timestamps, state/credit snapshots, and invariant outcomes. Fresh private keys/runIds may change addresses and hashes; equivalent transitions and assertions, not identical signatures, are the reproducibility goal. Provide at least two independent clean runs and deterministic encoding golden vectors across Python and Solidity.

Record negative and inconclusive results. Measure contract gas, verifier time, message count, rejection count, and time to settlement/refund, without claiming benchmarking generality. Local escrow and Task 003B end-to-end results are recorded in the coverage document. See [reproduction commands and process boundaries](../../sdk/python/README.md). Never include secret values, key exports, .env content, or private host details in published artifacts.

## What a successful execution would and would not establish

A successful future run would provide evidence that this specific local implementation can enforce a signed spending bound, immutable terms, replay protection, deterministic result validation, requester consent, and defined refunds under its tested assumptions. It would not establish a novel protocol, provider effort, efficient outsourcing, fair exchange, Sybil resistance, consensus safety, real-world identity, generalized computation verification, public-chain security, censorship resistance, production readiness, or the feasibility of the ultimate Genesis network.

No BLOCKING OPEN DECISION is left in this behavior. Task 003A separately authorizes and tests only the escrow component, preserving requester veto and pinning its dependencies. Task 003B separately authorizes the bounded Python integration; independent review and the pending cases in the coverage map remain open.

## Task 003C acceptance assessment

The [security review](EXPERIMENT_001_SECURITY_REVIEW.md) assesses all 18 invariants and records CONDITIONAL PASS for the bounded local fixture, with explicit residual review/coverage conditions. It is not an independent audit, production approval, final research report, or authorization for Experiment 002. Requester-veto semantics and the long-term independent-network ambition are preserved.
