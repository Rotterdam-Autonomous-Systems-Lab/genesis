# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-18

### Current status

Genesis's long-term research goal remains an independent permissionless L1/native human-and-machine economy with verifiable AI contribution/earning and genuine human utility. Experiment 001 is unchanged, published CONDITIONAL PASS. Task 007 supplies Experiment 002 specification revision 1 and separate economic research foundations. ADR 0002 remains **Proposed; implementation readiness BLOCKED**. No Experiment 002 code or token exists.

### Completed work

- [Final specification](experiments/EXPERIMENT_002_FINAL_SPEC.md) freezes proposed signing/wire schemas, negotiation envelopes, constructor/function/event interfaces, authorization/funding/result/settlement/refund/accounting/deadline/retry semantics and acceptance criteria.
- [Public vector guide](experiments/EXPERIMENT_002_SIGNING_VECTORS.md) and [JSON](experiments/EXPERIMENT_002_SIGNING_VECTORS.json) contain seven signed agreement/auth/claim sets, four additional artifacts and five mutations with concrete state/time cases. Hashes/public recovery checked locally with existing libraries; ephemeral keys discarded, no private material or raw transactions retained. Not executed Experiment 002 tests.
- [Dependency review](experiments/EXPERIMENT_002_DEPENDENCY_REVIEW.md) records exact baseline refs/hashes, OSV scan of 39 pinned packages, compiler inventory/chronology caveat, runtime/installer/CI risks and no adopted replacements. Existing vendored hashes and pip check pass.
- [Economic foundations](../research/economics/AI_EARNED_NATIVE_TOKENS_AND_UTILITY.md) compares established research/networks, separates customer earnings/issuance/security rewards, and proposes E-01–E-05 token-free investigations of useful work, Sybil rewards, demand/sustainability and stable settlement trade-offs. Linked main research navigation; all earlier T01–T20 remain planned.

### Open questions

- **B-DEP:** choose/validate exact maintained compatible compiler/Python/Web3/Foundry/Anvil/crypto references or explicitly document constrained baseline reuse and source/advisory applicability. No arbitrary upgrade is selected.
- **B-FEE:** finite operator per-gas fee and run-cost allowance, including failed transactions, separate from service principal. Existing unit/attempt ceilings alone cannot bound spend at unbounded fee prices.
- Reward eligibility, usefulness/uniqueness, consensus/Sybil security, genuine human demand and sustainable native economics remain research questions. No supply, ticker, issuance schedule, market value, stable asset, consensus or launch selected.
- Strong/confidential fair exchange, physical/subjective verification, offline/satellite assumptions and migration need separate evidence.

### Next task

Recommended technical task: resolve B-DEP/B-FEE in a bounded dependency/fee-policy specification review, update ADR 0002 disposition, then separately authorize isolated implementation if ready. Independently recommend scoped E-01/E-02 model/prior-art refinement without launching a token. Do not implement either automatically.

### Blockers

Experiment 002 readiness is BLOCKED by B-DEP and B-FEE; no Git blocker known. Public signature checks are not contract/E2E evidence. Disclosure/censorship/deadline/key/actor failures can prevent payment or progress. No automatic refund, general fairness, unique work, consensus or economic guarantee. Experiment 001's independent-review/residual conditions remain intact.

### Relevant commits

- `239a235` — foundation; `606a52c` — vision preservation; `e872efb` — reviewed routine commit/push default; `ed13296` — continuity hardening.
- `5701aee` — Experiment 001 specification; `db7da99` / `cb64036` — escrow and official tool-pin correction; `59375be` — separate-agent integration.
- [`f66cda9`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77) — final Experiment 001 adversarial review/112-test milestone; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966).
- [`418d310`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/418d3105ab96729cf01233bbcb0cde3aaee808be) — report publication; [CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39064529125); [publication Discussion](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/3).
- [`d41d2f4`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/d41d2f41c78070f4f89d5ea7e8b3f28353fe998a) — Task 005 proposal; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39114654576), 58 Solidity / 54 Python tests plus end-to-end. Not Experiment 002 execution evidence.
- [`ded3fff`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/ded3fff203145cd8ec50fb3d91cca916a95cb331) — Task 006 vision alignment/review; [regression CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39115815952), 58 Solidity / 54 Python plus end-to-end.
- Task 007 specification/research commit: resolve through `git log -1 -- docs/SESSION_HANDOFF.md`; inspect its Actions run. Any regression result remains Experiment 001 evidence, not Experiment 002 execution.

### Canonical documents

- [MASTER_PLAN.md](../MASTER_PLAN.md), [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [DECISION_REGISTER.md](DECISION_REGISTER.md), [ROADMAP.md](ROADMAP.md), [RESEARCH_JOURNAL.md](RESEARCH_JOURNAL.md).
- [RESEARCH_SPEC.md](RESEARCH_SPEC.md), [PROTOCOL_HYPOTHESES.md](PROTOCOL_HYPOTHESES.md), [FUTURE_NETWORK_ARCHITECTURE.md](FUTURE_NETWORK_ARCHITECTURE.md), [THREAT_MODEL.md](THREAT_MODEL.md).
- [Experiment 001 specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), [18 invariants](SECURITY_INVARIANTS.md), [coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md), [security review](experiments/EXPERIMENT_001_SECURITY_REVIEW.md), [report](../research/reports/EXPERIMENT_001_REPORT.md), [ADR 0001](adr/0001-experiment-001-architecture.md), [dependency pins](../DEPENDENCIES.md).
- [Experiment 002 research comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md), [proposal](experiments/EXPERIMENT_002.md), [architecture](architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat model](experiments/EXPERIMENT_002_THREAT_MODEL.md), [test plan](experiments/EXPERIMENT_002_TEST_PLAN.md), [proposed ADR 0002](adr/0002-experiment-002-fair-exchange.md).
- [Experiment 002 design review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md) and [ADR 0003 research direction](adr/0003-independent-l1-research-direction.md).
- [Experiment 002 final specification](experiments/EXPERIMENT_002_FINAL_SPEC.md), [vectors](experiments/EXPERIMENT_002_SIGNING_VECTORS.md), [dependency assessment](experiments/EXPERIMENT_002_DEPENDENCY_REVIEW.md), [economic foundations](../research/economics/AI_EARNED_NATIVE_TOKENS_AND_UTILITY.md).
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
