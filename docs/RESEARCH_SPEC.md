# Research Specification

## Purpose and boundaries

Translate the Genesis mission into research questions, assumptions, falsifiable hypotheses, and reproducible evaluations. The program spans autonomous economic authority, verifiable coordination, and autonomous network security. This is not a completed literature review or a protocol specification. Compare existing technologies and academic or engineering work before claiming a gap or novelty.

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
