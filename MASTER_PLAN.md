# Genesis Master Plan

**Canonical project charter — Rotterdam Autonomous Systems Lab (RASL)**

This document preserves the project's mission, scope, research program, decision boundaries, and staged path. It is the canonical specification for project intent. Approved decisions are recorded in `docs/DECISION_REGISTER.md`; major technical choices require an Architecture Decision Record (ADR). Historical brainstorming is preserved separately and must not be mistaken for selected architecture.

## Status and evidence labels

**Current status: early-stage experimental research.** Genesis has no selected independent network design, production protocol, token, finalized consensus algorithm, or validated new consensus mechanism. Experiment 001 is published with CONDITIONAL PASS for a small, bounded two-agent fixture; Experiment 002 has a partial isolated escrow implementation from separately authorized Task 009, but acceptance is FAIL / implementation BLOCKED by a pinned-Anvil fee-receipt contradiction; no complete agent workflow is published. See [the blocking review](docs/experiments/EXPERIMENT_002_IMPLEMENTATION_REVIEW.md). Both are subject to scoped research gates. This is a first step in investigating a much larger decentralized economic network; Genesis must not be reduced to an agent-payment application.

Use these labels consistently:

- **CONFIRMED DECISION** — explicitly adopted and recorded; binding until changed through review.
- **LONG-TERM ASPIRATION** — desired direction, not a promise or proof of feasibility.
- **RESEARCH HYPOTHESIS** — falsifiable proposition without established support.
- **OPEN QUESTION** — unresolved decision or knowledge gap.
- **REJECTED OR DEFERRED APPROACH** — not being pursued now; this does not imply the idea is universally impossible.
- **ESTABLISHED TECHNIQUE** — documented prior art or broadly used method. Cite sources and do not imply Genesis originated it.
- **FINDING** — a result supported by a documented method, evidence, and limitations.

## Founding vision and motivation

Genesis is the temporary internal codename for a research initiative originating in Rotterdam, Netherlands, under RASL. The ambition is to explore infrastructure that could become foundational to economic coordination among autonomous intelligences and systems.

Potential participants include humans and human-operated systems; AI agents and autonomous software; robots and industrial machines; vehicles, drones, and autonomous transport; satellites and space infrastructure; sensors and connected devices; distributed computational systems; and entities or technologies not yet invented. Participants may have different owners, hardware, capabilities, jurisdictions, objectives, and connectivity conditions.

**Central research question:** “Can autonomous intelligences that have never met, run on different hardware, operate under different owners, and have different objectives establish verifiable agreements, exchange resources, and coordinate safely without trusting each other or a central platform?”

**Core principle:** “The network must not need to trust the intelligence of its participants. It must only need to verify their actions.” This is a guiding principle and research challenge, not a claim that all actions can already be verified or that cryptography removes every trust dependency.

The ambition is to investigate something as foundational to future machine economies as Bitcoin became to permissionless digital value transfer. This is an aspiration only; it asserts neither comparable achievement nor technical novelty.

## Mission and guiding principles

Research whether open, verifiable infrastructure can let autonomous participants establish bounded authority, discover one another, make and fulfill agreements, exchange resources, and coordinate without routine permission from a centralized platform.

1. Research before implementation; evidence before claims.
2. Verify actions and bound authority rather than relying on the intelligence or good intentions of participants.
3. Minimize the authority and blast radius of any key, operator, service, or protocol component.
4. State trust assumptions and limits; do not describe a system as trustless when it relocates trust.
5. Support diverse operators, hardware, models, jurisdictions, and connectivity conditions where feasible.
6. Treat privacy, accessibility, resilience, abuse resistance, and interoperability as research requirements.
7. Preserve negative results, rejected ideas, and uncertainty.
8. Preserve the independent-L1/native-economy research goal without presuming a validated chain design, asset necessity, consensus mechanism, governance system, token parameters or launch.

## Long-term network ambition

**CONFIRMED RESEARCH DIRECTION / LONG-TERM ASPIRATION:** Task 006 explicitly clarifies the architectural research goal as an **independent, permissionless, AI-first Layer 1 blockchain economy with a native asset**, serving humans and autonomous systems. Investigate whether AI systems can mine or earn native tokens through independently verifiable contributions, subject to useful-work measurement, consensus, Sybil resistance and economic-security research. This is a goal to investigate, not approval of a chain implementation, token launch or evidence that such a system is viable. See [ADR 0003](docs/adr/0003-independent-l1-research-direction.md).

