# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — 2026-10-17

### Current status

Genesis is in early-stage experimental research. The current milestone is project foundation and prior-art mapping. A small, bounded two-agent independently verifiable economic transaction is the first implementation milestone, but remains an early step toward the broader permissionless economic network ambition. Task 003A implements and locally tests the Solidity escrow component with pinned dependencies and GitHub CI. Task 003B now implements separate Python requester/provider processes and a temporary Anvil end-to-end fixture; the original contract and requester-veto semantics are unchanged. Local Solidity and Python evidence is recorded in the coverage map. Independent review and explicitly pending fault/security cases remain open.

### Completed work

- Initial repository foundation was recorded in commit [`239a235`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/239a23574c012af9cd782b5bb17cb05b46e3665d).
- The long-term vision, research plan, decision boundaries, architecture research territory, and recovered history were documented in commit [`606a52c`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/606a52c8bc2a6c48961f164af4da718ecc06b163).
- Routine work now defaults to a reviewed commit and push to `origin/main`, as recorded in commit [`e872efb`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/e872efb93a0b8acb86db721fe293848eaa45a0cc).
- Continuity hardening was committed as `ed13296`; the journal and reusable handoff preserve repository history.
- Task 002B adds the Experiment 001 specification, architecture, 18 testable security invariants, proposed ADR 0001, expanded threat model, and implementation/security-review gates. Critical behavior is specified; requester veto and provider-fairness limitations are explicit. No implementation findings are claimed.

- Task 003A: escrow component, 55 passing local tests (including fuzz/stateful properties), dependency pins, offline build and read-only pinned-action CI. See the coverage map for partial/integration invariants; no independent audit or end-to-end finding is claimed.

- Organic discoverability: clarified the README introduction and researcher navigation; updated the GitHub description and eight research topics; enabled Discussions. Published a [welcome thread](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/1) and an [unresolved requester-veto fairness thread](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/discussions/2). No implementation, architectural decision, or research status changed. The documentation commit is recoverable from this file's Git history.

- Task 003B: independent ephemeral process-owned signers, signed file discovery/agreement/result/Acceptance transport, actual local escrow transactions, and bounded runner cleanup. All 55 Solidity tests and 30 Python tests passed locally; a standalone run settled and withdrew exact synthetic principal. Hash-locked Python dependencies and pinned-action CI now cover integration. See [agent reproduction](../sdk/python/README.md) and [coverage/pending cases](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md). The implementation commit is recoverable from this file's history; remote CI evidence belongs to that commit's Actions run.

### Open questions

- Whether an independent permissionless Layer 1 is justified compared with existing networks or another architecture.
- Whether a native asset is necessary and, if so, what function it serves.
- Which consensus or non-consensus security architecture is appropriate.
- Whether useful contributions can be measured and whether they belong in consensus, incentives, or service markets.
- How authority, discovery, execution, governance, upgrades, and offline coordination should work.

### Next task

Recommended next task: founder/security review of Task 003B evidence, requester-veto limitations, dependencies, and the explicit pending Task 003C candidate matrix. Any further implementation, fault-proxy expansion, or settlement redesign needs a separate task authorization. No Task 003C work has begun.

### Blockers

No blocking specification contradiction was found. Contract test evidence is local and scoped. Independent audit/advisory review, the broader fault matrix, and review of full experiment acceptance remain pending; local integration tests do not complete those gates.

### Relevant commits

- `239a235` — initial repository foundation.
- `606a52c` — vision and research-plan preservation.
- `e872efb` — routine `origin/main` push default.
- `ed13296` — journal and handoff continuity hardening.
- `5701aee` — Experiment 001 specification and invariants.
- `db7da99` — initial escrow implementation. Its first CI run rejected the mismatched preinstalled stable-build pin before tests.
- `cb64036` — Task 003A follow-up pins official Foundry v1.0.0 commit `8692e926…`; its [CI run passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39054332964).

### Canonical documents

- [`MASTER_PLAN.md`](../MASTER_PLAN.md) — canonical project charter.
- [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — concise onboarding and context recovery.
- [`DECISION_REGISTER.md`](DECISION_REGISTER.md) — established decisions and unresolved choices.
- [`ROADMAP.md`](ROADMAP.md) — conditional research stages.
- [`RESEARCH_SPEC.md`](RESEARCH_SPEC.md) and [`PROTOCOL_HYPOTHESES.md`](PROTOCOL_HYPOTHESES.md) — research methods and hypotheses.
- [`FUTURE_NETWORK_ARCHITECTURE.md`](FUTURE_NETWORK_ARCHITECTURE.md) — future architecture research territory.
- [`THREAT_MODEL.md`](THREAT_MODEL.md) — general threats and Experiment 001 severity/coverage.
- [`experiments/EXPERIMENT_001.md`](experiments/EXPERIMENT_001.md) — proposed experiment and evaluation.
- [`architecture/EXPERIMENT_001_ARCHITECTURE.md`](architecture/EXPERIMENT_001_ARCHITECTURE.md) — exact schemas, authority, state and failure behavior.
- [`SECURITY_INVARIANTS.md`](SECURITY_INVARIANTS.md) — 18 proposed invariants and required tests.
- [`adr/0001-experiment-001-architecture.md`](adr/0001-experiment-001-architecture.md) — accepted for local escrow only; not final network architecture.
- [`research/history/ORIGINAL_BRAINSTORM.md`](../research/history/ORIGINAL_BRAINSTORM.md) — reconstructed historical ideas, not an approved architecture or verbatim transcript.
- [`research/history/CONTEXT_RECOVERY.md`](../research/history/CONTEXT_RECOVERY.md) — instructions for reconstructing context.

- [EXPERIMENT_001_ESCROW_COVERAGE.md](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) — local results, invariant mapping and pending integration.
- [DEPENDENCIES.md](../DEPENDENCIES.md) and [contracts/README.md](../contracts/README.md) — exact pins and fresh-checkout commands.

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
