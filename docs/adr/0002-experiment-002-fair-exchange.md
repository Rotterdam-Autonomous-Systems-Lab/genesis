# ADR 0002: Direct-Predicate Fair-Exchange Baseline

- **Date:** 2026-10-18.
- **Status:** **Accepted for bounded local experimental design — Task 008; implementation requires separate authorization.**
- **Scope:** separate, synthetic, local Experiment 002; no Experiment 001 change or future network commitment.

## Context

The [published Experiment 001 report](../../research/reports/EXPERIMENT_001_REPORT.md) records CONDITIONAL PASS and a requester veto: correct work does not settle without a subsequent requester Acceptance. [Prior-art research](../../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md) compares six established families. Neither cryptographic commitments nor an off-chain assertion by itself proves correct work or fair payment.

## Proposed decision

Investigate an immutable, directly verifiable public arithmetic predicate with **upfront dual-signed contingent payment consent**, replacing the second requester approval in a distinct experiment. Once canonically funded, only the intended provider can claim the exact price for a valid bound result included before deadline. Requester silence or shutdown cannot veto it. No timely claim permits full requester refund at/after deadline. Revocation applies to unused authority, not funded obligations. Use the concrete [architecture](../architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat assumptions](../experiments/EXPERIMENT_002_THREAT_MODEL.md) and [test plan](../experiments/EXPERIMENT_002_TEST_PLAN.md).

Propose local Anvil/Ethereum tooling for controlled comparison only. This does **not** commit Genesis to Ethereum, an EVM-based final chain, any consensus algorithm or asset. The broader independent permissionless infrastructure direction remains open.

## Alternatives and rationale

- **Keep post-result Acceptance:** retains requester discretionary consent but cannot remove the observed veto; remains the unchanged Experiment 001 control.
- **Optimistic challenges/fraud proofs:** relevant for expensive deterministic work, but adds monitoring, data availability, bonds and dispute-window assumptions unnecessarily for addition.
- **FairSwap-style encrypted goods:** targets committed digital delivery and objective complaints; adapting it to unknown computations needs additional reviewed correctness binding.
- **Trusted exception resolver/arbitration:** can resolve specified disputes but adds authority, censorship and evidence/judgment trust.
- **Payment channels/HTLCs:** reduce repeated payment interactions; a preimage alone is not proof of correct service.
- **Computation proofs/zkVM:** potentially useful for expensive programs; too much proving/verifier complexity for the initial veto-isolation baseline.

Direct verification minimizes new assumptions and isolates a single consent variable. It is a research baseline, not a claim of protocol novelty, economic efficiency or generally solved fair exchange.

## Security trade-offs and reversibility

A must deliberately authorize the fixed objective policy before funding; there is no subsequent subjective satisfaction veto or early funded cancellation. Correctness is limited to the agreed predicate. Public inputs/results are visible, and result disclosure followed by censorship/expiry can leave B unpaid. Timely canonical inclusion, host/ledger behavior, key custody and exact accounting are assumptions or implementation obligations, not eliminated trust. No gas/effort compensation, subjective quality guarantee or physical-world truth is provided.

The proposal and eventual isolated prototype are reversible and disposable; they do not alter Experiment 001 evidence or choose irreversible network/economic architecture. Retain both positive and negative results. No code, deployment, dependency adoption or production permission is authorized by this ADR.

## Open questions and approval gate

Review whether conditional collectability rather than strong exchange fairness is the right bounded question; accept/reject the upfront-consent change and leakage/deadline limitations explicitly. Review/freeze proposed schemas, digest vectors, tested dependency references and reproducibility commands before a separately authorized implementation. Useful workloads, confidential delivery, expensive verification, intermittent connectivity and future ledger requirements remain open research topics. The historical Task 006/007 gate findings are preserved below. The Task 008 disposition supersedes their readiness status; no Experiment 002 implementation or outcome exists.

## Task 006 design review — 2026-10-18

**Disposition: amend and remain Proposed; not accepted or implementation-ready.** The [review report](../experiments/EXPERIMENT_002_DESIGN_REVIEW.md) finds this useful as a controlled veto-isolation baseline, but not a general provider-payment guarantee. H2-C is amended to exclusive outcomes and conditional refund availability: no actor/inclusion means no automatic closure. Add explicit provider-progress measurements and late-funding/no-caller/repeated-work controls, retaining all existing planned tests.

Outstanding gates R1–R3 are recorded scope/consent acceptance, frozen schemas/vectors and timing/recovery checks, and reviewed immutable dependency/test setup. Keeping the candidate is justified by cheap objective verification and fewer new trust roles; disclosure, censorship/deadlines, unique useful work and native-economy claims remain objections to broader acceptance. [ADR 0003](0003-independent-l1-research-direction.md) confirms research direction only and does not accept this experiment. No Experiment 001 semantics or evidence change.

## Task 007 specification finalization — 2026-10-18

**Status remains Proposed; implementation readiness BLOCKED.** The [final specification](../experiments/EXPERIMENT_002_FINAL_SPEC.md) freezes exact signed/wire schemas, interfaces, funding/verification/claim/refund/accounting/retry rules, concrete [public vectors](../experiments/EXPERIMENT_002_SIGNING_VECTORS.md) and acceptance criteria. R2's schema/vector work is supplied and the narrowed conditional-collectability scope is retained as the experimental question; this is no implementation authorization or general fairness acceptance.

[B-DEP](../experiments/EXPERIMENT_002_DEPENDENCY_REVIEW.md) requires an exact reviewed compatible dependency tuple or documented constrained reuse. **B-FEE** requires a finite operator fee/run-cost ceiling separate from signed service principal. Neither is silently resolved with arbitrary new versions or economic parameters. No replacement packages, new cryptography, token or consensus mechanism is adopted. Review these actionable gates before any separate implementation task; useful-work/native-economy research proceeds independently.

## Task 008 disposition — 2026-10-18

**Accepted for bounded local experimental design; READY for a separately authorized implementation.** [Blocker resolution](../experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md) resolves B-DEP by constrained baseline reuse with tested toolchain/lock, offline rebuild, original 58 Solidity/54 Python regressions, 25 Cast digests and 34 EVM/Python signature recoveries. [Bounded costs](../experiments/EXPERIMENT_002_BOUNDED_COST_MODEL.md) resolve B-FEE with the existing 3 gwei/1 gwei fee limits, 2,000,000 gas ceiling, explicit role/attempt/total budgets, no top-ups/fee escalation and measured controls.

The decision accepts upfront predicate consent for veto isolation because it removes the second approval with a minimal objective checker and keeps invalid-result, cap, replay and refund obligations. Alternatives and the disclosed public-result/inclusion/finality/key/host limitations remain unchanged. Compatibility and finite budgets support attempting implementation, not concluding general fairness or economic/security success. Retaining an old dependency tuple is an explicit disposable local-only risk decision, subject to source restrictions; not a clean audit or production endorsement.

Mandatory implementation acceptance: preserve the final specification/vector schemas, review all new source against compiler/library restrictions, enforce signer/run budgets and cleanup, measure gas below fixed ceilings, run all T01–T20/cost cases and unchanged controls, and verify canonical settlement/withdrawal. Reopen B-DEP/B-FEE for scope/feature/budget changes rather than silently increasing risk. Task 008 implements none of these protocol components and authorizes no deployment, production asset, consensus mechanism or autonomous public activity.
