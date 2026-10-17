# Research Journal

This journal records repository milestones supported by version-controlled artifacts. Historical entries use verified Git commit dates and contents. New entries describe the documentation in their own commit; locate that commit with Git history for this file. A specification milestone is not an experimental finding.

## 2026-10-17 — Repository foundation

Commit [`239a235`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/239a23574c012af9cd782b5bb17cb05b46e3665d) (`Initialize Genesis research repository`) established the initial repository foundation. The commit created 22 files, including the README, master plan, agent and contributor guidance, security and license proposal documents, initial research and threat-model documents, and reserved directories for future work. It did not implement a protocol, smart contracts, a blockchain node, or an agent system.

## 2026-10-17 — Vision and research-plan preservation

Commit [`606a52c`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/606a52c8bc2a6c48961f164af4da718ecc06b163) (`Preserve Genesis vision and research plan`) expanded the canonical project charter and README, added the future network architecture research territory, project context and decision register, expanded research specifications, hypotheses and roadmap, and created public history records for the recovered brainstorm, naming, and context recovery. The repository history records 14 files changed in this commit. `research/history/ORIGINAL_BRAINSTORM.md` identifies itself as a reconstruction from the supplied project brief and repository documents, not a verbatim transcript.

## 2026-10-17 — Experiment 001 architecture and security specification (Task 002B)

Added the proposed [Experiment 001 specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), [18 security invariants](SECURITY_INVARIANTS.md), and [ADR 0001](adr/0001-experiment-001-architecture.md); expanded the threat model and roadmap security gate. The design uses two separate local signers, bounded synthetic escrow, typed messages, independent requester verification, on-chain arithmetic checking, requester-signed Acceptance, and deterministic timeout refunds. The provider-fairness limitation is explicit: a requester may withhold Acceptance after correct work.

This is documentation only: no contracts, agent code, dependency installations, deployments, tests of an implementation, or experimental results are recorded. The ADR is Proposed. Next proposed task: review the specification and security gate, select exact dependency pins, and then separately authorize a small implementation task. Genesis's independent-network ambition, three research tracks, and unresolved native-asset/consensus questions are preserved.

## Source boundary

This journal does not infer events beyond the repository record. See [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) for current working context and the reusable handoff format.
