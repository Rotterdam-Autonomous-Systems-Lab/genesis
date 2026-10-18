# Genesis Project Context

## What Genesis is

Genesis is RASL’s temporary-codename, open-source, research-first initiative exploring foundational infrastructure for economic coordination among autonomous intelligences and systems. Task 006 explicitly sets an independent permissionless AI-first Layer 1 blockchain economy with a native asset as the long-term research goal. Investigate AI mining/earning through independently verified contributions and meaningful human-to-human, human-to-machine and machine-to-machine utility for the same network/asset. The mission spans humans, software agents, robots, machines, vehicles, sensors, satellites, distributed systems, and future entities. This is research direction, not a validated chain or native-token implementation. The central question is whether unfamiliar, independently operated participants can establish verifiable agreements, exchange resources, and coordinate safely without trusting each other or a central platform.

## What Genesis is not

Genesis is not only an AI-agent payment application. It is not currently a production blockchain, token, wallet, smart-contract system, or autonomous network. No new consensus protocol or cryptographic primitive has been invented or validated here. A Bitcoin-scale foundational ambition is an aspiration, not an achievement or novelty claim.

## Current research status and milestone

Status: early-stage experimental research. Current milestone: project foundation and prior-art mapping, with a small, bounded two-agent independently verifiable economic transaction experiment identified as the first implementation milestone. It is a first step, not the long-term product definition. Any experiment requires a scoped task, synthetic actors/data, and explicit validation criteria. Task 002B now provides a proposed, implementation-oriented [Experiment 001 specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), and [security invariants](SECURITY_INVARIANTS.md). Task 003A implements and locally tests the Solidity escrow only, with pinned dependencies and GitHub CI. [ADR 0001](adr/0001-experiment-001-architecture.md) is accepted for that component; [coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) lists remaining invariant integration checks. Task 003B adds separate-process Python requester/provider agents and local Anvil end-to-end tests, preserving requester veto. See [local reproduction](../sdk/python/README.md) and the coverage map for tested and pending cases. Task 003C records a [project-assisted adversarial review](experiments/EXPERIMENT_001_SECURITY_REVIEW.md) and CONDITIONAL PASS for this bounded local experiment. Task 004 publishes the [Experiment 001 research report](../research/reports/EXPERIMENT_001_REPORT.md) with immutable evidence and reproduction instructions. The result remains conditionally accepted; independent review and documented residual conditions remain open. Task 005 now provides a [fair-exchange comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md) and **Proposed** [Experiment 002 design](experiments/EXPERIMENT_002.md): upfront consent to a fixed result predicate, with no post-funding requester veto for timely valid claims. This is a separate consent policy, not a change to Experiment 001. Public-result leakage, non-inclusion and deadlines still prevent a general fairness guarantee. [Task 006 design review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md) amends the closure/progress claims and keeps [ADR 0002](adr/0002-experiment-002-fair-exchange.md) Proposed, not implementation-ready. Specification finalization must close R1–R3 before separate implementation authorization. Task 007 now supplies the [final technical proposal](experiments/EXPERIMENT_002_FINAL_SPEC.md) and checked [public signature/state fixtures](experiments/EXPERIMENT_002_SIGNING_VECTORS.md); readiness is BLOCKED by dependency selection/constrained reuse and finite local operator fee policy. A separate [AI-earned native-token/economic research foundation](../research/economics/AI_EARNED_NATIVE_TOKENS_AND_UTILITY.md) distinguishes service earnings, issuance and security rewards and proposes token-free hypotheses. No Experiment 002 implementation results exist. No public-chain or future Genesis consensus result is established.

## Task 008 current readiness and bootstrapping direction

[Compatibility/blocker review](experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md) resolves B-DEP through constrained tested baseline reuse. [Bounded costs](experiments/EXPERIMENT_002_BOUNDED_COST_MODEL.md) resolve B-FEE with explicit principal/fee/run budgets. The baseline already had 3 gwei maximum/1 gwei priority-fee fields; Task 007 overlooked them. ADR 0002 is now **Accepted for local design; READY for separate implementation authorization**, superseding the historical Proposed/BLOCKED status above. No Experiment 002 code or execution result exists.

[ADR 0004](adr/0004-autonomous-bootstrapping-research-direction.md) preserves the aspiration that agents eventually discover opportunities, onboard safely within bounded authority, contribute verifiable work and earn/spend native tokens, with genuine observable activity a potential path to organic human adoption. No current automatic discovery, token monetary value or adoption guarantee is claimed. Do not fabricate wallet activity/trades/signals; label synthetic tests. The [five bootstrapping research scopes](../research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md) are plans only.

## Task 009 current status — implementation stopped on evidence blocker

Task 009 separately authorized bounded local implementation. An [isolated Solidity escrow and 28 new tests](experiments/EXPERIMENT_002_IMPLEMENTATION_REVIEW.md) are published; original Experiment 001 code/evidence remain unchanged. Total local Solidity regressions: 86 passed. Experiment 002 acceptance is **FAIL / implementation BLOCKED**, superseding Task 008 READY: pinned Anvil reports effectiveGasPrice above the signed cap while the actual debit obeys it. This breaks required canonical fee reconciliation; it does not demonstrate excess wallet spending. See [the reproducer](../research/compatibility/experiment002/check_anvil_fee_receipt.py).

