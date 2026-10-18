# Genesis Project Context

## What Genesis is

Genesis is RASL’s temporary-codename, open-source, research-first initiative exploring foundational infrastructure for economic coordination among autonomous intelligences and systems. The mission spans humans, software agents, robots, machines, vehicles, sensors, satellites, distributed systems, and future entities. The central question is whether unfamiliar, independently operated participants can establish verifiable agreements, exchange resources, and coordinate safely without trusting each other or a central platform.

## What Genesis is not

Genesis is not only an AI-agent payment application. It is not currently a production blockchain, token, wallet, smart-contract system, or autonomous network. No new consensus protocol or cryptographic primitive has been invented or validated here. A Bitcoin-scale foundational ambition is an aspiration, not an achievement or novelty claim.

## Current research status and milestone

Status: early-stage experimental research. Current milestone: project foundation and prior-art mapping, with a small, bounded two-agent independently verifiable economic transaction experiment identified as the first implementation milestone. It is a first step, not the long-term product definition. Any experiment requires a scoped task, synthetic actors/data, and explicit validation criteria. Task 002B now provides a proposed, implementation-oriented [Experiment 001 specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), and [security invariants](SECURITY_INVARIANTS.md). Task 003A implements and locally tests the Solidity escrow only, with pinned dependencies and GitHub CI. [ADR 0001](adr/0001-experiment-001-architecture.md) is accepted for that component; [coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) lists remaining invariant integration checks. Task 003B adds separate-process Python requester/provider agents and local Anvil end-to-end tests, preserving requester veto. See [local reproduction](../sdk/python/README.md) and the coverage map for tested and pending cases. Task 003C records a [project-assisted adversarial review](experiments/EXPERIMENT_001_SECURITY_REVIEW.md) and CONDITIONAL PASS for this bounded local experiment. Task 004 publishes the [Experiment 001 research report](../research/reports/EXPERIMENT_001_REPORT.md) with immutable evidence and reproduction instructions. The result remains conditionally accepted; independent review and documented residual conditions remain open. Task 005 now provides a [fair-exchange comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md) and **Proposed** [Experiment 002 design](experiments/EXPERIMENT_002.md): upfront consent to a fixed result predicate, with no post-funding requester veto for timely valid claims. This is a separate consent policy, not a change to Experiment 001. Public-result leakage, non-inclusion and deadlines still prevent a general fairness guarantee. [ADR 0002](adr/0002-experiment-002-fair-exchange.md) remains Proposed; design review and separate implementation authorization are the next recommended steps. No Experiment 002 results exist. No public-chain or future Genesis consensus result is established.

## Core principles

“The network must not need to trust the intelligence of its participants. It must only need to verify their actions.” Treat this as a research principle, not a proven universal property. Prioritize bounded cryptographic authority, security, verifiability, interoperability, open participation, privacy, resilience, and honest reporting of uncertainty.

## Major decisions

RASL is the research organization; Genesis is temporary codename; development is open-source and research-first; the three tracks are Autonomous Economic Authority, Verifiable Coordination, and Autonomous Network Security; no premature token or consensus claims; no uncontrolled autonomous replication or unauthorized infrastructure use; and no permanent Ethereum commitment. There is no selected network name, ticker, consensus algorithm, tokenomics, or final architecture.

See [`DECISION_REGISTER.md`](DECISION_REGISTER.md) for the canonical register.

## Unresolved decisions

Whether an independent L1 is justified; whether any native asset is necessary; which consensus or non-consensus architecture fits requirements; whether useful contribution can be measured and where it belongs; how authority, discovery, execution, governance, upgrades, and offline operation should work; and which permanent name is suitable. APoC is only an internal research hypothesis.

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
