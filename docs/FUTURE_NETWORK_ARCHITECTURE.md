# Future Network Architecture Research Territory

**Task 016:** [Native L1 foundations](architecture/NATIVE_L1_RESEARCH.md) adds evidence-derived requirements, a candidate decision matrix, unresolved risks and a proposed comparative gate. No final architecture is selected; Experiment 002 is [closed as a bounded conditional result](experiments/EXPERIMENT_002_FINAL_REVIEW.md). Earlier milestone language below retains its historical scope.

This document maps the research space for the founder-defined goal of an independent permissionless Layer 1 (L1) blockchain economy with a native asset for humans and machines. Task 006 and [ADR 0003](adr/0003-independent-l1-research-direction.md) clarify the goal; other architectures remain comparison baselines. It is not a selected design or implementation specification. Candidate approaches below are starting points for comparison; Genesis has not completed a comprehensive literature review or selected an architecture.

For every area, selection requires relevant prior art, explicit trust and threat assumptions, measurable requirements, comparative evidence, and review. Dependencies connect network operation, consensus, execution, economics, and participant tooling; choices cannot be made in isolation.

## Research-goal requirements

Map each candidate to Verifiable Autonomous Work, Independent Network Security, and Human and Machine Economy. Investigate AI mining/earning through independently verified contributions without equating useful work, reward eligibility and consensus. Include AI Sybil swarms, shared operator control, fabricated/duplicated work and colluding verifiers; address scarce-resource assumptions and accessible independent validation.

The same native asset should support human-to-human, human-to-machine and machine-to-machine economic utility. Candidate services include compute, storage, bandwidth and human-directed coordination; real demand, sustainable fee/security budgets and fair access remain hypotheses. Compare issuance-funded rewards with service payments and existing-asset/no-token alternatives. No supply, ticker, issuance schedule, consensus algorithm or adoption/economic outcome is approved.

Future AI, computing, robotics, cryptography and communications developments motivate modular interfaces, cryptographic migration, version compatibility and diverse resource/latency profiles. Avoid claiming guaranteed future-proofing. Experiment 002's public sum checker could inform settlement requirements but provides no mining, useful-work, native-economy or consensus result.

## 1. Network foundations

| Area | Candidate approaches | Main risks and dependencies | Evidence needed before choosing |
| --- | --- | --- | --- |
| Peer-to-peer communication | Gossip, request-response overlays, relay-assisted paths, content-addressed messages, hybrid transports. | Eclipse attacks, spam, metadata leakage, poor mobile or constrained-device performance; depends on identity, routing, and message formats. | Adversarial network simulations, bandwidth/latency measurements, privacy analysis, and comparison across connectivity profiles. |
| Permissionless participation | Open node admission, resource-bounded admission, optional roles, reputation or stake signals. | Open access can invite Sybil and denial-of-service attacks; gates can concentrate power and exclude low-resource participants. | Measure participation cost, attack cost, operator diversity, accessibility, and effect of any admission assumptions. |
| Discovery and routing | DHT-like discovery, gossip discovery, bootstrap peers, signed directories, local discovery, or combinations. | Bootstrap dependence, poisoning, censorship, Sybil capture, stale advertisements, privacy leakage. | Test churn, partition recovery, discovery completeness, attack resistance, and degree of centralization. |
| Synchronization | Full replay, snapshots with verification, state sync, checkpoints, role-specific sync. | Invalid snapshots, long sync times, trusted checkpoints, data withholding, state growth. | Independent snapshot verification, recovery tests, storage and bandwidth profiles, malicious-peer scenarios. |
| Data availability | Replication, erasure coding, sampling, archival providers, availability attestations. | Withholding, false availability, sampling assumptions, storage concentration, verification complexity. | Quantify recoverability and verification under adversarial withholding and realistic node resources. |
| Storage and archival | Full history, pruning, snapshots, external archives, content-addressed records. | Permanent storage cost, loss of historical data, archive cartel, unverifiable pruning. | Long-term storage models, retrieval tests, independent reconstruction, data-retention and privacy analysis. |
| Transaction propagation | Gossip, batching, priority queues, private relay paths, fee-aware propagation. | Censorship, frontrunning, spam, propagation imbalance, central relay dependence. | Measure propagation delay and fairness under congestion, adversarial relays, and diverse network topologies. |
| Partitions and censorship | Store-and-forward, delayed inclusion, multiple paths, local operation, eventual reconciliation. | Conflicting actions, long-lived forks, delayed settlement, partition-specific censorship. | Define safety and liveness under explicit delay bounds; test partition, recovery, and censorship scenarios. |

