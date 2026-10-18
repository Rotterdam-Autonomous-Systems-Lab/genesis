# Experiment 002 Design Review — Task 006

**2026-10-18 — Documentation-based project review; no implementation, execution, independent audit or security proof.**

## Decision and rationale

**Amend the proposal and keep ADR 0002 Proposed. Experiment 002 is not yet ready to start implementation.** The direct checker is a useful candidate for isolating requester veto, but it cannot be accepted as a general provider-payment or fair-exchange guarantee. Final scope acceptance, schemas/vectors and dependency review remain pre-implementation gates. This review does not authorize code.

The review considered the [published Experiment 001 report](../../research/reports/EXPERIMENT_001_REPORT.md), [six-family comparison](../../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md), [proposal](EXPERIMENT_002.md), [architecture](../architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat model](EXPERIMENT_002_THREAT_MODEL.md), [test plan](EXPERIMENT_002_TEST_PLAN.md), [ADR 0002](../adr/0002-experiment-002-fair-exchange.md) and canonical research context. Findings below are reasoning about the specification, not confirmed code vulnerabilities.

For fixed public arithmetic, direct checking needs fewer new trust roles than challengers, an adjudicator or a proof system, and permits a controlled comparison with Experiment 001. Acceptance remains premature because its timely-inclusion premise is not a payment-liveness result, the original H2-C closure wording overstates progress without a live caller, and a future contribution economy needs much more than per-agreement result validity. The amendment narrows claims rather than promising away these limitations.

## Evaluation and technical risks

| Area | Review judgment and implication |
| --- | --- |
| Requester-veto resistance | Upfront dual consent plus B-only valid claim removes the second A signature gate after funding. Test A refusing and stopping. A can still decline terms/funding; that is not a breach of an unfunded agreement. |
| Provider payment | Correct timely canonical claim can credit B under the predicate; actual withdrawal requires live key ownership, gas, ledger progress and inclusion. Computation completion, broadcast or local verification alone gives no entitlement to automatic compensation. |
| Early disclosure | Inputs already disclose the trivial sum; claim/mempool data can also expose work before payment. Suppressing inclusion then refunding is a valid counterexample to strong exchange fairness. Encryption/proofs would require a separate reviewed protocol, not a cosmetic fix. |
| Censorship and deadlines | Trusted Anvil cannot establish permissionless inclusion or honest time. Late funding, congestion, transaction ordering, clock influence or partitions may eliminate a useful claim interval. Do not reinterpret send time as inclusion time or extend signed deadlines after a failure. |
| Replay and authority | Separate experiment domain, deployment/run, parties, terms/policy, consumed nonce, cap and exclusive terminal state are sensible controls, pending actual interoperability/adversarial evidence. Revocation-before-fund blocks authority; afterward it cannot cancel an agreed funded obligation. |
| Objective versus subjective | Exact sum is checkable, but does not prove effort, unique contribution, outsourcing benefit, AI quality, sensor truth or human demand. Repeated valid agreements may pay for identical work; that is not global work uniqueness or an issuance rule. |
| Independent-chain compatibility | Portable requirements are bounded signed consent, immutable terms, deterministic verification, liabilities, ordered terminal transitions and observable evidence. EIP-712/EOA addresses, EVM gas/time and Anvil finality are fixture choices; a future L1 needs its own reviewed encoding, replay domains, resource limits, time and finality semantics. No automatic portability or EVM commitment follows. |

## Specification amendments recorded in this task

1. H2-C now promises **at most one** terminal outcome and conditional refund availability, not automatic closure. A live authorized refund transaction must be canonically included; withdrawal is separately evidenced.
2. Separate contract claim safety from provider progress. Measure from observation of canonical funding through first submission, inclusion, credit and withdrawal. Count all attempted runs, including censorship, late funding, key loss and inconclusive RPC/reorg cases; do not report a success percentage only over already successful inclusions.
3. Add late-funding/non-inclusion, no-live-actor and repeated-work controls to the existing adversarial plan. Preserve strict signed deadlines and the original Experiment 001 control. No new settlement mechanism is introduced.

