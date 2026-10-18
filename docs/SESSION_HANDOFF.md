# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-18

### Current status

Genesis's goal is an independent permissionless AI-first L1/native economy shared by humans and machines, with eventual bounded autonomous discovery/earning/spending and possible organic human discovery through genuine activity. These are aspirations, not current discovery/token-value/adoption capabilities. Experiment 001 remains published CONDITIONAL PASS and unchanged. **Task 008 resolves B-DEP/B-FEE; ADR 0002 is Accepted for bounded local design, READY for separate implementation authorization.** Experiment 002 remains unimplemented.

### Completed work

- [Blocker resolution](experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md) selects constrained exact-baseline reuse with source restrictions and accepted residual local-only risks. Fresh offline build, 58 Solidity/54 Python regressions, 39 installed pins, 35 vendored hashes, pip check, 25 Cast digests/34 EVM/Python recoveries pass. Initial premature Python run failed on a missing build artifact; sequential rerun passed unchanged.
- [Bounded costs](experiments/EXPERIMENT_002_BOUNDED_COST_MODEL.md) document existing 3 gwei maximum/1 gwei priority fields overlooked in Task 007, independent principal/fee/run budgets, pre-signing reservations, no top-ups/escalation, failed/ambiguous transactions, runtime and loss assumptions. Integer checks cover 20 fee cases; two unchanged Experiment 001 controls settle/refund and stop children. None is Experiment 002 protocol evidence.
- Updated [final specification revision 2](experiments/EXPERIMENT_002_FINAL_SPEC.md)/ADR/readiness references. All earlier future P2/T01–T20/vector/fee tests remain required.
- [ADR 0004](adr/0004-autonomous-bootstrapping-research-direction.md) preserves founder direction and no-manufactured-signals rule. Five [bootstrapping research scopes](../research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md) cover discovery, external funding/issuance, useful/duplicate work, fixed-resource Sybils and human discovery. They remain plans, not implemented experiments.
- Public [compatibility tools/instructions](../research/compatibility/experiment002/README.md) reproduce stateless vector and arithmetic checks; no signing keys, protocol implementation, transactions or contract deployment in those probes. Original code/pins/CI/public evidence preserved.

### Open questions

- Future implementation must enforce budgets, source restrictions, signatures/ABI/state/recovery behavior and fit fixed gas ceilings. A feature/dependency/budget change reopens review; READY is not implementation/experimental acceptance.
- General/confidential fair exchange, inclusion/finality, key/host failures, absent callers and late work remain limitations.
- Initial agent resources/funding provenance, genuine beneficiary demand, useful/unique contribution, fixed-resource Sybil resistance, native issuance/security, stable settlement and human adoption remain research questions. No supply/ticker/consensus/valuation/launch selected.

### Next task

Recommended: separately authorize a small isolated Experiment 002 escrow implementation against the accepted final specification and constrained tuple, with full tests/source review/gas measurement and unchanged Experiment 001 controls. Do not implement automatically. Separately refine read-only AB-01 and funding-provenance AB-02 before any bootstrapping experiment; no public deployment or user recruitment follows.

### Blockers

No material scoped design blocker remains after Task 008; no Git blocker known. Mandatory future implementation evidence is outstanding. Compatibility does not eliminate old runtime/compiler/CCIP/installer risks, trusted host/RPC assumptions or arbitrary-censorship/payment limits. Broader economic/adoption/Sybil questions are unresolved; never fabricate activity to mask them.

### Relevant commits

- `239a235` — foundation; `606a52c` — vision preservation; `e872efb` — reviewed routine commit/push default; `ed13296` — continuity hardening.
- `5701aee` — Experiment 001 specification; `db7da99` / `cb64036` — escrow and official tool-pin correction; `59375be` — separate-agent integration.
- [`f66cda9`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77) — final Experiment 001 adversarial review/112-test milestone; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966).
- [`418d310`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/418d3105ab96729cf01233bbcb0cde3aaee808be) — report publication; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39064529125); [publication Discussion](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/3).
- [`d41d2f4`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d41d2f41c78070f4f89d5ea7e8b3f28353fe998a) — Task 005 proposal; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39114654576), 58 Solidity / 54 Python tests plus end-to-end. Not Experiment 002 execution evidence.
- [`ded3fff`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/ded3fff203145cd8ec50fb3d91cca916a95cb331) — Task 006 vision alignment/review; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39115815952), 58 Solidity / 54 Python plus end-to-end.
- [`d05d690`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d05d69008229cbb10f437eb622d88b11cc09bfdd) — Task 007 specification/vectors/economics; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39116760576), 58 Solidity/54 Python plus end-to-end.
- Task 008 blocker/vision/checks commit: resolve with `git log -1 -- docs/SESSION_HANDOFF.md`; inspect its Actions run. Existing workflow checks Experiment 001; new compatibility scripts and Experiment 002 are not automatically part of that workflow.

### Canonical documents

- [MASTER_PLAN.md](../MASTER_PLAN.md), [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [DECISION_REGISTER.md](DECISION_REGISTER.md), [ROADMAP.md](ROADMAP.md), [RESEARCH_JOURNAL.md](RESEARCH_JOURNAL.md).
- [RESEARCH_SPEC.md](RESEARCH_SPEC.md), [PROTOCOL_HYPOTHESES.md](PROTOCOL_HYPOTHESES.md), [FUTURE_NETWORK_ARCHITECTURE.md](FUTURE_NETWORK_ARCHITECTURE.md), [THREAT_MODEL.md](THREAT_MODEL.md).
- [Experiment 001 specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), [18 invariants](SECURITY_INVARIANTS.md), [coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md), [security review](experiments/EXPERIMENT_001_SECURITY_REVIEW.md), [report](../research/reports/EXPERIMENT_001_REPORT.md), [ADR 0001](adr/0001-experiment-001-architecture.md), [dependency pins](../DEPENDENCIES.md).
- [Experiment 002 research comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md), [proposal](experiments/EXPERIMENT_002.md), [architecture](architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat model](experiments/EXPERIMENT_002_THREAT_MODEL.md), [test plan](experiments/EXPERIMENT_002_TEST_PLAN.md), [accepted local-design ADR 0002](adr/0002-experiment-002-fair-exchange.md).
- [Experiment 002 design review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md) and [ADR 0003 research direction](adr/0003-independent-l1-research-direction.md).
- [Experiment 002 final specification](experiments/EXPERIMENT_002_FINAL_SPEC.md), [vectors](experiments/EXPERIMENT_002_SIGNING_VECTORS.md), [dependency assessment](experiments/EXPERIMENT_002_DEPENDENCY_REVIEW.md), [economic foundations](../research/economics/AI_EARNED_NATIVE_TOKENS_AND_UTILITY.md).
- [Task 008 resolution](experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md), [cost model](experiments/EXPERIMENT_002_BOUNDED_COST_MODEL.md), [ADR 0004](adr/0004-autonomous-bootstrapping-research-direction.md), [five bootstrapping scopes](../research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md), [compatibility instructions](../research/compatibility/experiment002/README.md).
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
