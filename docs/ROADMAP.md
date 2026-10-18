# Conditional Research Roadmap

These stages are conditional research gates, not release promises or a commitment to ship a blockchain. Each stage can be delayed, changed, or stopped. A negative result is a valid outcome. No stage authorizes production use, real funds, or unauthorized infrastructure.

## Three connected pillars

The founder's Task 006 instruction makes an **independent permissionless L1 blockchain economy with a native asset** the architectural research goal; [ADR 0003](adr/0003-independent-l1-research-direction.md) records the boundary. AI systems may mine or earn through independently verified contributions only if verification, useful-work, consensus, Sybil and economic research justify a mechanism. Human utility for that same network/asset is central, including human-to-human, human-to-machine and machine-to-machine exchange. No token parameters, launch or economic outcome are approved.

| Pillar | Central question | Required evidence / dependencies |
| --- | --- | --- |
| **1. Verifiable Autonomous Work** | How can autonomous participants make verifiable contributions and earn value? | Objective task/result criteria, independent verification cost, usefulness/uniqueness and demand; collusion/fake-work tests. Separate valid service payments, reward eligibility and consensus weight. |
| **2. Independent Network Security** | How can a permissionless L1 secure consensus and resist Sybil attacks, including large AI-agent swarms? | Scarce-resource/operator threat models, safety/liveness/finality and censorship analysis, attack cost, concentration, accessible independent validation. Identity count alone is insufficient. |
| **3. Human and Machine Economy** | Why would humans and machines repeatedly use the native token, and could fees, incentives, issuance and activity remain sustainable? | Concrete human/machine utility, affordability and consent; compare existing assets/non-token systems; adverse demand, security-budget and distribution analysis. No demand/adoption guarantee. |

The original authority, coordination and network-security tracks remain technical methods across these pillars. Long-term adaptability across AI, computing, robotics, cryptography and communications is cross-cutting; test interfaces, migration, client diversity and delay assumptions rather than promise future-proofing.

## Stage-to-pillar evidence map

All three pillars must remain visible as stages progress; service-exchange success cannot substitute for network or economic evidence. This map organizes the unchanged conditional stages below.

| Stages | Verifiable Autonomous Work | Independent Network Security | Human and Machine Economy |
| --- | --- | --- | --- |
| 0 | Prior art, objective contribution classes and verifier assumptions. | Independent-L1 requirements, consensus baselines and AI-Sybil attacker budgets. | Candidate human/machine needs, native-asset rationale and non-token controls. |
| 1–2 | Bounded agreements/result checking, refusal and failure evidence. | Settlement/replay/accounting requirements only; no consensus or Sybil result. | Operator consent and synthetic settlement only; no adoption, issuance or demand result. |
| 3 | Discovery, negotiation and coordination evidence. | Discovery poisoning, AI swarms, open access and operator concentration. | Matching/access/friction for human and machine roles. |
| 4 | Useful contribution, uniqueness, verification/production cost and fake-work tests. | Determine whether contribution belongs in consensus, rewards or a market. | Compare service fees and issuance/subsidy costs; real usefulness remains to be demonstrated. |
| 5–6 | Specify task/verifier interfaces from evidence. | Analyze consensus/Sybil/finality/censorship and independent-L1 architecture; no novelty required for a valid baseline. | Model sustainable security budgets, demand and distribution without selecting premature parameters. |
| 7–8 | Reproducible implementations and adversarial/independent review. | Local multi-node faults, client/operator diversity, then only separately authorized testnet review. | Synthetic economics and reviewed user/operational evidence; do not equate test activity with adoption. |
| 9–10 | Ongoing contribution correctness, accessibility and utility. | Separately approved production security, decentralization and verifiable upgrades. | Continuing demand, affordability, fee/incentive/issuance risks, distribution and capture monitoring. |

## Conditional stages

