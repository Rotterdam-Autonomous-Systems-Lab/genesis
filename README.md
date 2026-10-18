# Genesis

Genesis is the temporary codename for Rotterdam Autonomous Systems Lab (RASL)'s open research into **autonomous economic coordination and decentralized systems**. It researches an independent, permissionless, AI-first Layer 1 blockchain economy where independently controlled participants could establish cryptographic authority, make verifiable agreements, exchange resources, and transact without a centralized permission authority.

The long-term ambition encompasses humans and human-operated systems, AI agents and autonomous software, robots and industrial machines, vehicles and drones, satellites and space infrastructure, sensors, distributed computational systems, and future autonomous entities. Participants may have different owners, hardware, capabilities, jurisdictions, objectives, and connectivity. The network should not depend on one AI provider, model, manufacturer, or operating system.

The central question is whether participants that have never met can coordinate safely without trusting each other or a central platform. The guiding principle is: **the network must not need to trust the intelligence of its participants; it must only need to verify their actions.** This is a research challenge, not a proven guarantee.

The autonomous bootstrapping aspiration is that agents eventually discover opportunities, onboard within bounded authority, contribute verifiable work and earn/spend native tokens. Genuine observable activity could help humans discover useful infrastructure organically without traditional marketing as the primary mechanism. This is not a demonstrated capability, monetary-value claim or adoption guarantee. Never manufacture wallet activity, trades or misleading signals; synthetic tests remain labelled. See the [five research scopes](research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md).

A small two-agent transaction is the first engineering milestone toward this broader network ambition. It does not define the final Genesis architecture.

## Status

Genesis is in early-stage experimental research. Experiment 001 now includes the local Solidity escrow and separate Python requester/provider processes, with bounded synthetic-fund Anvil integration tests. See the [experiment specification](docs/experiments/EXPERIMENT_001.md) and [coverage and limitations](docs/experiments/EXPERIMENT_001_ESCROW_COVERAGE.md). Local test results do not establish production security, fair exchange, or an independently audited system.

No final independent network architecture, production blockchain, native token, ticker, or final consensus algorithm has been selected; no novel consensus protocol has been validated. An independent permissionless Layer 1 and native human/machine economy are the long-term research goal. AI mining or rewards through verified contributions, genuine human utility, consensus, Sybil resistance and sustainable economics remain unproven research questions; existing and non-chain systems remain comparison baselines. Ethereum-compatible local tooling is an experiment fixture, not a commitment to Ethereum as the final network. No tokenomics, presale, or launch date is approved.

Development follows explicit research questions and scoped experiments. Prior art, assumptions, security limits, hypotheses, and negative results must be documented before making claims.

## Research Results

[Experiment 001 research report](research/reports/EXPERIMENT_001_REPORT.md) — **CONDITIONAL PASS** for a bounded local service exchange. Separate Python requester/provider processes independently verified a deterministic result and settled synthetic payment on Anvil; the final validation milestone recorded 112 passing tests (58 Solidity, 54 Python). The report includes reproduction commands, adversarial findings, all 18 invariant assessments, and limitations. Requester-veto fairness and independent auditing remain unresolved; this is not production assurance or validation of a Genesis consensus mechanism.

## Start here

| Researcher's question | Documentation |
| --- | --- |
| What is Genesis, and what is established? | [Project context](docs/PROJECT_CONTEXT.md), [canonical charter](MASTER_PLAN.md), [decision register](docs/DECISION_REGISTER.md) |
| What is being investigated? | [Research specification](docs/RESEARCH_SPEC.md), [protocol hypotheses](docs/PROTOCOL_HYPOTHESES.md), [AI-earned native tokens and economic utility](research/economics/AI_EARNED_NATIVE_TOKENS_AND_UTILITY.md) |
| What could the long-term network include? | [Future network architecture research](docs/FUTURE_NETWORK_ARCHITECTURE.md), [conditional roadmap](docs/ROADMAP.md) |
| What does the first experiment specify and test? | [Experiment 001](docs/experiments/EXPERIMENT_001.md), [architecture](docs/architecture/EXPERIMENT_001_ARCHITECTURE.md), [coverage and limitations](docs/experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) |
| What are the security assumptions? | [Threat model](docs/THREAT_MODEL.md), [security invariants](docs/SECURITY_INVARIANTS.md) |
| How can I reproduce the local escrow tests? | [Contract setup and tests](contracts/README.md), [agent experiment instructions](sdk/python/README.md), [dependency pins](DEPENDENCIES.md) |
| Where is project history and current work recorded? | [Reconstructed brainstorm](research/history/ORIGINAL_BRAINSTORM.md), [research journal](docs/RESEARCH_JOURNAL.md), [session handoff](docs/SESSION_HANDOFF.md) |

## Research pillars

1. **Verifiable Autonomous Work** — independently verified contributions and bounded earning/payment.
2. **Independent Network Security** — secure permissionless consensus and resistance to Sybil attacks, including AI swarms.
3. **Human and Machine Economy** — meaningful human-to-human, human-to-machine and machine-to-machine use of the same native asset; investigate sustainable demand, fees, incentives and issuance without selecting parameters.

Long-term adaptability to AI, computing, robotics, cryptography and communications is a research requirement, not guaranteed future-proofing. See the [final Experiment 002 proposal](docs/experiments/EXPERIMENT_002_FINAL_SPEC.md) and [Task 006 design review](docs/experiments/EXPERIMENT_002_DESIGN_REVIEW.md); Experiment 002 is an accepted bounded local design after [blocker resolution](docs/experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md), READY for separate implementation authorization and still unimplemented.

## Cross-cutting technical tracks

1. **Autonomous Economic Authority** — cryptographic identity, bounded authority, delegation, wallets, agreements, and settlement.
2. **Verifiable Coordination** — discovery, negotiation, independently verifiable services and contributions, and offline coordination.
3. **Autonomous Network Security** — Sybil resistance, collusion, consensus and network research, economic security, and protocol evolution.

## Research discussion and contributions

Start with the [welcome discussion](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/1) for scope and research questions. The [requester-veto fairness discussion](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/2) examines an unresolved limitation: a requester can withhold acceptance after correct provider work, preventing payment. Discussion does not approve an architectural change.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a focused research task with prior art, assumptions, deliverables, and falsifiable acceptance criteria. Security concerns follow [SECURITY.md](SECURITY.md). Historical brainstorms in `research/history/` are public reconstructions, not approved architecture or verbatim transcripts. Do not include secrets or private notes in public contributions.
