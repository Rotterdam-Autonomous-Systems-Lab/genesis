# Threat Model — Research Inventory and Experiment 001

This document is a starting inventory, not a complete assessment of a deployed system. Genesis has no production protocol or network. Every future experiment must define its own boundary and update this model before making security claims.

## Assets to consider

- Cryptographic keys and delegated authority.
- Funds, compute, bandwidth, storage, physical resources, and service access.
- Integrity and provenance of service agreements, messages, and contribution evidence.
- Availability of discovery and coordination functions.
- Privacy of participants, activity, and relationships.
- Upgrade and recovery mechanisms.

## Adversaries and failure conditions

Consider malicious participants, Sybil identities, colluding parties, compromised or lost keys, dishonest service providers or requesters, spam and denial-of-service actors, censoring intermediaries, malicious software updates, network partitions, delayed or reordered messages, and accidental operator error. Environmental constraints may include low power, intermittent connectivity, limited storage, and heterogeneous capabilities.

## Trust assumptions to state

For every proposal, state assumptions about cryptography, hardware, identity claims, time, connectivity, external data, dispute resolution, and participant resources. A mechanism does not remove trust merely by moving it to an oracle, registry, committee, or upgrade key.

## Initial security questions

- Can authority be constrained so a compromised key cannot exceed a stated budget or capability?
- Can service and contribution claims be forged, replayed, selectively withheld, or mutually fabricated by colluding parties?
- Can an attacker cheaply create identities or overwhelm discovery and verification?
- What happens during long partitions, equivocation, and delayed settlement?
- Can protocol evolution introduce hidden privilege or break historical verification?

## Research controls

Use synthetic keys and test data. Do not use real funds, production endpoints, or unauthorized external services. Document attack preconditions, impact, mitigations, residual risks, and evaluation limits. This document does not certify any design as secure.

## Experiment 001 boundary and severity

The [proposed architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md) and [security invariants](SECURITY_INVARIANTS.md) add a narrow two-agent, synthetic-fund escrow threat model. Neither is implemented or validated. Existing general network questions above remain open.

Severity below reflects impact within the modeled experiment: **Critical** can defeat authority or arbitrarily corrupt the run; **High** can cause unauthorized principal movement, loss, or false results; **Medium** can prevent service/recovery or mislead discovery; **Low** affects diagnostics without principal/state impact. Synthetic ETH has no real value, but that does not reduce the importance of a potential design flaw. “Design coverage” describes intended mitigation and required tests, never a verified guarantee.

Trusted boundary: local host/operator, Anvil privileged RPC and canonical state/time, EVM semantics, correct hash/signature primitives, exact dependency versions and integration, runner evidence collection. A and B, transport messages, discovery contents, and external callers are untrusted within that boundary. Shared machine access is not adversarial process isolation. EOAs establish key control only.

