# Proposed Experiment 002 Threat Model and Assumptions

**2026-10-18 — Design analysis, not tested security evidence.** Read the [architecture](../architecture/EXPERIMENT_002_ARCHITECTURE.md) and [test plan](EXPERIMENT_002_TEST_PLAN.md). Severity estimates describe impact within a synthetic fixture, not production loss estimates.

## Assets, adversary and assumptions

Protect bounded requester principal, provider entitlement under signed terms, single-use authority, immutable agreement binding, correct result/state evidence and finite local resources. Either peer and any local message writer may be dishonest. Attackers may replay, mutate, reorder, truncate or suppress messages, submit unauthorized calls, return false work, withhold cooperation or crash. Controlled ledger/RPC faults are injected separately.

**Cryptographic assumptions:** established signature/hash security, correct standard libraries and exact domain/field encoding. **Environmental assumptions:** trusted shared OS/harness, independently generated process-owned keys, correct compiler/VM/predicate, accessible canonical chain data and eventual ledger progress. Conditional provider collection specifically assumes a valid claim is included before claimBefore and remains canonical. A local single-node chain does not test decentralized inclusion, censorship resistance or finality. B pays synthetic gas independently; requester authority covers principal only.

After A explicitly signs the upfront policy and funds, refusal is no longer an authorization withdrawal. Revocation-before-funding blocks first use; revocation-after-funding cannot cancel the obligation. Key compromise can issue seemingly valid signatures; cryptographic checks do not identify operator intent. Confidentiality and compensation for computation/gas are not guaranteed.

## Threat assessment and planned evidence

| Threat / severity | Proposed control | Planned test and remaining gap |
| --- | --- | --- |
| Requester withholds post-result approval / High research relevance | No second approval in this separate policy; provider claim checks public predicate. | T02/T03: refusal and requester shutdown after funding; only timely included claims are covered. |
| Provider false result or forged evidence / High | Stored-input arithmetic plus exact bound Claim signature/caller. | T04/T05/T06: false result, wrong key/domain/run/fields. No claim about subjective correctness. |
| Consent tampering or cross-experiment use / High | Dual signed fixed policy/service/terms and distinct EIP-712 domain. | T05/T06: mutate every field; Experiment 001 signatures must fail. |
| Replay, nonce reuse, retry ambiguity / High | Irreversible nonce/terminal state, pending-intent latch and reconciliation. | T07/T12: retries before/after broadcast and receipt loss. Unresolvable RPC ambiguity aborts, never creates new spending authority. |
| Revocation/funding races / High | Canonical execution order; unused revoke only. | T08: both ordered schedules. No retroactive funded cancellation. |
| Deadline/order manipulation / High | Strict claim-before/refund-at-or-after checks. | T09: -1/equality/+1, competing transactions and delayed workflow. Timestamp/inclusion remains ledger trust. |
| Unauthorized fund/claim/refund/withdraw / High | Exact actor checks and own-credit pull withdrawal. | T10: outsider calls and wrong payee; no general smart-wallet support. |
| Reentrancy, transfer failure, accounting corruption / High | Guard, effects before interaction, atomic revert, aggregate liabilities. | T11: callback attempts, rejected transfers, surplus balances and concurrent agreements. Tests are not a proof. |
| Front-running/public-output leakage / High limitation | Bind B/payment recipient and terms; outsider cannot redirect proceeds. | T14: reveal correct output then suppress timely claim, refund A. This intentionally demonstrates failure of strong fairness; no delivery confidentiality. |
| Provider disappears or sends malformed/oversized/nonregular data / Medium | No work before funding; bounded transport, deterministic refund and cleanup. | T13/T15: crashes, invalid files, duplicates, absent evidence. Refund does not repay effort or gas. |
| Chain rollback, false events or malicious RPC / High | Canonical receipt/state/code/run/credit checks; stop on contradictions. | T12/T16: altered hashes/events, lost receipts, snapshot/revert. A fully malicious trusted harness/RPC is outside assurance. |
| Unbounded compute/messages/process lifetime / Medium | Fixed arithmetic, bounded inputs/read/time/polling and cleanup. | T15/T17: resource-bound and interrupt tests. No malicious-host isolation. |
| Compromised participant key / High | Ephemeral keys, scoped one-use capped consent, unused revocation. | T08/T10 show scope, not recovery of a compromised funded identity. Funds can remain unclaimed after key loss. |
| Sybil identities/collusion / Medium limitation | Bind participants per agreement; no reputation/security inference from address counts. | Wrong-peer tests only; no Sybil resistance, fair pricing or anti-collusion mechanism claimed. |
| Dependency/compiler/verifier compromise / High residual | Exact reviewed pins/hashes, minimal read-only CI and no public-network runtime dependencies. | Pre-implementation maintenance review; do not copy old pins unreviewed. Full supply-chain assurance remains outside scope. |
| Offline/delayed/satellite communication / High portability limit | Explicit deadline/inclusion assumptions rather than hidden liveness claims. | Delay and non-inclusion negative controls. Arbitrary delay cannot satisfy the chosen finite collectability premise. |

