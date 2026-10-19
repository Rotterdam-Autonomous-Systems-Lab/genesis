# Session Handoff

Use this document to carry concise project context between Codex sessions and contributors. Update the current handoff after significant work; preserve prior handoffs in Git history where useful. Do not put secrets, credentials, or local-only notes here.

## Current handoff — Task 020 source freeze, measured outcome pending

[Task020 report](architecture/NATIVE_L1_TASK020_RESULTS.md), [spending policy](architecture/NATIVE_L1_SPENDING_POLICY.md) and [measurement contract](architecture/NATIVE_L1_MEASUREMENT_CLOSURE.md) define revised bounded models. Original S09 timeout reproduced before change; original2,242,702 proxy bytes imply219seconds at10KiB/s. Full-width compact references and removal of an unused delegate-balance dependency allow a single local development S09 to finish in172.1seconds without raising caps. Thirteen security/control tests pass. Checkpointdc589ba batches were cancelled after finding undercharged build requests; the172.1second development pass is superseded, not resource acceptance. Corrected build requests charge actual required preimages; both scored environments restart under unchanged caps. No final G1 pass/architecture decision yet. MASTER_PLAN, prior experiments, frozen corpus and signed stress inputs unchanged. Final evidence must retain failures and exact source identities. Earlier handoffs below are historical.

## Previous handoff — Task 019 completed comparison, G1 HOLD

[Results](architecture/NATIVE_L1_COMPARISON_RESULTS.md): **CONTINUE COMPARISON — G1 HOLD**, no candidate eliminated/prioritized. Source checkpoint `6872f4b2a208f70074b67bbd47e9095043e0dc18` is pushed. Both clean local and independent Ubuntu environments completed 273 planned slots; accounts/objects pass90 measured runs each, UTXO passes87 with three S09 watchdog HOLDs per environment. All21 core cases pass;89 complete configurations reproduce deterministically. [Permanent raw evidence/checks](../research/reports/task019/README.md) retain failures and compressed traces. Seven model tests and twelve supplemental local controls pass. Legacy CI passes; model CI intentionally fails on resource HOLD. Final publication regression CI must be checked at the evidence commit.

Recipient-output coalescing consumes a recipient output without its signature; owner/value remain intact, but an independently validated top-up covenant is missing. Resource instrumentation/control gaps prevent full G1 acceptance; no frozen semantics or measured model was changed to conceal them. Next Task020: review spending-policy and metering remediation, then bounded rerun under unchanged logical requirements/caps. Native finality/recovery proofs and permissionless bootstrap remain open. MASTER_PLAN and Experiments001/002 preserved. Earlier handoffs below are historical.

## Current handoff — 2026-10-19 (Task 018)

**READY FOR COMPARATIVE MODELS**, research/fixtures only. Baseline `23be098502f7fa0920e02930d3130fa78926289d`; locate publication with Git history for this file. [Adversarial review](architecture/NATIVE_L1_SPEC_REVIEW.md) records six resolved specification findings; [adapter](architecture/NATIVE_L1_ADAPTER.md), [measurement plan](architecture/NATIVE_L1_MEASUREMENTS.md) and [v1 corpus](../research/fixtures/native_l1/README.md) freeze 21 core vectors/32 signed intents plus nine deterministic stress configurations. Nine fixture-integrity tests pass and are added to CI. No candidate model execution or winner. MASTER_PLAN and Experiments 001/002 preserved.

Recommended next task: Task 019 three distinct bounded models and independent harness, pinned wrappers/dependencies/instrumentation and second-environment reproduction under unchanged budgets. No blocker to this bounded implementation scope. Production finality/non-execution proofs, permissionless security/bootstrap, replay retention, recovery and physical-service truth remain open; fixture oracle solves none of them. Earlier handoff retained below as history.

## Current handoff — 2026-10-19 (Task 017)

Research/specification only. Five canonical documents: [workloads](architecture/NATIVE_L1_WORKLOADS.md), [authority/settlement/recovery](architecture/NATIVE_L1_AUTHORITY_SETTLEMENT_RECOVERY.md), [consensus assumptions](architecture/NATIVE_L1_CONSENSUS_ASSUMPTIONS.md), [budgets](architecture/NATIVE_L1_RESOURCE_BUDGETS.md), [next experiment](architecture/NATIVE_L1_NEXT_EXPERIMENT.md). Eight workloads share I1–I8, deterministic logical intent/operation schemas, cumulative principal/fee reserve semantics, expiry/revoke ordering and journal/evidence recovery; each maps account/object/eUTXO obligations without free external infrastructure.