The same network and native asset should offer meaningful human utility through human-to-human, human-to-machine and machine-to-machine economic activity. Candidate utility includes exchange for compute, storage or bandwidth, payment for services and human-directed resource coordination. These are hypotheses about demand, not adoption forecasts or promises of value. Participants should be able to establish cryptographic authority, discover services, sign bounded agreements and verify actions across owners, models and hardware. A claimed AI identity or unverified output must not be treated as a scarce security resource, contribution proof or voting weight.

Existing chains, layered designs, existing assets and non-chain systems remain necessary comparison baselines. Negative evidence may require revising or stopping the independent-L1/native-asset research program through explicit review; alternatives must not silently replace the stated goal. Research direction is now explicit; final protocol architecture, economic rules and production decisions remain unselected.

Potential functions include permissionless discovery and routing; cryptographic authority and scoped delegation; service and contribution verification; resource markets; programmable settlement; resilient peer-to-peer communication; and long-lived protocol evolution. Offline and delayed communication, satellite links, and eventually interplanetary constraints are research environments, not current capabilities.

No one AI provider, intelligence model, manufacturer, operating system, or centralized permission authority should be a necessary gatekeeper to the long-term network. Whether that objective is achievable for each function, and what trade-offs it entails, remains open.

## Autonomous network bootstrapping

**CONFIRMED RESEARCH DIRECTION / LONG-TERM ASPIRATION:** Task 008 clarifies that autonomous AI agents should eventually discover Genesis, assess economic opportunities, enter within operator-granted bounded cryptographic authority, contribute independently verifiable work and earn/spend native tokens. AI-first prioritizes safe autonomous interfaces and participation; it does not make intelligence a consensus proof or exclude humans and other machines. See [ADR 0004](docs/adr/0004-autonomous-bootstrapping-research-direction.md).

Genuine, observable on-chain economic activity could provide a path for humans to discover and adopt the same open infrastructure organically, without traditional marketing as the primary adoption mechanism. This is not evidence of present discovery capability, native-token monetary value, independent customer demand or guaranteed adoption. Initial fee resources, external customer funding versus issuance, verifier costs, Sybil resistance, privacy and useful-work attribution remain research questions. No system can assume demand or spending authority merely because a network is discoverable.

Never manufacture wallet activity, artificial trades, circular demand or misleading economic signals. Clearly label synthetic fixtures; address counts and transaction volume do not prove independent users or beneficial activity. The five [bootstrapping research scopes](research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md) are unimplemented plans; preserve negative evidence and safe abstention. Adaptability remains a research aim, not complete future-proofing.

## Participants and example use cases

Research should account for human-directed software, autonomous software agents, robots and machines, transport systems, sensors, satellites, distributed compute and storage providers, service requesters, infrastructure operators, developers, and future entities. Example questions include: an agent purchasing bounded compute; a robot contracting for maintenance; a sensor selling authenticated observations; two machines coordinating a transfer while intermittently connected; or independent operators contributing verifiable storage or bandwidth.

These examples describe research scenarios. They do not authorize autonomous spending, imply a selected use case, or establish that the proposed verification is feasible.

## Research philosophy and technical principles

- Separate the authority to decide from the authority to act. A capable or autonomous decision-maker should only exercise cryptographic capabilities granted within explicit limits.
- Prefer independently verifiable evidence with clear provenance, scope, and cost.
- Design evaluation around adversaries, collusion, incentives, failure, and realistic resource constraints.
- Treat permissionless participation as an objective that must be measured against concentration, accessibility, cost, and performance.
- Consider offline delivery, delay, reordering, partitions, and recovery explicitly.
- Favor modularity and open interfaces where they improve verifiability and evolution; avoid claiming universal compatibility or perfect future-proofing.
- Compare against existing systems and techniques before asserting a gap or novelty.

## Research program

### Connected research pillars

Task 006 organizes the research program and roadmap around three connected pillars:

1. **Verifiable Autonomous Work:** how can autonomous participants contribute objectively verifiable work and earn value? Separate proof of a valid result, useful demand, unique contribution and payment; investigate fake/duplicate work, verifier costs and collusion.
2. **Independent Network Security:** how can an independent permissionless network secure consensus and resist Sybil attacks, including large AI-agent swarms under common control? Study scarce-resource assumptions, safety/liveness/finality, censorship, concentration and independent validation. Many agent addresses do not imply many independent operators.
3. **Human and Machine Economy:** why would humans and machines repeatedly use the same network and native token? Investigate actual service demand, bounded authority, affordability, fees, incentives, issuance, security budgets, distribution and sustainability under low demand and adverse conditions. Token price or subsidized transaction volume alone cannot demonstrate utility.

