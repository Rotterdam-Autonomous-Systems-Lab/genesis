# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-18 (Task 013)

### Current status

**Experiment 002 security/evidence closure BLOCKED pending remediation**, per [review](experiments/EXPERIMENT_002_INDEPENDENT_REVIEW.md). Task 012 narrow no-second-signature conditional collectability is reproduced, not upgraded to PASS. Its [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39137210473). No confirmed unauthorized principal payout, replay or cap bypass was found; this is not a formal/organizationally independent audit. Long-term Genesis vision, MASTER_PLAN, existing implementations and published evidence remain unchanged.

### Completed work

- Traced contract/agents/codec/signer/supervisor, frozen specs, cost/toolchain assumptions, tests and archived evidence at `2161dc2b32c2e4b872bf1ebfee63aa1b6b9a544c`.
- R013-01 Medium: aggregate supervisor audit accepts swapped credit owners. R013-02 Medium: inconsistent current receipt fee fields/transaction identities accept; preflight can allow a subsequent bounded send. R013-03 Low: ready barriers/signer do not enforce expired wall deadline before acting. R013-04 Medium: initial review CI errored at existing late-funding setup (funding reverted); exact failed-run timestamp evidence is unavailable.
- Seven [review characterization/control tests](../tests/experiment002/test_review013.py) reproduce findings, verify contract negative controls and archive arithmetic. Existing assertions/caps/code/pins are untouched. Green characterization tests mean unresolved defects reproduce, not that they were repaired.
- [Acceptance assessment](experiments/EXPERIMENT_002_AGENT_ACCEPTANCE.md) now points to the review; historical observations/archive are retained. Local regressions passed: 86 Solidity, 54 original Python and 59 Experiment 002 Python tests; check the review commit's Actions result.

### Open questions

Exact owner/terminal/liability reconstruction, complete cross-source fee/identity/intent checks, pre-signing/phase deadline enforcement. Broader inclusion/disclosure/finality/host/key/supply-chain and useful-work/native-economy questions remain unchanged.

### Next task

Recommend separately authorized minimal evidence-checker/deadline hardening. Convert accepting-bad-evidence characterization into rejection/no-new-send regression assertions; preserve budgets and normal/refusal/offline/deadline controls; re-review closure. Do not automatically begin another experiment, token, L1 or public bootstrapping.

### Blockers

R013-01/02 block mandatory P2-14/T12/T16 evidence closure. R013-03 needs explicit runtime remediation/disposition; R013-04 requires captured failure evidence and deterministic valid-late-funding setup. No implementation fix was authorized/performed in this review task. A passing CI is reproduction/regression evidence, not a clearance of the findings.

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
