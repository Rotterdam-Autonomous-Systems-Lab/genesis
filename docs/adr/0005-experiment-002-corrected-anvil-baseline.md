# ADR 0005: Isolated Corrected Anvil for Experiment 002

- **Date:** 2026-10-18.
- **Status:** Accepted for bounded local infrastructure, subject to the publication commit's required Ubuntu compatibility CI passing.
- **Scope:** corrected node selection only; no agent implementation, production permission, authorization/economic redesign or future Genesis architecture commitment.

## Context and evidence

[Task 010](../experiments/EXPERIMENT_002_FEE_INVESTIGATION.md) diagnosed missing fee-cap clamping in Anvil v1.0.0 RPC reporting. Wallet/EVM charges respected the cap, but accepted strict evidence checks correctly blocked. [Task 011 validation](../experiments/EXPERIMENT_002_ANVIL_VALIDATION.md) tests the unchanged negative control and the same matrix/oracle on a checksum/source-pinned corrected node, then runs original Python and signature controls. Acceptance here is infrastructure compatibility, not Experiment 002 experimental acceptance.

## Decision

Use **only Anvil v1.6.0-rc1, commit b272ce3366987406406e9eb1b82596653a3ad628, explicit --hardfork cancun**, installed separately under ignored `internal/tools/experiment002-anvil-v1.6.0-rc1/`. Retain Forge/Cast v1.0.0, Solidity 0.8.28/Cancun/viaIR/optimizer 200, existing OpenZeppelin/forge-std and CPython/hash-locked dependencies. [Manifest](../../research/compatibility/experiment002/anvil-candidate.json) pins source, platform archive and extracted-binary SHA-256. Installer verifies before execution; loader rechecks binary hash/version and rejects unknown platforms/bytes.

Do not replace global tools, PATH or Experiment 001's default node. Existing Experiment 001 source/tests and historical metadata stay unchanged. A clearly scoped research harness redirects only the verified node executable and adds Cancun for compatibility testing; it exports the original required PYTHONPATH for child tests. Report the actual candidate separately from Experiment 001's historical hardcoded Foundry label. Future Experiment 002 integration must explicitly select this verified profile; no broad bypass of original version guards is authorized.

All principal/fee/attempt/reservation/wallet/time limits, signed types, caller/nonce/deadline/refund rules and strict fee reconciliation remain unchanged. Corrected RPC evidence must agree with arithmetic, canonical records, opcode witness and isolated balances. False evidence must still reject.

## Alternatives and rationale

- Keeping the old node leaves required evidence inconsistent; retain it as negative control and Experiment 001 historical baseline.
- The exact upstream receipt correction is 75151e9cae397d34034c1d03defc4f94b6363a3c; that snapshot also has corrected mined-transaction pricing. Its exact nightly artifact was unavailable. A custom source build adds compiler/build/provenance obligations.
- The reviewed v1.5.1 source still contains the receipt defect. v1.6.0-rc1 is the smallest suitable packaged family reviewed, before the larger v1.8.5 candidate. This is not proof of a globally minimal possible revision. Preserve its rc1 label even though GitHub marks the release non-prerelease.
- Receipt normalization, cap increases, hiding clamped cases and relaxed comparisons are rejected.

## Trade-offs, residual risks and reversibility

Official HTTPS archives and recorded upstream digests verify integrity under GitHub/publisher trust. Binary self-reported commit/source SHA/ancestry corroborate identity, but no successful cryptographic attestation or reproducible build is claimed: the attestation API lookup returned 404. New Rust/node dependencies are not a comprehensive advisory-clean/audit claim. macOS uses existing libusb; Linux compatibility is a required CI gate. No host packages or credentials changed.

The node version/feature graph differs from v1.0.0; Cancun is fixed explicitly to avoid silently adopting a later default EVM fork. Existing compiler/library source restrictions and CCIP-disabled Web3 mitigations remain. Trusted host/RPC, public-output leakage, inclusion/deadline/finality, key loss and supply-chain risks persist. This reversible side-by-side local pin selects no future independent Genesis L1 VM, consensus, cryptography or native asset.

## Gate and follow-up

Local decision: PASS for scoped compatibility. Required Ubuntu CI must run original 86 Solidity/54 Python controls, old fee characterization/signatures/arithmetic, nine candidate integrity/fee tests, candidate signatures and unchanged 54 Python controls plus success/refusal. A failing CI, integrity mismatch or new incompatibility retains/reopens BLOCKED; do not weaken tests to accept it. When CI passes, B-ANVIL-FEE-EVIDENCE is resolved for this profile, allowing a subsequent authorized Task 009 continuation. Task 011 itself does not resume agents or confer Experiment 002 PASS.

## Task 012 execution follow-up

Task 011 publication [Ubuntu CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39136054716), closing this infrastructure gate for the pinned profile. Separately authorized [agent integration](../experiments/EXPERIMENT_002_AGENT_ACCEPTANCE.md) now explicitly verifies/uses it and reports conditional experimental acceptance subject to its own CI. All original pin/budget/scope restrictions remain; this is no new dependency or architecture decision.
