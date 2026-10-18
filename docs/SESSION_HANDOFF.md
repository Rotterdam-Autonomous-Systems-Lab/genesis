# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-18

### Current status

Genesis remains early-stage research into broad permissionless economic infrastructure, including a possible independent network. Experiment 001 is published with **CONDITIONAL PASS** and unchanged requester-veto semantics. Task 005 supplies a research-only Experiment 002 proposal; no implementation, new test results or adopted architecture follows.

### Completed work

- Preserved [Experiment 001's published report](../research/reports/EXPERIMENT_001_REPORT.md), implementation and 112-test milestone (58 Solidity / 54 Python); no code or baseline evidence changed.
- Compared six established [fair-exchange mechanism families](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md), with primary sources, immutable open-source references and explicit inspection limits.
- Proposed a [bounded Experiment 002](experiments/EXPERIMENT_002.md), [architecture](architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat model](experiments/EXPERIMENT_002_THREAT_MODEL.md), [test plan](experiments/EXPERIMENT_002_TEST_PLAN.md) and **Proposed** [ADR 0002](adr/0002-experiment-002-fair-exchange.md).
- Recommendation: upfront consent to a fixed deterministic predicate permits provider collection without a second requester approval, conditional on a timely canonical claim. Documented output-leakage/censorship/expiry counterexample prevents a general fairness claim. Updated roadmap, journal, decision register and context.

### Open questions

- Accept/reject the upfront-consent change and bounded conditional-collectability research question; no design approval recorded yet.
- Which useful task justifies outsourcing with cheap objective verification? Addition isolates the veto but does not establish useful work.
- How to bind confidential delivery/payment, accommodate offline or satellite delays, and verify subjective AI or physical tasks without disguising oracle trust?
- Whether challenger/proof systems justify their costs; no measurements or completed exhaustive literature review exist.
- Final network/consensus/asset/governance/economics remain open under the canonical charter.

### Next task

Recommended: founder/design review of the Experiment 002 proposal, explicit consent semantics, leakage/deadline limitations and tests. If approved, separately authorize small local implementation with reviewed/frozen schemas and digest vectors, dependency-maintenance review, pinned tools and tested reproduction commands. Do not implement automatically or change Experiment 001.

### Blockers

No repository or specification contradiction discovered in this documentation task. Implementation is not authorized. Proposal review, schema/vector review and dependency maintenance are required pre-implementation gates. Full-paper/source audits were not performed; source-access/inspection limits are recorded. General fair exchange and requester-veto fairness for subjective/physical work remain unresolved. Experiment 001's independent-review and residual supply-chain/fault conditions remain open.

### Relevant commits

- `239a235` — foundation; `606a52c` — vision preservation; `e872efb` — reviewed routine commit/push default; `ed13296` — continuity hardening.
- `5701aee` — Experiment 001 specification; `db7da99` / `cb64036` — escrow and official tool-pin correction; `59375be` — separate-agent integration.
- [`f66cda9`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77) — final Experiment 001 adversarial review/112-test milestone; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966).
- [`418d310`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/418d3105ab96729cf01233bbcb0cde3aaee808be) — report publication; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39064529125); [publication Discussion](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/3).
- Task 005 documentation commit: recover its exact hash with `git log -1 -- docs/SESSION_HANDOFF.md`; inspect that commit's Actions run for regression status. It is not Experiment 002 execution evidence.

### Canonical documents

- [MASTER_PLAN.md](../MASTER_PLAN.md), [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [DECISION_REGISTER.md](DECISION_REGISTER.md), [ROADMAP.md](ROADMAP.md), [RESEARCH_JOURNAL.md](RESEARCH_JOURNAL.md).
- [RESEARCH_SPEC.md](RESEARCH_SPEC.md), [PROTOCOL_HYPOTHESES.md](PROTOCOL_HYPOTHESES.md), [FUTURE_NETWORK_ARCHITECTURE.md](FUTURE_NETWORK_ARCHITECTURE.md), [THREAT_MODEL.md](THREAT_MODEL.md).
- [Experiment 001 specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), [18 invariants](SECURITY_INVARIANTS.md), [coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md), [security review](experiments/EXPERIMENT_001_SECURITY_REVIEW.md), [report](../research/reports/EXPERIMENT_001_REPORT.md), [ADR 0001](adr/0001-experiment-001-architecture.md), [dependency pins](../DEPENDENCIES.md).
- [Experiment 002 research comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md), [proposal](experiments/EXPERIMENT_002.md), [architecture](architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat model](experiments/EXPERIMENT_002_THREAT_MODEL.md), [test plan](experiments/EXPERIMENT_002_TEST_PLAN.md), [proposed ADR 0002](adr/0002-experiment-002-fair-exchange.md).
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
