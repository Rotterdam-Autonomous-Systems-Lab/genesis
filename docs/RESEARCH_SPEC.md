# Research Specification

## Purpose and boundaries

Translate the Genesis mission into research questions, assumptions, falsifiable hypotheses, and reproducible evaluations. The founder-defined target is an independent permissionless L1 economy with a native asset, verifiable AI contribution/mining or reward participation, and genuine human and machine utility. The connected planning pillars are Verifiable Autonomous Work, Independent Network Security, and Human and Machine Economy. Autonomous Economic Authority, Verifiable Coordination and Autonomous Network Security remain cross-cutting technical tracks. This is not a completed literature review or a protocol specification. Compare existing technologies and academic or engineering work before claiming a gap or novelty.

## Three connected research pillars

| Pillar | Questions and candidate methods | Evidence limits / falsification |
| --- | --- | --- |
| Verifiable Autonomous Work | Define useful compute/storage/bandwidth/verification tasks; compare verification versus production costs, objective correctness, uniqueness and demand. Investigate AI earning native tokens via service payment, mining or contribution rewards without selecting a mechanism. | Fake/duplicate/padded work and colluding verifiers can invalidate reward claims. Correct arithmetic alone is not useful/scarce work; distinguish service fees from protocol issuance and consensus. |
| Independent Network Security | Compare scarce-resource/consensus assumptions under adversarial operators creating many AI agents; model safety, liveness, censorship, concentration and independent validation costs. | Agent identity counts are not operator independence or scarce resources. A single-node prototype cannot establish secure permissionless consensus or Sybil resistance. |
| Human and Machine Economy | Investigate recurring human-to-human, human-to-machine and machine-to-machine demand for the same network/asset; evaluate affordability, operator consent, fee/security budgets, issuance incentives and distribution under adverse demand/cost scenarios. | Subsidized volume, wash exchange or token appreciation does not establish utility or sustainability. Preserve no-demand, concentration and unsustainable-budget outcomes; no economic parameters selected. |

Use existing networks/assets/non-token systems as comparative controls capable of challenging the target architecture, not silently replacing the goal. Adaptability research covers future AI, computing/robotics hardware, cryptographic migrations and communication delays; measure compatibility and authority trade-offs rather than guarantee future-proofing.

## Experiment-to-pillar boundary

[Experiment 001](../research/reports/EXPERIMENT_001_REPORT.md) contributes narrow authority/result-verification/settlement evidence with CONDITIONAL PASS. [Experiment 002 review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md) proposes a veto-isolation test with explicit upfront consent and conditional inclusion, not a result. Both principally inform Verifiable Autonomous Work's agreement layer; they expose settlement safety/timing requirements relevant to Independent Network Security and bounded consent relevant to Human and Machine Economy. Neither supplies mining, useful-work uniqueness, consensus/Sybil resistance, native-token demand or sustainability evidence. Physical truth and subjective AI output remain distinct verification problems.

## Track 1: Autonomous Economic Authority

Research cryptographic identities and claims; machine and agent wallets; operator-controlled spending limits; scoped delegation; revocation, rotation, and recovery; bounded autonomous spending; capability advertisement; service discovery; negotiation; verifiable agreements; escrow and settlement; and privacy.

Questions include: What authority should an agent or machine hold? How can an operator limit harm while permitting useful autonomy? What can be verified cryptographically, and what depends on software, hardware, sensors, or external facts? How can limits and revocations work when a participant is offline? What recovery methods avoid centralized control while preventing permanent loss or takeover?

Candidate methods: threat-driven capability models; formal state machines; interoperability tests across independent signers/verifiers; simulations of compromise and delayed revocation; usability and failure analysis with synthetic scenarios.

Adversarial cases: stolen keys, malicious or defective agents, confused-deputy actions, replay, overbroad delegation, colluding counterparties, dishonest capability advertisements, operator coercion, and delayed revocation.

## Track 2: Verifiable Coordination

Research permissionless discovery, multi-agent coordination, negotiation, machine-readable service agreements, independently verified contributions, dispute evidence, offline and delayed communication, resource exchange, and interoperability.