Work verification, reward eligibility and consensus validity are separate questions until evidence justifies connecting them. An economic reward is not necessarily newly issued currency; fees, market payments and protocol issuance have different accounting/security implications. No parameters are approved.

The original three foundational **technical tracks** remain cross-cutting methods, not competing roadmap pillars:

### 1. Autonomous Economic Authority

Cryptographic identity and claims; agent and machine wallets; operator-controlled limits; scoped delegation; revocation, rotation, and recovery; bounded autonomous spending; service discovery and capability advertisement; negotiation; verifiable service agreements; escrow and settlement; independent verification; and privacy-preserving authority.

### 2. Verifiable Coordination

Permissionless discovery; multi-party coordination; agreement formats; independently verified contributions; dispute evidence; offline and delayed communication; resource exchange; interoperation; and coordination among parties with different goals and operators.

### 3. Autonomous Network Security

Sybil resistance; collusion; adversarial participation; network discovery and censorship; consensus and fork choice research; economic security; verification costs; key compromise; denial of service; protocol evolution; and recovery after partitions.

Prior-art comparisons are ongoing. Existing systems such as Bitcoin and other Proof of Work systems, Proof of Stake systems, capability-based security, cryptographic identity systems, distributed storage, peer-to-peer protocols, and smart-contract platforms are reference points only. No comprehensive literature review has yet been completed by this repository.

## Economic architecture ambitions

**LONG-TERM ASPIRATION:** Research a native asset used by humans and machines in the independent blockchain economy. **RESEARCH HYPOTHESIS:** fees, security bonds, settlement, validator incentives and permissionless resource exchange may justify its role. AI systems may mine or earn it for independently verified contributions, without assuming that AI computation or useful work is itself a sound consensus mechanism. Human-to-human utility is part of the goal, alongside human-to-machine and machine-to-machine exchange.

Research must test necessity and sustainable demand against existing-asset/non-token alternatives and examine issuance, distribution, concentration, capture, sustainability, legal/operational constraints and user harm. It may find the asset unjustified or unsafe; such findings must be preserved and trigger explicit direction review rather than invented economic claims.

Mining, contribution-linked issuance, fees, validator rewards, treasury mechanisms, and resource marketplaces are candidate research areas. No tokenomics parameters, ticker, presale, launch date, allocation, or issuance schedule is approved. There is no token.

## Candidate consensus research program

Proof of Work and Proof of Stake are **ESTABLISHED TECHNIQUE** reference families with distinct security assumptions, resource costs, and concentration risks. Genesis may examine them and other designs as comparison baselines. Novel consensus approaches are research questions only.

Autonomous Proof of Contribution (APoC) is an **internal RESEARCH HYPOTHESIS**: investigate whether useful contributions such as computation, storage, bandwidth, sensing, or verification can be measured and rewarded in ways that improve security or coordination. It is not an invented, specified, or finalized consensus mechanism. A contribution may be better handled as a service market or incentive layer than as consensus input. Work must address objective measurement, independent verification, fake-work, collusion, reward manipulation, Sybil resistance, and security consequences.

## Network architecture research

The project will investigate peer-to-peer communication, discovery and routing, synchronization, data availability, transaction propagation, storage and archival strategies, execution models, verification, light clients, partition resilience, and interoperability. The target research architecture is an independent permissionless L1; modular designs, application-specific networks and integrations are comparison options or possible components subject to justification. No concrete architecture is selected, and Ethereum is not a permanent commitment.

## Developer ecosystem

A mature ecosystem could include full nodes, validators, light clients, wallets, SDKs, APIs, explorers, test networks, developer tooling, documentation, open standards, independent infrastructure providers, and community governance. These are long-term possibilities, not current deliverables. Standards and tools should grow from demonstrated requirements and preserve independent implementation and verification where practical.

## Governance and evolution