| Stage | Prerequisites | Deliverables | Measurable exit criteria | Major risks |
| --- | --- | --- | --- | --- |
| **0. Project foundation and prior-art research** | Charter and evidence labels adopted. | Research questions, annotated prior-art map, threat model, experiment standards. | Each core track has bounded questions, cited references, stated gaps and search limits; threat review identifies key assumptions. | Premature narrowing, missed prior art, unexamined assumptions. |
| **1. First independently verifiable autonomous economic transaction** | Stage 0 question and threat scope reviewed; synthetic actors and bounded sandbox. | Small two-agent transaction experiment with a documented agreement, constrained authority, verifiable outcome, and reproducible method. | Independent verifier can accept/reject according to predeclared criteria; compromised/misbehaving actor scenarios are reported; no real funds or production services. | Framing project as payment-only, unverified real-world claims, unsafe autonomy, overfitting to one platform. |
| **2. Adversarial validation and security testing** | Stage 1 artifacts and limits documented. | Threat-driven tests, attack analysis, failure report, prioritized mitigations or negative result. | Defined adversarial scenarios are reproducible; verification behavior and residual risks documented; independent review completed for in-scope claims. | False confidence from a narrow test set, undiscovered interactions, brittle assumptions. |
| **3. Permissionless discovery and multi-agent coordination** | Clear identity/authority boundary; discovery threat model; offline assumptions. | Bounded discovery/coordination experiment involving multiple synthetic participants and independent implementations where feasible. | Measure discovery success, cost, censorship, Sybil resistance assumptions, and recovery under delay/partition; results reproduce. | Sybil capture, spam, privacy leakage, hidden directory dependence. |
| **4. Verifiable useful-contribution experiments** | Contribution candidate and objective evidence defined; adversarial baseline. | Narrow experiments for selected resources such as computation, storage, bandwidth, sensing, or verification. | Report false-claim rate, verifier cost, attack cost, collusion outcomes, and comparison with service-market alternatives. | Fake work, oracle dependence, reward gaming, contribution does not help security. |
| **5. Novel consensus feasibility research** | Prior-art review and security requirements; evidence from stages 2–4. | Formalized candidate protocol hypothesis and feasibility analysis, or documented reason to stop. | Novelty search documented; safety/liveness assumptions stated; known attack models analyzed; independent experts review. | Rebranding known work, unprovable guarantees, economic attacks, complexity exceeding benefit. |
| **6. Independent network architecture research and specification** | Evidence that independent architecture may meet a demonstrated need; alternatives compared. | Architecture options, requirements, threat model, execution/economic/network analyses, draft specification. | Candidate design compared against existing networks and non-chain options; decision record includes alternatives, risks, evidence, and unresolved issues. | Building a chain without need, unsuitable asset assumptions, architecture lock-in. |
| **7. Experimental implementation and local multi-node network** | Reviewed specification, scoped prototype authorization, isolated environment and synthetic data. | Non-production implementation, local multi-node harness, reproducible tests and operational documentation. | Nodes synchronize and validate under defined fault scenarios; reproducibility and security limits documented; no external public deployment. | Prototype mistaken for secure software, unsafe key handling, implementation divergence. |
| **8. Public testnet and independent security review** | Stage 7 evidence, explicit authorization, public threat and operations plan. | Public test network, independent security reviews, remediation records, monitoring and incident process. | Reviews published or summarized; critical findings addressed or explicitly accepted; safe reset, rate limits, and participant guidance tested. | Public harm, abuse, real-value confusion, unbounded infrastructure costs. |
| **9. Potential production network, only if justified** | Evidence of necessity and maturity; independent reviews; governance, legal, and operational readiness. | Decision dossier and, only if approved, production launch plan. | Explicit approval after security, economic sustainability, decentralization, governance, recovery, and operational criteria are met. | Irreversible losses, regulatory exposure, capture, unmanageable incident response. |
| **10. Long-term decentralization, governance, and protocol evolution** | Any production deployment would require prior authorization and a continuing public process. | Ongoing decentralization measures, governance and upgrade records, compatibility and migration research. | Periodic measurements of operator/client diversity, concentration, participation, upgrade authority, and recovery; public review of changes. | Governance capture, ossification, upgrade coercion, misleading decentralization metrics. |

## Stage transition rule

A stage does not automatically authorize the next. Publish the evidence and limitations, review threats and prior art, update `docs/DECISION_REGISTER.md` and relevant ADRs, and obtain explicit authorization for implementation or external deployment when required. Stage 1 is an initial research experiment, not the project’s ultimate purpose.

## Experiment 001 implementation prerequisites

Task 002B supplies a proposed [experiment specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), [security invariants](SECURITY_INVARIANTS.md), and [ADR 0001](adr/0001-experiment-001-architecture.md). This is specification progress within the early research gates, not completion of Stage 0, Stage 1, or the long-term network program.