**Dependencies:** discovery and routing affect consensus participation; data availability affects execution and finality; transaction propagation affects censorship and fork choice. Any baseline should include small, intermittently connected nodes as well as well-provisioned infrastructure.

## 2. Consensus and security

**Established reference mechanisms:** Proof of Work (PoW) and Proof of Stake (PoS) are existing consensus families. They have different assumptions around resource expenditure, validator selection, concentration, and attack economics. This document does not claim a complete comparison or endorse either family.

| Area | Candidate approaches | Main risks and dependencies | Evidence needed before choosing |
| --- | --- | --- | --- |
| Sybil resistance | Resource costs, stake or bonded participation, identity/certification assumptions, hybrid defenses, application-specific limits. | Any scarce-resource assumption can exclude participants or concentrate control; identity gates undermine permissionlessness; resource costs may be externalized. | Model attacker budget and access, compare inclusion and concentration, test adaptive Sybil strategies. |
| Validator or proposer selection | Resource-weighted, stake-weighted, work-weighted, rotating, committee-based, hybrid, or open competition. | Capture, predictable targets, correlated failures, hidden centralization, high hardware requirements. | Quantify selection fairness, attack probability, infrastructure concentration, and participation cost. |
| Safety, liveness, finality | Probabilistic or deterministic finality families; synchronous, partially synchronous, or asynchronous assumptions. | Safety/liveness trade-offs; finality delay; dependence on clocks, synchrony, and network assumptions. | State formal properties and network assumptions; model adversarial delays and faults; independently review proofs. |
| Fork choice and recovery | Cumulative work, stake-weighted rules, checkpoints, social coordination, or hybrid recovery. | Deep reorgs, checkpoint authority, long-range attacks, conflicting social norms. | Analyze adversarial histories, partitions, recovery, and who can influence checkpoints or emergency choices. |
| Economic security | Fees, rewards, bonds, penalties, external costs, reputation, or combinations. | Bribery, rent extraction, value volatility, strategic withholding, concentration, incentive misalignment. | Agent-based and economic analysis with adversarial strategies; sensitivity to adoption, price, and costs. |
| Verification costs | Full validation, light-client proofs, sampling, delegated verification, hardware acceleration. | Trust leakage, proof system assumptions, high compute, denial of service, implementation diversity. | Benchmark independent verification across device classes and test malformed or adversarial inputs. |
| Adversarial participation | Equivocation, bribery, collusion, censorship, selfish participation, cartel formation. | Models may omit adaptive attackers, private coordination, off-protocol incentives, or correlated operators. | Red-team scenarios, game-theoretic analysis, network simulation, and independent review. |
| Partitions and recovery | Pause, continue locally, fork, delayed settlement, checkpointed recovery, or protocol-specific reconciliation. | No single policy handles all delay regimes; conflicting histories and social coordination can persist. | Define guarantees under partitions and recovery; test long delays, reconnects, and adversarial split-brain. |
| Decentralization trade-offs | Optimize for low cost, throughput, independent operators, or constrained devices; compare explicitly. | Throughput and convenience may centralize hardware or services; decentralization measures are multidimensional. | Publish measurable concentration, entry costs, client diversity, geography, and operator independence. |

**Novel consensus research:** explore only after requirements and existing mechanisms are mapped. Novelty requires documented prior-art review and a precise protocol proposal. Claims require formal analysis, adversarial testing, and independent scrutiny.

**Autonomous Proof of Contribution (APoC):** internal research hypothesis about whether verifiable useful contributions can contribute to security or incentives. It is neither an invented nor finalized consensus mechanism. A contribution may belong in a service market or reward layer instead.

## 3. Verifiable contribution research