## Property mapping and uncertainty

Proposed Experiment 002 properties are P2-01 valid upfront authorization, P2-02 caps, P2-03 single-use replay prevention, P2-04 expiry, P2-05 unused revocation order, P2-06 immutable terms, P2-07 domain/run binding, P2-08 participant/agreement binding, P2-09 objective result verification, P2-10 caller restrictions, P2-11 exclusive terminal/refund rules, P2-12 accounting/withdraw safety, P2-13 no post-funding requester veto for timely valid claims, P2-14 honest evidence/retry reconciliation, P2-15 bounded local execution and P2-16 no production/external service use.

These are **proposed properties**, not a new assessment of Experiment 001's 18 invariants. Many authorization/accounting goals overlap, but the post-result Acceptance requirement intentionally differs. Future coverage must map each P2 property to actual code/tests and record pending cases rather than claiming inherited enforcement.

## Why fairness remains unresolved

A provider can publish a usable result, lose inclusion until the deadline, and receive nothing while A refunds. An honest computation finishing too late is also unpaid. An incorrectly specified but faithfully executed predicate can pay for useless work. Physical inputs or subjective quality require additional trust. This proposal removes one peer-controlled approval gate; it does not remove ledger, time, specification, key or data-availability assumptions. Adding bonds, challengers, encryption or computation proofs changes those assumptions and must be evaluated separately.

## Task 006 review additions

[Design review](EXPERIMENT_002_DESIGN_REVIEW.md) retains the proposal with amended claims. **Late funding / High liveness limitation:** signed valid deadlines can still leave B insufficient time; T18 records slack and non-inclusion without promising compensation. **Absent actors / High availability limitation:** after expiry the record remains Funded until a valid refund transaction is included; T19 must distinguish enabled refund, credit and successful withdrawal. **Repeated/collusive work / High future-reward risk:** identical valid results across distinct authorized agreements are not a proof of useful or scarce contribution; T20 records this boundary, not a mining/Sybil defense.

P2-11 specifies exclusive outcomes and deterministic refund rules, not automatic progress. P2-13 remains conditional collectability; P2-14 must report all attempted runs and stages, not only timely inclusions. A future native reward or consensus mechanism cannot reuse per-agreement validity as evidence of unique work or independent operators without separate research.

## Task 007 fee and supply-chain boundaries

**Gas-cost exhaustion / High bounded-authority risk:** a principal-only signed cap is not a total wallet-cost ceiling. The existing gas-unit/attempt bounds need a finite per-gas fee and total run-cost policy; B-FEE blocks integrated implementation until it is specified/tested. Do not infer unauthorized principal transfer from expected gas charged on a mined revert. **Dependency expansion / High residual:** [B-DEP review](EXPERIMENT_002_DEPENDENCY_REVIEW.md) records point-in-time findings, not approved new pins. See the [final specification](EXPERIMENT_002_FINAL_SPEC.md) and [public fixtures](EXPERIMENT_002_SIGNING_VECTORS.md). No changes to Experiment 001's security claims follow.