Before any implementation, define a separate bounded task, finish the focused prior-art comparison, review the proposal and threat assumptions, select exact compatible dependency/tool versions and hashes, and map SI-01 through SI-18 to positive/adversarial tests. Use independent ephemeral signers, synthetic ETH, loopback-only Anvil without a public fork, a fresh runId, and documented execution limits. No production or external infrastructure authorization follows from this roadmap.

## Experiment 001 security-review gate

Review must explicitly accept or revise the requester-veto/provider-fairness limitation, on-chain arithmetic plus requester-signed Acceptance, A-only funding/refund, B-only settlement, first-use nonce revocation, immutable funded obligations, strict expiry boundaries, deterministic full refund, retry reconciliation, accounting and withdrawal safeguards. The original Task 002B ADR was Proposed; see the scoped Task 003A progress below for escrow-only acceptance. No critical security behavior is left undefined; no BLOCKING OPEN DECISION is currently recorded in the proposed semantics.

Implementation is a separately authorized task after this gate. Before calling the experiment successful, require:

- At least two clean local runs with separate A/B keys, independently checked result, canonical receipt/state evidence, exact provider credit and successful withdrawal.
- Reproducible deterministic refund runs for absent/invalid result, disagreement, and withheld Acceptance, with exact requester credit and withdrawal.
- Positive and adversarial coverage of all 18 invariants, including signature-field mutation, wrong domain/run/participant, replay, revocation order, timestamp -1/equality/+1 boundaries, invalid result even with A signature, unauthorized callers, reentrancy/transfer failure, and retry ambiguity.
- Identical Python/Solidity digest vectors, bounded inputs and runtime, conservation of principal/credits, and no secret-bearing artifacts.
- A documented security review of the resulting code and test evidence before claiming the in-scope properties, plus negative/inconclusive results and residual-risk disclosure. A local demonstration does not close Stage 2's wider adversarial research program.

Do not describe a specification as an executed result or this local Ethereum-compatible fixture as a final network choice. Stages 3–10 and all independent-network/consensus/native-asset research questions remain intact.

## Task 003A escrow-only progress

Task 003A separately authorizes the Solidity escrow implementation with requester veto preserved. [Dependency pins](../DEPENDENCIES.md), [contract evidence and invariant coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md), and a read-only GitHub Actions workflow now support offline build/tests after tool setup. ADR 0001 is accepted only for this local component. This does not close Stage 0, Stage 1, the full independent review gate, or end-to-end experiment acceptance. Python signer/verifier, discovery, transport/retry handling, local-only endpoint/key controls and full reproducibility evidence remain separate future tasks.

## Experiment 001 publication milestone — Task 004

The [published report](../research/reports/EXPERIMENT_001_REPORT.md) records a bounded Stage 1 service-exchange demonstration and project-assisted Stage 2 adversarial evidence with **CONDITIONAL PASS**, anchored to implementation commit `f66cda91af5cb2f2da266fe11d90bc67c05cfc77` and [passing CI run 39057757966](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966). It reports 58 Solidity and 54 Python tests and preserves unresolved requester-veto fairness, independent review, supply-chain maintenance and fault-coverage conditions.

Earlier escrow-only progress above is historical. Publication does not certify completion of all Stage 0, Stage 1 or Stage 2 gates, and does not narrow Stages 3–10 or the independent-network ambition. The next proposed step is selecting an Experiment 002 research question through a separate design review; no implementation, architecture change or automatic stage transition follows.

## Experiment 002 fair-exchange design proposal — Task 005

The [six-mechanism comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md) and **Proposed** [ADR 0002](adr/0002-experiment-002-fair-exchange.md) supply a focused Stage 0/Stage 2 research question: can upfront consent to a fixed deterministic predicate remove requester veto for timely funded claims? See the [experiment](experiments/EXPERIMENT_002.md), [architecture](architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat assumptions](experiments/EXPERIMENT_002_THREAT_MODEL.md) and [test/acceptance plan](experiments/EXPERIMENT_002_TEST_PLAN.md).

**Prerequisites:** review the explicit change from post-result Acceptance to upfront predicate consent; accept or reject trusted-ledger, public-output and deadline assumptions; freeze schemas, digest vectors, maintained dependency pins and bounded test budgets; separately authorize implementation. Experiment 001's control, published evidence and all existing tests remain unchanged.

