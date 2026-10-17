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

## Source boundary

This journal does not infer events beyond the repository record. See [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) for current working context and the reusable handoff format.
