# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-18

### Current status

Genesis retains its independent permissionless AI-first L1/native human-and-machine economy research goal and autonomous bootstrapping aspiration. No token, consensus or organic adoption is demonstrated. Experiment 001 remains published CONDITIONAL PASS and unchanged. **Task 009: Experiment 002 partial contract implementation; acceptance FAIL / implementation BLOCKED by B-ANVIL-FEE-EVIDENCE.** ADR 0002 remains accepted bounded local design, not experimental acceptance.

### Completed work

- [Isolated escrow](../contracts/src/Experiment002Escrow.sol), [adversarial/stateful tests](../contracts/test/Experiment002Escrow.t.sol) and [frozen-vector tests](../contracts/test/Experiment002Vectors.t.sol). All 86 Solidity tests pass (original 58 + new 28), with unchanged compiler/dependency/fuzz/invariant baseline.
- [Blocking review](experiments/EXPERIMENT_002_IMPLEMENTATION_REVIEW.md), [bounded local reproducer](../research/compatibility/experiment002/check_anvil_fee_receipt.py) and [numeric evidence](../research/compatibility/experiment002/task009-fee-receipt-evidence.json). Deployment uses 1,632,623 gas, below 2,000,000. At a controlled fee boundary, receipt effectiveGasPrice is 3.625 gwei while the signed maximum and observed debit imply 3 gwei. The reproducer exits 2; this is a blocker, not a passing test.
- Partial separate-process agent work/tests are retained in ignored `internal/task009/unpublished/`; no complete runner or agent acceptance is published. A preliminary 36-method suite had one method with two fee-boundary errors; no assertions were weakened. Published original Python controls remain separate evidence.
- Existing CI, Experiment 001 source/tests/publication, signatures, pins, node/compiler flags and budget/design semantics remain unchanged. Final CI checks published Solidity plus original agent controls, not Experiment 002 acceptance. Locate publication commit using Git history for this file.

### Open questions

Root cause/scope of the pinned-node canonical receipt/debit contradiction; reviewed corrected dependency versus explicitly revised evidence policy; full T01–T20/P2/fee/resource integration evidence. General fairness, censorship/inclusion/finality, host/key failures, useful-work uniqueness, consensus security, native economics and genuine adoption remain unresolved.

### Next task

Recommended: independently reproduce B-ANVIL-FEE-EVIDENCE, review an explicit compatibility/evidence resolution, and update readiness through ADR/register before resuming Task 009. Do not start a new experiment, bootstrap implementation or token.

### Blockers

**B-ANVIL-FEE-EVIDENCE:** required canonical fee calculation disagrees with actual wallet accounting. Dependency compatibility/fee-evidence readiness reopened; specified finite fee policy remains unchanged. No workaround, upgrade or budget increase approved. Partial agent draft requires review/retesting; do not infer integration readiness from contract tests or preliminary local output.

### Relevant commits

- `239a235` — foundation; `606a52c` — vision preservation; `e872efb` — reviewed routine commit/push default; `ed13296` — continuity hardening.
- `5701aee` — Experiment 001 specification; `db7da99` / `cb64036` — escrow and official tool-pin correction; `59375be` — separate-agent integration.
- [`f66cda9`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77) — final Experiment 001 adversarial review/112-test milestone; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966).
- [`418d310`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/418d3105ab96729cf01233bbcb0cde3aaee808be) — report publication; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39064529125); [publication Discussion](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/3).
- [`d41d2f4`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d41d2f41c78070f4f89d5ea7e8b3f28353fe998a) — Task 005 proposal; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39114654576), 58 Solidity / 54 Python tests plus end-to-end. Not Experiment 002 execution evidence.
- [`ded3fff`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/ded3fff203145cd8ec50fb3d91cca916a95cb331) — Task 006 vision alignment/review; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39115815952), 58 Solidity / 54 Python plus end-to-end.
- [`d05d690`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d05d69008229cbb10f437eb622d88b11cc09bfdd) — Task 007 specification/vectors/economics; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39116760576), 58 Solidity/54 Python plus end-to-end.
- [`f41216f`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f41216fae335a83cc758d11033d2066397a4f0aa) — Task 008 blocker/vision/checks; [baseline CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39117831964).
- Task 009 partial escrow/blocker publication: resolve with `git log -1 -- docs/SESSION_HANDOFF.md`; inspect its regression Actions run. This does not establish Experiment 002 integration/fee acceptance.

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