**Proposed exit/security-review gate:** at least two fresh separate-process exchanges, refusal/offline-requester collection with timely canonical claims, no invalid/unauthorized/over-cap/replayed payment, deterministic refund and conserved accounting, signature/retry/deadline/fault tests and reviewed reproducibility evidence. Report the intentional output-leakage/non-inclusion counterexample and all inconclusive runs. Strong fair exchange, useful outsourcing and production assurance are not exit claims.

**Status and risks:** design proposal only, not executed or accepted. Misspecified predicates, expensive verification, censorship, late claims, key loss and communication failures remain risks. No automatic stage completion or next-task authorization follows; Stages 3–10 and independent-network/consensus/native-asset research remain intact.

## Task 006 review disposition

[Experiment 002 design review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md): **amend and remain Proposed**, not implementation-ready. H2-C now distinguishes exclusive outcomes/refund availability from automatic progress. T18–T20 add late-funding, absent-caller and repeated-work controls; all earlier planned tests remain. Close R1–R3 (scope/consent, schema/vector/timing freeze, reviewed pinned dependencies and evidence mapping) in a small specification-finalization task before separate implementation authorization. No stage completion, native-token result or consensus conclusion follows.

## Task 007 technical and economic research foundations

[Experiment 002 final specification](experiments/EXPERIMENT_002_FINAL_SPEC.md) adds exact interfaces/rules, [public signed/state vectors](experiments/EXPERIMENT_002_SIGNING_VECTORS.md), an acceptance gate and [dependency assessment](experiments/EXPERIMENT_002_DEPENDENCY_REVIEW.md). ADR 0002 remains Proposed; **BLOCKED** pending reviewed compatible dependency selection/constrained reuse and finite operator gas-fee/run-cost policy. Vector hash/recovery checks are documentation evidence, not executed Experiment 002 tests. Next technical task: resolve B-DEP/B-FEE, review ADR and separately authorize implementation only afterward.

The separate [economic research foundation](../research/economics/AI_EARNED_NATIVE_TOKENS_AND_UTILITY.md) links Stage 0 prior art to Stage 4 work/reward eligibility, Stages 5–6 security coupling and the Human and Machine Economy pillar. Prioritize E-01 correctness/uniqueness/demand separation and E-02 fixed-resource AI-Sybil amplification models, then E-03 subsidy/security-budget sensitivity and E-04 native versus stable-value settlement stress. E-05 compares consensus/reward decoupling. Prerequisites: one bounded candidate, reviewed assumptions, baselines, units/seeds/budgets and falsification criteria; no token or simulation implementation is authorized. Exit evidence must report verification/attack costs, repeated/fake work, collusion, real-demand assumptions and negative outcomes, not speculative price or subsidized-volume claims. All earlier stages/risks remain intact.

## Task 008 resolved design gates and bootstrapping scopes

[B-DEP/B-FEE resolution](experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md) and [bounded costs](experiments/EXPERIMENT_002_BOUNDED_COST_MODEL.md) supersede Task 007's readiness status. ADR 0002 is **Accepted for bounded local design; READY for separate implementation authorization**. Baseline offline build/58 Solidity/54 Python tests, 25 Cast digests/34 EVM-plus-Python recoveries and two unchanged end-to-end controls support constrained reuse. New source must satisfy compiler/library restrictions, budget controls, gas ceilings and all existing future tests before experimental acceptance; no code or production authorization follows.

[ADR 0004](adr/0004-autonomous-bootstrapping-research-direction.md) preserves AI-first autonomous onboarding/earning and potential organic human discovery through genuine activity, without guaranteed discovery/value/adoption. All five [future scopes](../research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md) are unimplemented. AB-01/AB-02 belong first to Stage 0 requirements/threat/funding research, informing Stage 3 safe discovery; AB-03/AB-04 connect Stage 4 useful-work eligibility with Stage 5 Sybil/security research; AB-05 begins as a genuine-evidence rubric in Stage 0, with any human/public-network study separately authorized under later gates. Require explicit data/actor/time/resource bounds, baseline and falsification criteria before executing. No manufactured activity or artificial trading to make a stage look successful; no alteration/removal of earlier stage risks.
