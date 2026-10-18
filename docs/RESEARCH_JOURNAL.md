# Research Journal

This journal records repository milestones supported by version-controlled artifacts. Historical entries use verified Git commit dates and contents. New entries describe the documentation in their own commit; locate that commit with Git history for this file. A specification milestone is not an experimental finding.

## 2026-10-17 — Repository foundation

Commit [`239a235`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/239a23574c012af9cd782b5bb17cb05b46e3665d) (`Initialize Genesis research repository`) established the initial repository foundation. The commit created 22 files, including the README, master plan, agent and contributor guidance, security and license proposal documents, initial research and threat-model documents, and reserved directories for future work. It did not implement a protocol, smart contracts, a blockchain node, or an agent system.

## 2026-10-17 — Vision and research-plan preservation

Commit [`606a52c`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/606a52c8bc2a6c48961f164af4da718ecc06b163) (`Preserve Genesis vision and research plan`) expanded the canonical project charter and README, added the future network architecture research territory, project context and decision register, expanded research specifications, hypotheses and roadmap, and created public history records for the recovered brainstorm, naming, and context recovery. The repository history records 14 files changed in this commit. `research/history/ORIGINAL_BRAINSTORM.md` identifies itself as a reconstruction from the supplied project brief and repository documents, not a verbatim transcript.

## 2026-10-17 — Experiment 001 architecture and security specification (Task 002B)

Added the proposed [Experiment 001 specification](experiments/EXPERIMENT_001.md), [architecture](architecture/EXPERIMENT_001_ARCHITECTURE.md), [18 security invariants](SECURITY_INVARIANTS.md), and [ADR 0001](adr/0001-experiment-001-architecture.md); expanded the threat model and roadmap security gate. The design uses two separate local signers, bounded synthetic escrow, typed messages, independent requester verification, on-chain arithmetic checking, requester-signed Acceptance, and deterministic timeout refunds. The provider-fairness limitation is explicit: a requester may withhold Acceptance after correct work.

This is documentation only: no contracts, agent code, dependency installations, deployments, tests of an implementation, or experimental results are recorded. The ADR is Proposed. Next proposed task: review the specification and security gate, select exact dependency pins, and then separately authorize a small implementation task. Genesis's independent-network ambition, three research tracks, and unresolved native-asset/consensus questions are preserved.

## 2026-10-17 — Escrow-only implementation and CI (Task 003A)

Implemented the minimal local escrow and EIP-712 authorization/state rules, retaining requester veto and deterministic timeout refunds. Recorded exact Foundry/Solidity references, vendored immutable OpenZeppelin/forge-std source with licenses and checksums, added read-only pinned-action GitHub CI, and documented [invariant coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md).

Local evidence: 55 tests passed (36 unit, 15 fuzz, four stateful invariants); each stateful property ran 128 x 64 calls with zero unexpected reverts. Formatting, offline build, workflow actionlint, shell syntax, and loopback zero-account Anvil smoke checks passed. One initial fixture-only failure was corrected without changing contract checks; the coverage report preserves it. No Python agents, production credentials, public blockchain access, or real-fund transactions were involved. Independent security audit and remaining integration checks are not complete. The pushed commit's Actions result is available through GitHub; this journal does not predeclare remote CI success.

CI follow-up: the first run for `db7da99` correctly rejected the tool pin before compilation because the local preinstalled `1.0.0-stable` commit was not the official `v1.0.0` tag commit. Pins were corrected to official `8692e926198056d0228c1e166b1b6c34a5bed66c`; strict version verification and all security tests were retained and rerun with that exact release. This configuration correction does not change settlement semantics.

Next proposed task: review escrow code and residual risks, then separately authorize bounded Python signer/verifier and local transport integration for the remaining invariant coverage. The broader Genesis network ambition is unchanged.

## 2026-10-17 — Independent-agent local integration (Task 003B)

Implemented separate Python requester/provider OS processes with independently generated ephemeral keys and signed, bounded public JSON file transport. Added exact EIP-712 interoperability checks for all five schemas, independent requester arithmetic verification, local signed funding/settlement/refund/withdrawal, receipt/event/canonical-state checks, finite budgets, and cleanup. The Solidity contract and all existing contract tests are unchanged; requester veto is explicitly preserved.

Local evidence: 55 Solidity tests and 30 Python unit/live-Anvil/process integration tests passed, including two clean success runs, maximum operands, invalid-result rejection without Acceptance, requester refusal, provider termination, cap/binding/replay/expiry rejection, exact refunds, client-boundary RPC failure/lost-response reconciliation, and reorg detection. A standalone local run settled result 18 and withdrew 10^12 synthetic wei; all children stopped. The coverage report preserves an initial bytes32 representation mismatch and explicitly pending broader fault/security cases. No fair-exchange, provider effort, production readiness, native blockchain, or Genesis consensus finding is claimed.

Pinned CPython/Web3.py/eth-account and transitive hashes; extended the read-only pinned-action workflow to install locked dependencies, run the existing Solidity suite, Python tests, and an end-to-end temporary-Anvil experiment. The pushed commit's Actions run is the source for remote CI status; this entry does not predeclare CI success. Recommended next task: review evidence and residual risks, then separately authorize any Task 003C work.

## 2026-10-17 — Adversarial validation and security review (Task 003C)