No candidate eliminated; final native architecture unsupported. Budget numbers are proposed finite laboratory controls, not performance results. Native scarce-resource bootstrap and authenticated finality/recovery remain the most consequential unresolved dependency; toy ordering/proof oracle cannot close it. Physical services, discovery, true demand, secure offline transfer and useful-AI-work consensus are unverified. MASTER_PLAN, Experiments 001/002, implementation, caps, dependencies and workflow unchanged.

Next recommendation: independent adversarial schema/vector/adapter and corpus freeze (G0), then separately authorized Task 018 bounded shared-budget/crash-recovery models (G1). No nodes/consensus/wallet/token implementation in Task 017. Proposed accountability roles are listed in the next-experiment document; no appointments or independent review are claimed. Baseline `5ebb298138bc222822af07def0e77b9112bd77bc`; Task 017 commit introduces these specifications. Documentation checks passed for 11 changed Markdown documents and 162 local links, structure, workload/invariant/budget coverage and protected-file preservation. Required push CI is the remaining publication gate; inspect the Task 017 commit’s run.

## Previous handoff — 2026-10-18 (Task 016)

Research/documentation only. [Native L1 report](architecture/NATIVE_L1_RESEARCH.md), [decision matrix](architecture/NATIVE_L1_DECISION_MATRIX.md), [open risks](architecture/NATIVE_L1_RISKS.md) and [next gate](architecture/NATIVE_L1_DECISION_GATE.md) separate experimental evidence from architecture hypotheses. Candidates: account/module-or-VM + stake-BFT; owned/shared objects/resource VM + stake-BFT; extended UTXO/restricted validation + PoW contrast. Pairings are research configurations, not selected stacks; state and consensus comparisons must control different variables.

Completed: charter/ADRs/experiment evidence and primary technical source review; N-01–N-08 requirements, A-01–A-10 risk register, expensive commitments, machine-participation/economic boundaries and falsifiable gate. No native chain, asset, monetary policy, discovery, final architecture or new consensus result. MASTER_PLAN, prior experiments, implementation, caps and dependencies preserved. Source review is focused, not exhaustive; benchmarks/audits not reproduced.

Next recommended Task 017: comparative authority, settlement and durable-recovery specification plus independent consensus/admission threat model (G0); only a later separately authorized task may build disposable models (G1). Blockers to final selection: no native workload/device budgets, comparative semantics/resource results, dynamic-participation/security economics, authenticated offline/light-client recovery or demand evidence. No implementation is authorized by the report.

Baseline `ce657ccf244f9b94168518934aae4f61b361fcff`; Task 016 commit is the commit introducing these reports. Documentation checks passed: eight changed Markdown files, 145 local link targets, table/fence/newline structure, whitespace and protected-file preservation. Required push-triggered CI remains the publication gate; inspect this commit’s run. Preserve Task 015 bounded closure and historical failed inclusion-timing uncertainty.

## Previous handoff — 2026-10-18 (Task 015 completed)

[Final review](experiments/EXPERIMENT_002_FINAL_REVIEW.md): **BOUNDED CONDITIONAL PASS — READY TO CLOSE** for the unchanged synthetic local Experiment 002. Earlier environment-blocked verdict/evidence is preserved in the review and below. No unconditional PASS, general fairness, native-network, token, consensus or autonomous-discovery result.

Permissions recovered: local TCP bind/connect and GitHub HTTPS verified. Exact tools/candidate identity, checksums and pip consistency pass. Local validation: 86 Solidity, 73 Experiment 002 Python, 54 unchanged Experiment 001 Python on each node, 14 original fee controls, nine candidate tests, 25 digests/34 signatures per node and 20 fee-model cases. Standalone Experiment 002 settles result 18; controlled late funding gives two seconds slack, rejects late claim and refunds/withdraws. Both controlled repetitions pass; Experiment 001 success/refusal remains intact. All four R013 fixes verified within declared trusted/cooperative fixture boundaries.

Preserved original review commit `f1dab65e141bb6fa0385a96a7a344bbe8b9721d8`, pushed ordinary fast-forward to origin/main. [Its complete Ubuntu CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39168554999); [Task 014 CI](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39142706331) independently verified green. Completion documentation is a subsequent ordinary commit; retain required publication CI and reopen if it fails.