Candidate resources include computation, storage, bandwidth, sensing, verification, maintenance, and other useful services. Candidate measurement approaches include challenge-response, replicated work, proofs or attestations, sampled audits, redundant independent verification, and outcome-based evidence. These are reference categories, not chosen mechanisms.

Key risks include fake work, colluding verifiers, Sybil identities, unverifiable real-world outcomes, measurement gaming, low-quality contributions, reward manipulation, and hardware or energy barriers. Sensing introduces trust in physical devices and environments; computation can be padded or hidden; storage and bandwidth can be temporarily simulated; verification itself can be attacked.

Before deciding whether contributions belong in consensus, incentives, or service markets, research must define the resource and service boundary, identify an objective measurement, assess independent verification cost, model attacks and collusion, compare market and protocol-level incentives, and measure whether integration increases security or only complexity. Experiments should include adversarial providers and verify that rewards cannot be claimed through fake or duplicated contributions.

## 4. Economic layer

| Area | Candidate approaches | Main risks and dependencies | Evidence needed before choosing |
| --- | --- | --- | --- |
| Native asset justification | No native asset; existing assets; fee token; security asset; settlement medium; multiple specialized assets. | A token creates speculation, legal, governance, custody, volatility, and capture risks; it may not solve a real requirement. | Test the target native asset's role against alternatives; analyze human/machine utility, recurring demand, user impact, attack surfaces, and legal/operational questions. |
| Distribution and issuance | No issuance; fair-launch options; mining- or contribution-linked issuance; fixed or adaptive schedules. | Premine perceptions, bot capture, concentration, sybil farming, incentive distortion, unfair access. | Simulate distribution under realistic adoption and adversarial behavior; publish assumptions and concentration outcomes. |
| Fees and validator incentives | Fee markets, fixed or dynamic fees, rewards, external subsidy, or combinations. | Congestion pricing, censorship, volatile security budget, rent-seeking, exclusion of small transactions. | Model demand, costs, attacks, and participation under low/high usage; measure affordability and sustainability. |
| Programmable settlement | Native execution, constrained agreement engine, or settlement through other networks. | Complex execution bugs, state bloat, cross-network bridges, dependence on privileged components. | Demonstrate necessity, deterministic behavior, bounded resources, and security under adversarial contracts or messages. |
| Resource marketplaces | Protocol-level markets, application-level matching, bilateral agreements, or external marketplaces. | Collusion, quality uncertainty, centralized discovery, dispute costs, privacy leakage. | Compare independently verifiable service outcomes, market concentration, and dispute resolution costs. |
| Treasury and governance | No treasury, transparent grants, protocol-controlled funds, community-governed allocation. | Capture, discretionary control, opaque spending, governance attacks, conflicts of interest. | Analyze authority, accountability, minority protections, and alternatives before any treasury proposal. |

**Current decision boundary:** no ticker, tokenomics parameters, presale, sale, launch date, issuance schedule, allocation, or treasury design is approved. No token issuance is planned at this stage.

## 5. Execution and state

| Area | Candidate approaches | Main risks and dependencies | Evidence needed before choosing |
| --- | --- | --- | --- |
| State model | Account-based, UTXO-style, object/capability model, or hybrid. | Concurrency, privacy, state growth, composability, wallet complexity, and verification costs differ. | Map use cases to state transitions; benchmark and analyze security, concurrency, and recovery. |
| Transaction formats | Canonical binary formats, typed messages, versioned envelopes, capability-based requests. | Ambiguous encoding, replay, upgrade incompatibility, signature confusion. | Specify canonicalization, domain separation, versioning, fuzzing, and cross-implementation agreement. |
| Deterministic execution | Restricted virtual machine, deterministic interpreter, transaction state machine, or off-chain execution with proofs. | Nondeterminism, resource exhaustion, implementation divergence, proof overhead. | Define determinism and resource metering; test cross-platform consistency and adversarial programs. |
| Agreements and contracts | Escrow scripts, smart contracts, state channels, signed agreements, adjudication modules, or non-programmable settlement. | Bugs, upgrade authority, oracle dependence, irreversibility, complexity. | Demonstrate that automation is needed; analyze failure recovery, verification, and dispute assumptions. |
| Resource accounting | Gas-like metering, quotas, fees, capability budgets, per-resource limits. | Metering games, denial of service, mispriced work, constrained-device exclusion. | Measure worst-case execution and storage; test attempts to exhaust resources or bypass quotas. |
| Verification and isolation | Replicated execution, proofs, sandboxes, independent clients, hardware isolation. | Trust in proof systems or hardware, implementation bugs, verifier monoculture. | Require diverse implementations, adversarial inputs, isolation analysis, and independent review. |