Reviewed the complete Experiment 001 lifecycle against all 18 invariants and added [security findings and conditional acceptance](experiments/EXPERIMENT_001_SECURITY_REVIEW.md). Fixed nonregular-file blocking, publication overwrite races, incomplete requester-side payment evidence, unresolved-client reuse, swallowed chain-uncertainty classification, and interrupted-startup cleanup. Disabled unused CCIP Read after an upstream advisory match for the pinned Web3.py version. No Solidity protocol logic, signature schema, deadline, spending cap, or requester-veto semantics changed.

Expanded local evidence: 58 Solidity and 54 Python tests pass, retaining all earlier tests and unchanged fuzz/stateful budgets. Tests include real loopback RPC faults, all-type signature mutations, process crashes, malformed evidence, exact timing, concurrent accounting, snapshot/revert before Acceptance, and resource cleanup. Initial new transport regressions failed on the baseline and passed after fixes. The review preserves fault coverage and supply-chain limits rather than claiming independent audit or formal assurance.

The gate is CONDITIONAL PASS for the bounded local research fixture; requester-veto fairness, independent source/compiler/dependency review, and broader lifecycle/network/host-failure testing remain open. No Experiment 002 or final research report begins. Remote CI evidence is the Actions run attached to this entry's commit, not predeclared by the journal. Recommended next task: founder/security review of the conditions and explicit follow-up authorization.

## 2026-10-17 — Experiment 001 research publication (Task 004)

Published the [Experiment 001 report](../research/reports/EXPERIMENT_001_REPORT.md), covering question/hypothesis, architecture/trust assumptions, cryptographic authority, methods, reproduction, results, adversarial findings, all 18 invariants, threats to validity and open questions. The evidence anchor is [`f66cda9`](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/f66cda91af5cb2f2da266fe11d90bc67c05cfc77) and [successful CI run 39057757966](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39057757966): 58 Solidity plus 54 Python tests, 112 total, and actual temporary-Anvil settlement/withdrawal with separate agent processes. Publication verification repeated the local setup/test/runner commands successfully.

Experiment 001 is conditionally accepted and publicly documented, not production-ready, formally proven, independently audited, or evidence of new consensus/native blockchain/native asset feasibility. Requester-veto fairness and the existing acceptance conditions remain open. The publication discussion is created only after the report is verified on origin/main; its URL is recorded in the Task 004 completion report and the thread is discoverable by title “Experiment 001: Reproducible autonomous service exchange — results and limitations”. No implementation or architecture changed. Next proposed step: select the Experiment 002 research question through a separate design review; no Experiment 002 implementation is authorized here.

## 2026-10-18 — Experiment 002 fair-exchange research proposal (Task 005)

Compared six established mechanism families using primary research, specifications and selected open-source references: direct deterministic verification, optimistic challenge games, committed encrypted delivery/FairSwap, optimistic third-party resolution, channels/HTLCs and proof-verified computation. The [research comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md) records citation/inspection limits and distinguishes deterministic digital services from subjective AI and physical tasks.

Proposed a separate [Experiment 002](experiments/EXPERIMENT_002.md), [architecture](architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat model](experiments/EXPERIMENT_002_THREAT_MODEL.md), [test plan](experiments/EXPERIMENT_002_TEST_PLAN.md) and **Proposed** [ADR 0002](adr/0002-experiment-002-fair-exchange.md). The bounded hypothesis is provider collectability for a timely canonical correct claim under upfront signed predicate consent, without a second requester approval. Public-result leakage followed by non-inclusion/expiry is an explicit counterexample to strong fair exchange, not hidden by the hypothesis.

This is documentation only: no Experiment 002 implementation, benchmark, executed test or security result exists. Experiment 001's published CONDITIONAL PASS, 112-test milestone and requester-veto semantics remain unchanged. Existing regression CI, if successful for this documentation commit, is evidence about Experiment 001 only. Resolve the task commit and CI through Git history/Actions rather than predeclaring success here. Next proposed task: founder/design review of the consent change, assumptions and test plan, then a separately authorized bounded implementation. No final Genesis chain, consensus, native asset or production architecture is chosen.

## 2026-10-18 — Vision alignment and Experiment 002 design review (Task 006)

The founder's Task 006 instruction explicitly clarifies an independent permissionless L1/native human-and-machine economy as the long-term research goal, including AI mining/earning through independently verifiable contributions and genuine human utility. [ADR 0003](adr/0003-independent-l1-research-direction.md) records research-scope acceptance only; no chain, asset, consensus, issuance parameters or economic outcome is approved. Updated canonical vision/charter, architecture territory and research documents; organized all roadmap stages around Verifiable Autonomous Work, Independent Network Security and Human and Machine Economy, retaining the original technical tracks and historical reconstruction.

The [Experiment 002 review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md) concludes **amend and remain Proposed**, not implementation-ready. H2-C now distinguishes exclusive outcomes/refund availability from automatic closure, and provider progress is reported independently of timely-inclusion safety. T18–T20 add late-funding, absent-caller and repeated-work controls without removing T01–T17. Upfront consent remains a candidate for veto isolation, not proof of general fairness, unique useful contributions, Sybil resistance, consensus or native demand.

Documentation/design review only: no Experiment 002 code, deployment or executed evidence. Experiment 001's publication, 112-test milestone, implementation and control semantics remain unchanged. Next recommended task: close review gates R1–R3 in specification finalization, explicitly decide on ADR 0002, then separately authorize bounded implementation if accepted. This entry's commit and regression CI are recoverable from Git history/Actions; regression CI is not Experiment 002 evidence.

## Source boundary

This journal does not infer events beyond the repository record. See [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) for current working context and the reusable handoff format.