No complete Experiment 002 agent workflow is released. The partial agent draft is local-only under ignored internal notes; all mandatory integrated scenarios/cost controls still require reviewed evidence. ADR 0002 remains accepted design only. Do not silently upgrade dependencies, replace canonical fee evidence, raise budgets or claim acceptance. Next recommended task is independent reproduction/root-cause and explicit dependency/evidence-policy review, then resume implementation only after the blocker is resolved.

## Task 010 current status — root cause diagnosed, still blocked

The [fee investigation](experiments/EXPERIMENT_002_FEE_INVESTIGATION.md) reproduces the discrepancy through raw JSON-RPC, sender balances and an EVM GASPRICE/BASEFEE witness. The pinned Anvil source omits the total-fee clamp in mined receipt and transaction reporting; actual charges respect the cap. Two clean runs of 11 cases give 12 reconciled, eight contradictory and two not included. The strict checker still rejects contradictions; no fee cap, signature, escrow or agent policy changed.

**STILL BLOCKED:** an upstream source correction and a source-reviewed v1.8.5 candidate exist, but the one candidate binary download timed out and failed integrity validation. It was never executed/adopted. The original baseline and Experiment 001/002 regressions are preserved. The incomplete agents remain paused; do not infer readiness from green discrepancy-characterization CI. Next task is verified corrected-node acquisition and full compatibility review, followed by an explicit dependency decision before implementation resumes.

## Core principles

“The network must not need to trust the intelligence of its participants. It must only need to verify their actions.” Treat this as a research principle, not a proven universal property. Prioritize bounded cryptographic authority, security, verifiability, interoperability, open participation, privacy, resilience, and honest reporting of uncertainty.

## Major decisions

RASL is the research organization; Genesis is temporary codename; development is open-source and research-first; planning uses Verifiable Autonomous Work, Independent Network Security and Human and Machine Economy, with the original Autonomous Economic Authority, Verifiable Coordination and Autonomous Network Security tracks retained as technical methods; no premature token or consensus claims; no uncontrolled autonomous replication or unauthorized infrastructure use; and no permanent Ethereum commitment. There is no selected network name, ticker, consensus algorithm, tokenomics, or final architecture.

[ADR 0003](adr/0003-independent-l1-research-direction.md) records the founder-defined independent-L1/native-economy research direction. Seek adaptability to future AI, computing, robotics, cryptography and communications; never guarantee complete future-proofing. See [`DECISION_REGISTER.md`](DECISION_REGISTER.md) for the canonical register.

## Unresolved decisions

Whether the target independent L1/native economy is justified and viable compared with alternatives; the native asset's concrete utility/design; which consensus or non-consensus architecture fits requirements; whether useful contribution can be measured and where it belongs; how authority, discovery, execution, governance, upgrades, and offline operation should work; and which permanent name is suitable. APoC is only an internal research hypothesis.

## Canonical documents

- [`MASTER_PLAN.md`](../MASTER_PLAN.md) — canonical project charter and boundaries.
- [`DECISION_REGISTER.md`](DECISION_REGISTER.md) — established decisions and unresolved choices.
- [`FUTURE_NETWORK_ARCHITECTURE.md`](FUTURE_NETWORK_ARCHITECTURE.md) — architecture research territory.
- [`RESEARCH_SPEC.md`](RESEARCH_SPEC.md) and [`PROTOCOL_HYPOTHESES.md`](PROTOCOL_HYPOTHESES.md) — research methods and falsifiable hypotheses.
- [`THREAT_MODEL.md`](THREAT_MODEL.md) — initial threat inventory.
- [`ROADMAP.md`](ROADMAP.md) — conditional research gates.
- [`research/history/ORIGINAL_BRAINSTORM.md`](../research/history/ORIGINAL_BRAINSTORM.md) — recovered brainstorm; not approved architecture.
- [`research/history/CONTEXT_RECOVERY.md`](../research/history/CONTEXT_RECOVERY.md) — how to reconstruct project context.
- [`research/history/NAMING_AND_IDENTITY.md`](../research/history/NAMING_AND_IDENTITY.md) — explored names and naming boundary.

## Recover context in future sessions

Read this guide, then read `MASTER_PLAN.md` and `docs/DECISION_REGISTER.md`. Use ADRs for accepted architectural decisions. Consult the history archive for origin and rejected or deferred ideas, but do not treat brainstorm entries as approvals or as verbatim historical records. Check current `git status`, recent commits, and open research tasks before acting. Separate established techniques, project assumptions, hypotheses, and findings. Update all affected canonical documents when an approved decision changes. After significant tasks, update [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) with current status, completed work, open questions, next task, blockers, relevant commits, and canonical links. See `research/history/CONTEXT_RECOVERY.md` for details.