## 6. Autonomous economic participants

Research capabilities include cryptographic identities and machine/agent wallets; operator-controlled spending limits; scoped delegation by purpose, amount, time, counterparty, or resource; revocation, key rotation, and recovery; service discovery and capability advertisement; negotiation; machine-readable agreements; escrow and settlement; independent verification; and multi-agent coordination.

Candidate approaches include software keys, hardware-backed keys, threshold control, capability tokens, signed offers, reputation signals, local directories, peer-to-peer discovery, and conditional settlement. These are not selected design choices. Risks include key theft, confused-deputy behavior, overbroad delegation, unreliable capability claims, identity correlation, coercive operators, offline revocation delay, fabricated service evidence, and unsafe agent decisions.

Dependencies include the authority model, message format, state/settlement mechanism, discovery, contribution verification, and dispute process. Evidence must show bounded consequences under compromised or misbehaving agents; interoperable signing and verification across implementations; clear failure behavior; and consent and recovery suitable for operators and affected humans.

## 7. Future-oriented infrastructure

Research may examine offline operation, intermittent connectivity, delayed settlement, satellite and interplanetary communication constraints, model-agnostic participation, hardware-independent interfaces, cryptographic agility, post-quantum migration, long-lived compatibility, interoperability with existing networks, and modular upgrades. Candidate approaches include asynchronous protocols, store-and-forward messages, version negotiation, algorithm agility, translation gateways, and layered settlement.

Risks include stale authority, conflicting local histories, long-term key compromise, migration coordination failure, gateway centralization, incompatible versions, and assumptions that do not survive decades. “Future-proof” and “universal compatibility” are not achievable guarantees; define narrow properties and test them. Evidence should include delay and partition simulations, migration and downgrade analysis, independent implementation tests, and explicit cryptographic lifecycle assumptions.

## 8. Ecosystem

Potential ecosystem roles include full nodes, validators, light clients, wallets, SDKs, APIs, explorers, developer tooling, documentation, open standards, test networks, independent infrastructure providers, and community governance. Candidate approaches range from one reference implementation to multiple independent clients and standards-first interfaces.

Risks include client monoculture, service-provider concentration, privileged hosted APIs, brittle tooling, inaccessible participation, and governance capture. Before selecting an ecosystem architecture, identify actual users and workflows; test independent implementations; publish interface and conformance requirements; and measure participation and operator diversity. A test network or public ecosystem is conditional on earlier research and security gates.

## Cross-cutting decision criteria

Any future architecture proposal must include: (1) requirement and use case; (2) existing approaches and prior art; (3) candidate alternatives; (4) assumptions and trust dependencies; (5) adversaries and failure modes; (6) safety, liveness, privacy, and availability properties; (7) cost and hardware profiles; (8) reproducible comparative evidence; (9) upgrade and governance implications; and (10) limitations and reasons alternatives were rejected or deferred.

## Autonomous bootstrapping requirements — Task 008

The target is AI-first and permissionless while shared by humans and machines. [ADR 0004](adr/0004-autonomous-bootstrapping-research-direction.md) adds eventual safe agent discovery, opportunity assessment, scoped onboarding and earning/spending to the research direction, not implemented capabilities. Compare independent network identity verification, permissionless/read-only discovery, initial gas resources, bounded delegation, genuine task/funding evidence and observable settlement while respecting privacy. Agents must be able to abstain when identity, value, opportunity or authority cannot be established.

Genuine activity may aid organic human discovery without marketing as the primary mechanism, but volume, many addresses and newly issued rewards do not prove independent demand or adoption. No manufactured wallet activity/trading/signals; synthetic fixtures remain explicit laboratory evidence. Use the [bounded scopes](../research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md) as research inputs rather than selected network components. Neither accepted local EVM design nor compatibility checks establish future L1 consensus, native value or guaranteed adaptability.
