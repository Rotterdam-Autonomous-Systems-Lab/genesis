# Genesis Project Context

## Task 018 current status — adversarial review and fixture freeze

[Review/readiness](architecture/NATIVE_L1_SPEC_REVIEW.md): **READY FOR COMPARATIVE MODELS**, no candidate selected/eliminated. [V1 fixtures](../research/fixtures/native_l1/README.md) freeze 21 signed core vectors plus nine stress configurations; [adapter](architecture/NATIVE_L1_ADAPTER.md) and [measurements](architecture/NATIVE_L1_MEASUREMENTS.md) define Task 019. Authority-before-fee, atomic solvency, structural-versus-logical conflicts, fenced recovery and sum-only service semantics are clarified. Nine integrity tests pass; no candidate transitions executed. Native permissionless security and authenticated finality remain open. Earlier statuses below are historical.


## Task 017 current status — comparative specification, no implementation

[Workloads W01–W08](architecture/NATIVE_L1_WORKLOADS.md), [authority/settlement/recovery](architecture/NATIVE_L1_AUTHORITY_SETTLEMENT_RECOVERY.md), [consensus premises](architecture/NATIVE_L1_CONSENSUS_ASSUMPTIONS.md), [budgets](architecture/NATIVE_L1_RESOURCE_BUDGETS.md) and [proposed experiment](architecture/NATIVE_L1_NEXT_EXPERIMENT.md) define a common bounded evaluation framework. Caps are proposed lab controls, not native capabilities; model ordering/checkpoint oracle does not solve consensus. Shared grant reserves, stable logical intents and durable recovery must be compared at identical semantics. No candidate eliminated; G0 independent review/vector/adapter freeze pending, G1 unrun. Recommend separately authorized Task 018 reference models after that freeze; no native devnet/token/monetary policy or final design selected. MASTER_PLAN and both experiments preserved.

## Task 016 current status — native architecture research, no selection

[Native L1 foundations](architecture/NATIVE_L1_RESEARCH.md), [matrix](architecture/NATIVE_L1_DECISION_MATRIX.md), [risks](architecture/NATIVE_L1_RISKS.md) and [proposed gate](architecture/NATIVE_L1_DECISION_GATE.md) compare accounts, objects and extended UTXO with execution and consensus as separate axes. Experiment 002 is [BOUNDED CONDITIONAL PASS — READY TO CLOSE](experiments/EXPERIMENT_002_FINAL_REVIEW.md); native consensus, useful-work scarcity, secure offline recovery and real demand remain unverified. Next recommendation: comparative authority/settlement/recovery specification, then separately authorized bounded models. No final architecture, asset, monetary policy, chain implementation or discovery capability selected. MASTER_PLAN and all experiment/security boundaries are preserved; older statuses below are historical.

## Task 014 current status — remediation pending re-review

[Evidence/workflow remediation](experiments/EXPERIMENT_002_REMEDIATION.md) implements owner/state reconstruction, pinned/repeated observations, full receipt/own-intent consistency and sticky submission failure, shared cooperative deadlines, and controlled last-valid late funding with failure diagnostics. Existing caps, contract, schemas, Anvil/Cancun profile, Experiment 001 and MASTER_PLAN are unchanged. All prior review scenarios remain as rejection/boundary regressions. Original late-funding CI timing cannot be conclusively reconstructed, but the old scheduling-sensitive mechanism reproduces and current fixture controls inclusion without extending terms. **Independent re-review may proceed after required publication CI; acceptance/closure is not automatically granted.** Earlier statuses below are historical.

## Task 013 current review status — closure blocked

[Experiment 002 adversarial review](experiments/EXPERIMENT_002_INDEPENDENT_REVIEW.md) confirms two medium evidence-validation defects (credit-owner allocation and contradictory RPC re-reads) and a low wall-deadline coverage gap. The no-second-requester-signature demonstration remains reproducible, with no confirmed unauthorized payout/cap bypass, but full security/evidence closure is BLOCKED pending minimal hardening and review. Task 012 CONDITIONAL PASS remains historical, not upgraded to PASS. R013-04 additionally preserves an initial review CI failure in the existing late-funding setup; the exact failed inclusion timestamp is unavailable and reproducibility remains open. Only review documentation and seven characterization/control tests changed; experiments, limits and MASTER_PLAN remain intact. Next recommended task is separately authorized evidence/deadline hardening, not another experiment or architecture expansion.

## Task 012 current status — local integration completed

[Experiment 002 integration assessment](experiments/EXPERIMENT_002_AGENT_ACCEPTANCE.md) records **CONDITIONAL PASS**, subject to the publication commit CI: separate requester/provider processes settle objectively correct, timely included work without a second requester authorization. The exact ADR 0005 Anvil/Cancun profile, existing contract, signatures and principal/fee/wallet/run limits remain unchanged. Experiment 001 remains unchanged and conditionally accepted. Public disclosure, censorship/deadlines, absent callers, rollback, trusted host/RPC and supply-chain limitations remain. Earlier milestone statuses below are historical, superseded in sequence; no native-chain/token/consensus/adoption result follows. Next recommendation: independent review and separately selected research question, not automatic implementation expansion.

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

## Task 011 current status — corrected infrastructure profile validated

[Validation](experiments/EXPERIMENT_002_ANVIL_VALIDATION.md) and [ADR 0005](adr/0005-experiment-002-corrected-anvil-baseline.md) select isolated Anvil v1.6.0-rc1 / b272ce3366987406406e9eb1b82596653a3ad628, explicit Cancun, with source/archive/binary hashes. Local compatibility is PASS; publication Ubuntu CI is mandatory. When it passes, the reporting blocker is resolved for this profile. Original node remains the negative control; Forge/Cast/compiler/libraries/Python and all fee/authority limits are unchanged. Official artifacts were verified; no successful attestation/reproducible-build claim.

The same 22-case matrix now gives 20 reconciled/two unincluded, versus eight reporting contradictions on the old node. All 86 Solidity tests, 54 Python tests on each node, signatures/fee arithmetic and old/new research tests pass locally. Green compatibility is not Experiment 002 acceptance: incomplete agents stay paused, and full T01–T20/P2/fee/resource integration remains the next implementation dependency. Do not silently replace Experiment 001's default tools or infer production/native-network security.

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
