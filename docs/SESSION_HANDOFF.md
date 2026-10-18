# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-18

### Current status

Genesis retains the independent permissionless AI-first L1/native human-and-machine economy and bootstrapping research direction; no chain/consensus/token/adoption result is claimed. Experiment 001 remains published CONDITIONAL PASS and unchanged. **Task 011 infrastructure compatibility PASS for ADR 0005's corrected Anvil profile, subject to publication Ubuntu CI.** When CI passes, the fee-reporting blocker is resolved for that profile. Experiment 002 still lacks accepted full agent integration; agents stayed paused throughout Task 011.

### Completed work

- [Validation](experiments/EXPERIMENT_002_ANVIL_VALIDATION.md)/[ADR 0005](adr/0005-experiment-002-corrected-anvil-baseline.md): isolated Anvil v1.6.0-rc1 / b272ce3366987406406e9eb1b82596653a3ad628, explicit Cancun. [Manifest/installer](../research/compatibility/experiment002/anvil-candidate.json) verify source/archive/binary hashes before execution; no global/PATH or old-tool replacement. Existing Forge/Cast/compiler/library/Python pins and limits remain.
- [44-case comparison](../research/compatibility/experiment002/task011-comparison.json): old 12 reconciled/eight contradictory/two unincluded; corrected 20 reconciled/zero contradictory/two unincluded. Same strict oracle and original escrow probe, no normalization/cap increase. Corrected probe deployment remains 1,632,623 gas.
- 86 Solidity tests, unchanged 54 Python tests on each node, 14 old research and nine candidate tests pass locally (217 executions). Both signature probes match 25 digests/34 signatures; 20 fee cases pass. Candidate success/refusal controls preserve requester veto. [Actual-node regression metadata](../research/compatibility/experiment002/task011-regressions.json) distinguishes the old fixture's historical version label.
- CI adds verified Linux candidate installation and identical matrix/signature/original-control gates. Inspect the publication commit's Actions run; failure retains/reopens BLOCKED. [Provenance](../research/compatibility/experiment002/task011-provenance.json) preserves setup failures, hash/source identities and attestation 404; no crypto-attestation, reproducible-build or comprehensive audit claim.

### Open questions

Full Experiment 002 T01–T20/P2/fee/resource and fault-recovery evidence; verified accounting with principal flows; general fairness/disclosure/inclusion/deadlines/finality, host/key and supply-chain risks. Future useful-work/Sybil/security/native economics/adoption remain unresolved. A new platform/node feature, integrity mismatch or CI failure reopens compatibility.

### Next task

After required CI passes, recommend Task 009 continuation using only ADR 0005's explicit verified node. Review the ignored partial draft before integrating; complete all tests/gas budgets/security assessment without changing consent rules. Task 011 does not itself authorize resuming agents or starting another experiment/token/bootstrapping implementation.

### Blockers

No known local infrastructure blocker on the verified macOS profile. Ubuntu CI is mandatory before final cross-platform readiness; then B-ANVIL-FEE-EVIDENCE is resolved for the manifest profile. Experiment 002 acceptance remains pending complete implementation/security evidence. Never use the old node as if its fee check passed or weaken the check for either node.

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
- [`b7ba71b`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/b7ba71b41e8e1c48d1427677eee5ed0207f4606e) — Task 010 diagnosis; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39120325081).
- Task 011 corrected-node publication: locate with Git history for this file and verify its Actions run. Infrastructure PASS does not mean Experiment 002 acceptance.

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