| Threat / actor | Severity | Experiment 001 design coverage | Residual limitation / required evidence |
| --- | --- | --- | --- |
| Malicious requester | High | Wrong results cannot settle even with A's signature; signed terms immutable; no early cancellation. SI-06, SI-09, SI-10. | A can withhold Acceptance after valid work and later refund; fair exchange is not solved. Test denial/no-receipt path and report provider loss of effort. |
| Malicious provider | High | A recomputes independently; contract verifies sum, B signature and A consent; fixed beneficiary. SI-01, SI-08–SI-11. | Can waste time or withhold service; no availability guarantee or proof B performed work. |
| Compromised agent keys | Critical | Per-authorization cap, fixed terms and effective unused-nonce revocation limit some actions. SI-02, SI-05. | Partial only: stolen A key can sign new authorizations until synthetic balance exhausted; B key permits B actions. No secure recovery or host protection. |
| Replay attacks | High | Domain/type/run binding, single-use nonce, unique agreement and terminal states. SI-03, SI-07, SI-17. | Resets/reorgs rewind state; freshness policy and trusted run environment required. Test old-run and cross-deployment messages. |
| Forged computation results | High | Both independent requester verification and contract arithmetic; signatures cannot override incorrect result. SI-09, SI-11. | Only fixed public arithmetic is covered; general computation/physical evidence out of scope. |
| Agreement tampering | High | Dual signatures over every field, derived ID, immutable stored terms. SI-06–SI-08. | Signing deliberately bad terms remains possible; UI/policy mistakes are not eliminated. |
| Front-running / ordering | High | Direct A funding and B settlement callers; fixed parties/amounts, no redirectable beneficiary. SI-08, SI-12. | Censorship/delay can cause timeout. Ordering still decides revoke/fund races. Test copied calldata from stranger and reordered operations. |
| Revocation races | High | Effective only at canonical execution, Unused->Revoked vs Unused->Consumed mutually exclusive. SI-05. | Funding first preserves obligation; pending revocation is not a guarantee. No funded/Acceptance revocation. |
| Expiration boundaries | High | Explicit strict funding/settlement comparisons and inclusive refund boundary using chain timestamp. SI-04, SI-10, SI-13. | Operator controls local timestamps; no wall-clock accuracy or public-chain timestamp security claim. Test -1/equality/+1 for each boundary. |
| Reentrancy | High | Pull credits, checks-effects-interactions, guarded mutators, atomic failure. SI-14. | Design only; malicious receiver and cross-function tests required despite EOA fixture. |
| Unauthorized withdrawals | High | Only credit holder withdraws its own positive credit to itself; no admins or arbitrary target. SI-12–SI-14. | Lost key can strand credits; forced ETH has no rescue mechanism. |
| Resource exhaustion | Medium | Bounded message schemas, fixed computation, no arbitrary code, offer/retry/run budgets. SI-18. | Host/RPC DoS remains possible; refunds require chain progress and A availability. |
| Dependency compromise | Critical | Exact versions/hashes, advisory and applicable audit review, no floating installs, independent digest vectors. | Gate incomplete. Malicious compiler/library/harness can defeat design; test success is insufficient against a compromised toolchain. |
| Chain reorganization / reset | High | Receipt block-hash/state reconciliation and runId checks; abort inconclusive on replacement/reset. SI-03, SI-07, SI-17. | Single local operator is trusted; no distributed finality or public reorg tolerance is established. |
| Sybil identities and collusion | High for future network; Medium within fixed fixture | Distinct A/B addresses and authenticated signed messages only; SI-08. | Not addressed as network security: two keys need not mean separate owners; colluders can fabricate activity, and no Sybil mechanism is proposed. |
| Unreliable communication | Medium | Idempotent semantic retries, receipt/state checks, finite retry limits, timeout refund. SI-10, SI-13, SI-17. | Liveness/fair exchange not guaranteed; keys lost at host restart terminate the run. |
| Unsafe autonomous spending | High | Explicit per-use maximum, fixed terms/recipient/service, separate signer policies, bounded harness, synthetic-only environment. SI-01, SI-02, SI-16, SI-18. | No contract-enforced aggregate wallet budget; gas and multiple fresh permissions can consume balance. No autonomous real-fund authorization. |
| Privileged RPC / malicious local host | Critical | Explicitly outside adversary model; loopback controls reduce accidental exposure. SI-16. | Can read memory, impersonate accounts, change state/time, and fake evidence. Experiment cannot protect against its test operator. |
| Off-chain “verified” flag or AI validity oracle | High | No such contract path; require typed Acceptance, B evidence, and deterministic arithmetic. SI-09, SI-11, SI-15. | Does not prove A ran a verifier; arbitrary intelligence and external facts remain unverified. |

## Security review and failure reporting

Before implementation, review the requester-veto/provider-fairness trade-off, exact signature schemas, revocation scope, deadlines, state transitions, input bounds, retry handling, dependencies, and invariant coverage. Record changes in ADR 0001 and associated specifications. No BLOCKING OPEN DECISION is present in the proposed semantics, but this review and separate implementation authorization are incomplete gates.

After any future experiment, report attacks that succeeded or remained inconclusive, not only mitigated threats. Distinguish cryptographic assumptions, contract properties, off-chain behavior, and environmental controls. Do not describe the local fixture as a permissionless network or as evidence for a consensus hypothesis.
