# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-18

### Current status

Genesis retains its independent permissionless AI-first L1/native human-and-machine economy and bootstrapping research direction; these are aspirations, not demonstrated consensus/token/adoption capabilities. Experiment 001 remains published CONDITIONAL PASS and unchanged. Experiment 002 has the partial Task 009 escrow but no accepted/published complete agent workflow. **Task 010 conclusion: STILL BLOCKED**, with the fee-reporting root cause diagnosed. ADR 0002 remains accepted design only.

### Completed work

- [Fee investigation](experiments/EXPERIMENT_002_FEE_INVESTIGATION.md): pinned Anvil omits total-fee clamping in mined receipt/transaction RPC prices. Actual wallet charges and EVM GASPRICE agree with the signed cap. No excess debit observed.
- [Raw-RPC probe](../research/compatibility/experiment002/investigate_fee_receipts.py), [test-only opcode witness](../contracts/test/FeeWitness.sol), strict oracle and 14 research tests. Two repeats of 11 cases give 12 reconciled, eight contradictory and two not included; [full public evidence](../research/compatibility/experiment002/task010-fee-evidence.json) records raw fields/balances/versions/cleanup. The default diagnostic and unchanged Task 009 reproducer return 2 to preserve the blocker.
- Existing Solidity/Python controls, pins, signed fixtures, escrow code and fee caps remain unchanged. CI adds only a clearly named defect-characterization step with the existing read-only permissions/actions. Green CI does not mean Experiment 002 readiness.
- Upstream fix and a source-reviewed v1.8.5 candidate are documented. A single archive download timed out; unverified partial bytes were never executed/adopted. No candidate runtime/full compatibility evidence exists. The incomplete agents under ignored `internal/task009/unpublished/` were not resumed.

### Open questions

Which exact corrected-node tuple satisfies full local/CI compatibility and supply-chain review? How will the resumed workflow reconcile fee evidence together with principal and concurrent flows? All T01–T20/P2/fee/resource integration gates remain. Broader fairness, inclusion/finality, trusted-host/key failures, useful-work uniqueness, native economics/consensus and organic adoption remain unresolved.

### Next task

Recommended: verify an explicit corrected-node candidate and test both RPC reporting paths against the strict matrix, original reproducer and full regressions. Record reviewed dependency adoption before resuming Task 009. Do not resume agents under Task 010 or start a new experiment/token/bootstrap implementation.

### Blockers

**B-ANVIL-FEE-EVIDENCE remains open:** source-level root cause identified but no verified compatible corrected runtime adopted. The equation/caps remain valid; replacing reported fees with computed values, hiding clamp cases or increasing caps is prohibited. Partial agents require review and full acceptance evidence after resolution.

### Relevant commits

- `239a235` — foundation; `606a52c` — vision preservation; `e872efb` — reviewed routine commit/push default; `ed13296` — continuity hardening.
- `5701aee` — Experiment 001 specification; `db7da99` / `cb64036` — escrow and official tool-pin correction; `59375be` — separate-agent integration.
- [`f66cda9`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77) — final Experiment 001 adversarial review/112-test milestone; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966).
- [`418d310`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/418d3105ab96729cf01233bbcb0cde3aaee808be) — report publication; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39064529125); [publication Discussion](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/3).
- [`d41d2f4`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d41d2f41c78070f4f89d5ea7e8b3f28353fe998a) — Task 005 proposal; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39114654576), 58 Solidity / 54 Python tests plus end-to-end. Not Experiment 002 execution evidence.
- [`ded3fff`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/ded3fff203145cd8ec50fb3d91cca916a95cb331) — Task 006 vision alignment/review; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39115815952), 58 Solidity / 54 Python plus end-to-end.
- [`d05d690`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d05d69008229cbb10f437eb622d88b11cc09bfdd) — Task 007 specification/vectors/economics; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39116760576), 58 Solidity/54 Python plus end-to-end.
- [`f41216f`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f41216fae335a83cc758d11033d2066397a4f0aa) — Task 008 blocker/vision/checks; [baseline CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39117831964).
- [`aa484cd`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/aa484cd0355131a8fb3cac5db5898bb97a3786a1) — Task 009 partial escrow/blocker; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39119076562).
- Task 010 investigation publication: locate using Git history for this file; inspect its regression/characterization Actions run. Neither is Experiment 002 acceptance.

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