Historical failed CI log fetched: confirms funding rejection, but failed receipt timestamp/root cause remains unrecovered. Residual trusted host/RPC/supply chain, explicit inclusion control, public disclosure, late/censored/absent actors, key loss, rollback, in-memory recovery and cooperative resource limits remain. MASTER_PLAN, contracts, agents, caps, Experiment 001 and CI workflow unchanged.

Next recommended dependency: separately scoped specification/research on useful/unique contribution evidence or delivery/inclusion assumptions; no automatic implementation expansion. Completion commit is the commit adding this disposition. Local logs are ignored under `internal/task015-completion/`.

## Previous handoff — 2026-10-18 (Task 015 environment-blocked)

[Final review](experiments/EXPERIMENT_002_FINAL_REVIEW.md): **NOT READY TO CLOSE** because fresh live remediation/compatibility checks and publication CI could not be verified in this restricted session. No new material contract defect confirmed; source and isolated tests support the corrections and the bounded no-second-authorization claim.

Completed: exact pinned Foundry format/build/86 Solidity tests; 15 existing socket-free tests; three candidate integrity tests; three new independent probes including 24 receipt mutations and deadline/latch interactions. Dependency checksums and candidate loader identity pass. MASTER_PLAN, implementation, limits and historical archives preserved.

Blockers: loopback socket bind is prohibited, so full Python suites and standalone exchange cannot validate integrations. GitHub DNS/API unavailable; CI status unknown. Global Foundry initially differed; rerun used existing exact pinned binaries. See report for every failed/inconclusive attempt.

Next dependency: finish live suites/unchanged CI on exact tools and Anvil/Cancun, publish review, inspect commit-specific CI, then explicitly reconsider bounded conditional closure. Do not infer unconditional PASS or implement another experiment/token/consensus/discovery feature. Historical failed CI timestamp/root cause remains unrecovered. Baseline and local tracking ref: `f5efc4b4a1a73ec651e7f1cbde4c4720d1c558e5`; Task 015 commit is the commit introducing this review.

## Previous handoff — 2026-10-18 (Task 014)

### Current status

Experiment 002 [remediation](experiments/EXPERIMENT_002_REMEDIATION.md) implemented; **pending required publication CI and independent re-review**, not final PASS/closure. Preserve Task 012 conditional result, Task 013 findings and failed CI history. Genesis vision, MASTER_PLAN, contracts, schemas, fee/principal/wallet/time budgets, exact Anvil/Cancun profile and Experiment 001 are unchanged.

### Completed work

- R013-01: reconstruct each owner/state/result/entitlement from attributed signed included transactions; repeated pinned final snapshot must match model.
- R013-02: cross-check current/block receipts, transaction identity and own signing intent; contradictory/stale observations latch further signing. Known terminal events constrain record views.
- R013-03: shared 120-second cooperative monotonic deadline at ready barriers/RPC/typed signing/transaction phases/audits; unknown post-broadcast outcomes remain latched. Cleanup cap remains 15 seconds.
- R013-04: old auto-clock +1.1-second delay reproduces expiry with gas-only loss; queue then explicitly mine the late test at existing fundBefore-1. Separate expired-funding control retained; safe failure diagnostics survive into error output. Historical CI timestamp is irrecoverable, not invented.
- Seven converted review scenarios plus eleven new tests; local results: 86 Solidity /54 original Python /70 Experiment 002 Python. See [timing evidence](../research/experiments/experiment002/task014-timing-evidence.json) and exact reproduction/limitations in remediation record. No new dependencies/workflow permissions.

### Open questions

Independent review of reconstruction/snapshot assumptions, sticky evidence handling and cooperative deadline enforcement. Consistently dishonest RPC/host, finality/rollback, public disclosure, censorship/deadlines, absent callers/key loss and supply chain remain risks. No general fairness, work-uniqueness or native-network result.

### Next task

Recommend independent re-review of the remediation and published CI before explicit acceptance disposition. No automatic new experiment, token/L1/consensus or public infrastructure work.

### Blockers

No known local unresolved implementation finding within the stated cooperative/trusted fixture; final regressions and publication CI must pass. Closure still requires re-review. Original failed CI's exact timing remains unverified; current clock fix is supported by new reproducible evidence, not recovered historical data.

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
