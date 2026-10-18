# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-18

### Current status

Genesis's founder-defined long-term research goal is an independent permissionless L1/native economy for humans and machines, with AI mining/earning through independently verified contributions subject to verification, consensus, Sybil and economic research. No final mechanism, token parameters or sustainable outcome exists. Experiment 001 remains published CONDITIONAL PASS. Task 006 reviews Experiment 002: **amend and remain Proposed**, not implementation-ready. No implementation occurred.

### Completed work

- [ADR 0003](adr/0003-independent-l1-research-direction.md) records the explicit Task 006 research goal and three planning pillars: Verifiable Autonomous Work, Independent Network Security and Human and Machine Economy. Original technical tracks remain cross-cutting methods.
- Aligned charter, vision, README, agent instructions, architecture territory, research hypotheses/specification, roadmap, decisions and context. Preserve meaningful human-to-human, human-to-machine and machine-to-machine utility and adaptability without guaranteed future-proofing.
- [Design review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md) evaluates veto resistance, provider payment, disclosure, censorship/deadlines, authority/replay, objective verification and independent-chain compatibility. Amended H2-C to conditional refund availability/exclusive outcomes; added provider-progress reporting and T18–T20 controls for late funding, absent callers and repeated work.
- Preserved Experiment 001's code, tests, report and evidence. Task 005's six-family comparison remains a scoped review with source-access limitations; no new empirical or prior-art discovery is claimed.

### Open questions

- R1: explicitly accept/reject the narrowed Experiment 002 scope and upfront-consent policy, including public disclosure, strict deadlines and conditional payment.
- R2/R3: freeze schemas/digest vectors, timing/recovery/code/run checks and reviewed dependency/test/reproduction setup before implementation.
- Useful/unique contribution and verification costs, AI-Sybil/security resources, human demand and native-token sustainability remain unproven. Native asset design, issuance, consensus, governance and final architecture remain unselected.
- Subjective/physical verification, confidential delivery, delayed/satellite operation and cryptographic migration need separate work; the sum fixture supplies no guarantees for them.

### Next task

Recommended: small Experiment 002 specification-finalization task to close R1–R3 and explicitly accept/reject ADR 0002. If accepted, separately authorize a bounded isolated escrow implementation, retaining Experiment 001 unchanged. Do not implement automatically or infer token/consensus authorization.

### Blockers

Task 006 documentation is complete; no Git blocker is known. Experiment 002 implementation remains gated by R1–R3 and separate authorization. Disclosure/non-inclusion can leave correct work unpaid; key loss, missing actors and ledger failure can prevent progress. Experiment 001's independent-review and residual dependency/fault conditions remain open. No complete future-proofing or general fair-exchange claim.

### Relevant commits

- `239a235` — foundation; `606a52c` — vision preservation; `e872efb` — reviewed routine commit/push default; `ed13296` — continuity hardening.
- `5701aee` — Experiment 001 specification; `db7da99` / `cb64036` — escrow and official tool-pin correction; `59375be` — separate-agent integration.
- [`f66cda9`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77) — final Experiment 001 adversarial review/112-test milestone; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966).
- [`418d310`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/418d3105ab96729cf01233bbcb0cde3aaee808be) — report publication; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39064529125); [publication Discussion](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/3).
- [`d41d2f4`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d41d2f41c78070f4f89d5ea7e8b3f28353fe998a) — Task 005 proposal; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39114654576), 58 Solidity / 54 Python tests plus end-to-end. Not Experiment 002 execution evidence.
- Task 006 documentation/review commit: resolve with `git log -1 -- docs/SESSION_HANDOFF.md`; inspect its Actions run for regression status. Do not predeclare success or treat it as Experiment 002 evidence.

### Canonical documents

- [MASTER_PLAN.md](../MASTER_PLAN.md), [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [DECISION_REGISTER.md](DECISION_REGISTER.md), [ROADMAP.md](ROADMAP.md), [RESEARCH_JOURNAL.md](RESEARCH_JOURNAL.md).
- [RESEARCH_SPEC.md](RESEARCH_SPEC.md), [PROTOCOL_HYPOTHESES.md](PROTOCOL_HYPOTHESES.md), [FUTURE_NETWORK_ARCHITECTURE.md](FUTURE_NETWORK_ARCHITECTURE.md), [THREAT_MODEL.md](THREAT_MODEL.md).
- [Experiment 001 specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), [18 invariants](SECURITY_INVARIANTS.md), [coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md), [security review](experiments/EXPERIMENT_001_SECURITY_REVIEW.md), [report](../research/reports/EXPERIMENT_001_REPORT.md), [ADR 0001](adr/0001-experiment-001-architecture.md), [dependency pins](../DEPENDENCIES.md).
- [Experiment 002 research comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md), [proposal](experiments/EXPERIMENT_002.md), [architecture](architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat model](experiments/EXPERIMENT_002_THREAT_MODEL.md), [test plan](experiments/EXPERIMENT_002_TEST_PLAN.md), [proposed ADR 0002](adr/0002-experiment-002-fair-exchange.md).
- [Experiment 002 design review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md) and [ADR 0003 research direction](adr/0003-independent-l1-research-direction.md).
- [Original brainstorm](../research/history/ORIGINAL_BRAINSTORM.md) remains a reconstruction, not a transcript or approved design; [context recovery](../research/history/CONTEXT_RECOVERY.md).

## Reusable handoff template

Copy and complete this section after a significant task. Use specific commit hashes and repository-relative links where available. Mark unknowns explicitly rather than guessing.

### Current status

[Project status and active milestone]

### Completed work

[Concrete outcomes and relevant files]

### Open questions

[Unresolved decisions or research questions]

### Next task

[Next authorized or recommended task; label recommendations]

### Blockers

[Current blockers, or “None known” with scope]

### Relevant commits

[Commit hashes and concise descriptions]

### Canonical documents

[Links to the documents needed to resume safely]