Questions include: How can participants discover one another without a gatekeeping directory? Which claims about service fulfillment can an independent verifier establish? What evidence is needed when outcomes are subjective or physical? How do parties coordinate across partitions, delayed messages, and different goals? When is escrow or adjudication useful, and what new trust does it introduce?

Candidate methods: protocol modeling; event-driven simulation of delay, reordering, loss, churn, and partitions; agreement conformance tests; independent verification cost measurements; comparative analysis of on-chain, off-chain, and bilateral mechanisms.

Adversarial cases: fake service, selective evidence disclosure, collusion between requester/provider/verifier, Sybil discovery poisoning, censorship, replay, equivocation, non-delivery, and strategic dispute escalation.

## Track 3: Autonomous Network Security

Research Sybil resistance, collusion, adversarial participation, peer-to-peer discovery and routing, consensus baselines, economic security, verification cost, denial of service, key compromise, network partitions, censorship, and protocol evolution.

Questions include: What assumptions make participation permissionless in practice? Which safety and liveness properties survive adversarial delay? Can useful contributions be objectively verified? Are contribution mechanisms safer as a market or incentive layer than as consensus? How can upgrades remain open without concentrating authority?

Candidate methods: threat modeling; formal properties; comparative network and economic simulations; attack-cost and concentration analysis; red-team review; fault injection; client-diversity and resource benchmarking.

Adversarial cases: Sybil swarms, colluding validators or verifiers, bribery, private coordination, selfish participation, censorship, eclipse attacks, denial of service, fake work, reward manipulation, long-range histories, partition recovery, and malicious upgrades.

## Hypothesis and experiment template

Every experiment should record:

1. Research question and motivation.
2. Prior art and baseline systems reviewed (with references and review scope).
3. Hypothesis and plausible competing hypotheses.
4. System boundary, actors, resources, and trust assumptions.
5. Adversarial scenarios and failure cases.
6. Method, metrics, parameters, synthetic data, and reproducibility steps.
7. Falsification criteria chosen before interpreting results.
8. Results, uncertainty, negative or inconclusive outcomes, and limitations.
9. Follow-up decisions and links to ADRs where relevant.

A simulation result supports only the modeled conditions. A cryptographic proof does not by itself establish correct implementation, safe governance, real-world input validity, or operational security.

## Evidence and literature discipline

Use `ESTABLISHED TECHNIQUE`, `PROJECT ASSUMPTION`, `RESEARCH HYPOTHESIS`, and `FINDING` labels where helpful. Cite primary sources and technical documentation for factual comparisons. State what was searched and what was out of scope. Do not claim comprehensiveness or originality without a documented, reviewable search. Current repository content does not establish that such a comprehensive review has been completed.

## Task 007 economic research foundations

The separate [AI-earned native-token and human/machine utility review](../research/economics/AI_EARNED_NATIVE_TOKENS_AND_UTILITY.md) proposes E-01–E-05 without issuing a token or selecting consensus. Prioritize correctness/usefulness/uniqueness separation and fixed-resource identity-splitting tests, then subsidy/security-budget and native-versus-stable-settlement sensitivity. These are research plans, not results. The [Experiment 002 final proposal](experiments/EXPERIMENT_002_FINAL_SPEC.md) remains BLOCKED by dependency and finite-fee-policy decisions; synthetic service settlement does not validate issuance eligibility or economic demand.

## Task 008 autonomous bootstrapping research

The [five bounded research scopes](../research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md) cover AB-01 safe read-only discovery/onboarding, AB-02 external funding versus issuance, AB-03 useful/duplicate work, AB-04 fixed-resource identity splitting and AB-05 genuine activity/human discovery. They are unimplemented and carry explicit budgets/metrics/failure cases. Prioritize identity/authority and funding provenance before reward experiments; synthetic transactions cannot establish adoption. [ADR 0004](adr/0004-autonomous-bootstrapping-research-direction.md) records the aspiration without value/adoption claims. [Experiment 002 blockers](experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md) are resolved only for its accepted local design; implementation and independent-network/economic evidence remain separate.