No governance model is finalized. Research should examine proposal rights, upgrade authority, client diversity, emergency powers, key rotation, standards processes, forks, and capture risks. Protocol evolution should be transparent, reviewable, and compatible with independent verification where possible. Any upgrade mechanism creates authority and attack surface; no mechanism guarantees conflict-free or universally accepted change. Long-term adaptability must address future AI, computing hardware, robotics, cryptography and communications through versioned interfaces, migration research, resource profiles and adversarial compatibility tests. These are research methods, not a guarantee of complete future-proofing.

## Security and threat assumptions

Assume participants may be malicious, compromised, self-interested, offline, colluding, or operating under conflicting goals. Examine Sybil identities, censorship, equivocation, replay, fake work, denial of service, resource exhaustion, key loss, dishonest service claims, network partitions, delayed messages, malicious upgrades, and concentrated control. State assumptions about cryptography, hardware, time, identity claims, external data, dispute resolution, connectivity, and participant resources in each proposal.

All experiments use synthetic identities and data. No real funds, production credentials, production deployment, unauthorized infrastructure, external compute, or external services. See `docs/THREAT_MODEL.md` and `SECURITY.md`. The [Experiment 002 review](docs/experiments/EXPERIMENT_002_DESIGN_REVIEW.md) distinguishes direct-predicate settlement, conditional payment progress and strong fairness; none supplies consensus or native-economy security evidence.

## Conditional milestone roadmap

The detailed gates and exit criteria are in `docs/ROADMAP.md`. Stages are conditional research gates, not release promises:

0. Project foundation and prior-art research.
1. First independently verifiable autonomous economic transaction.
2. Adversarial validation and security testing.
3. Permissionless discovery and multi-agent coordination.
4. Verifiable useful-contribution experiments.
5. Novel consensus feasibility research.
6. Independent network architecture research and specification.
7. Experimental implementation and local multi-node network.
8. Public testnet and independent security review.
9. Potential production network, only if justified.
10. Long-term decentralization, governance, and protocol evolution.

Progress to an implementation or public network requires explicit evidence and review gates. A stage may be delayed, changed, or abandoned based on results.

## Research validation gates

Before moving from a question to an experiment, define its boundary, prior art, assumptions, threat cases, competing hypotheses, measures, baseline, and falsification criteria. Before a prototype, document why simulation or a toy implementation is needed, isolate it, and prevent production use. Before a public test network, require a reviewed specification, reproducible test results, security analysis, operational controls, and independent review. Production requires separate justification, governance and legal review, sustained security evidence, operational maturity, and explicit approval; it is not an assumed destination.

## Open questions

- What entities, claims, and behaviors must the system represent, and which should remain outside its scope?
- What action evidence is independently verifiable, and what remains dependent on sensors, hardware, operators, or external data?
- How can autonomous authority be constrained, audited, revoked, and recovered across owners and disconnected systems?
- Which discovery and negotiation methods resist gatekeeping, spam, censorship, and collusion?
- Which contributions can be objectively measured, and do they belong in consensus, incentives, or service markets?
- What Sybil-resistance assumptions are acceptable for different participants and resource classes?
- Is a native asset necessary? What alternatives exist, and what concentration or capture risks follow?
- Would an independent chain solve a demonstrated need better than integrating existing systems?
- What safety, liveness, finality, and availability goals are appropriate under partitions and long delays?
- How can protocol evolution remain open without creating unaccountable upgrade power?
- Which interoperability and post-quantum migration requirements can be tested over long time horizons?
- What governance model can accommodate independent operators without implying that governance disappears?

## Non-goals and rejected or deferred approaches

- Treating Genesis solely as an AI-agent payment application.
- Claiming a new consensus protocol, novel cryptographic primitive, or verified security property without evidence.
- Implementing a chain, consensus algorithm, contracts, token, or agent framework as part of documentation tasks.
- Premature token issuance, tokenomics, presale, ticker selection, or launch scheduling.
- Permanent commitment to Ethereum or any other existing platform as the final architecture.
- Uncontrolled autonomous replication, self-propagation, or unauthorized use of infrastructure.
- Assuming all useful work is measurable, all trust can be eliminated, or all participants can be served by one design.
- Treating aspirations such as space operation or universal future-proofing as present capability.

## Change control

Read `docs/PROJECT_CONTEXT.md`, this charter, and `docs/DECISION_REGISTER.md` before work. Changes to mission, architecture direction, economics, or security boundaries require explicit review and an ADR. Update this charter, decision register, context guide, and relevant research records when a decision changes. Preserve superseded reasoning and negative results in project history.