## Required adversarial evidence

Retain all T01–T17 cases: requester refusal/shutdown; false results; all-field signature/domain/policy/party mutations; malformed encodings; nonce/terminal replay; revocation order; exact expiry boundaries; outsiders; caps/accounting/reentrancy; RPC ambiguity; crashes; malformed transport; disclosure without payment; rollback and cleanup. New T18–T20 specifically cover late funding/claim-time scarcity, a funded expired record with no caller (still Funded until an authorized refund), and repeated separately authorized identical work (not proof of scarce contribution). All are **planned**, not passed.

Mandatory negative controls must remain visible even if core safety passes. Synthetic clock/censorship injection explores consequences under assumptions; it does not measure decentralized attack resistance. The full [test plan](EXPERIMENT_002_TEST_PLAN.md) specifies assertions and metrics.

## Implications for the three pillars

- **Verifiable Autonomous Work:** Experiment 001 shows bounded authority/result verification; Experiment 002 would test payment conditional on an objective result without a second approval. Neither verifies useful, unique resource contribution or AI mining eligibility.
- **Independent Network Security:** replay, accounting and ordering requirements inform a future settlement specification. Single-node Anvil, two keys and arithmetic provide no consensus, Sybil-resistance, finality or censorship-resistance evidence. A thousand AI agents under one owner are not a thousand independent security resources.
- **Human and Machine Economy:** explicit human/operator consent and service settlement are building blocks for human-to-human, human-to-machine and machine-to-machine use. Neither experiment demonstrates native-token demand, sustainable fees/issuance, fair distribution or repeat human utility. Synthetic ETH is not a Genesis native token.

[ADR 0003](../adr/0003-independent-l1-research-direction.md) records the founder's independent-L1/native-economy research goal. Experiments must preserve it without pretending they validate it. Future compatibility means requirements can inform design, not that this escrow can be transplanted unchanged.

## Readiness gates and next task

Before implementation: **R1** explicitly accept the narrowed conditional-collectability scope and upfront-consent policy, including disclosure/deadline limits; **R2** freeze exact schemas, cross-language digest vectors, concrete code/run checks and bounded local timing/recovery fixtures; **R3** review/pin maintained dependencies, compiler/tool references and installation/test commands, mapping every P2 property and T01–T20 scenario to intended evidence. ADR 0002 stays Proposed until these gates are recorded and a separate task authorizes implementation.

Recommend a small **Experiment 002 specification-finalization task** next, closing R1–R3 and making an explicit accept/reject decision. If accepted, a later scoped task may implement an isolated escrow first, preserving Experiment 001 unchanged. General confidential fair exchange, useful-work/mining eligibility, AI-Sybil security and native-economy sustainability remain separate research programs; they need not be solved to test the narrow claim, but must not be inferred from it.

## Task 007 follow-up

[Final specification](EXPERIMENT_002_FINAL_SPEC.md) supplies R2's exact schemas/interfaces and checked public signature fixtures. Conditional collectability remains the narrow proposed question. ADR 0002 stays Proposed because B-DEP and B-FEE remain explicit blocking release decisions; see the [dependency assessment](EXPERIMENT_002_DEPENDENCY_REVIEW.md). This follow-up does not retroactively change the Task 006 review or supply implementation/audit evidence.

## Task 008 subsequent decision

The historical Task 006/007 review is preserved above. [Task 008 blocker resolution](EXPERIMENT_002_BLOCKER_RESOLUTION.md) records tested constrained baseline reuse and an explicit finite fee model; ADR 0002 is now Accepted for bounded local design only, READY for separate implementation authorization. The public disclosure, conditional inclusion/refund, useful-work and economic limitations remain. No Experiment 002 implementation/audit/result or final Genesis architecture follows.
