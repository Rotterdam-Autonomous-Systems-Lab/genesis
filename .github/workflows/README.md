# GitHub workflows

[foundry.yml](foundry.yml) checks pinned tool/dependency integrity, Solidity formatting, offline compilation, unit/fuzz/stateful tests, and a loopback Anvil smoke query on Ubuntu 24.04. It installs pinned Python with hash-locked binary-only dependencies, runs Python unit/adversarial/live-Anvil/process integration tests, and executes the end-to-end experiment against temporary loopback Anvil with synthetic funds.

Permissions are `contents: read` only; all three third-party actions use full commit SHAs, checkout credentials are not persisted, and Foundry caching is disabled. Triggers are `push` to main and `pull_request`, with no privileged PR-target or downstream workflow trigger. There are no secret inputs, production wallets, public-chain endpoints, or real-fund deployments. No artifacts are uploaded. Experiment output contains only public identifiers, receipts, and bounded metrics; private keys and raw signed transactions are excluded.

Setup downloads tools/packages over HTTPS and trusts the upstream distributions/actions. A commit/version check is not a cryptographic attestation of the executed Foundry binaries; Python hashes do not certify publisher trust. Hosted runners still have network access, and an untrusted PR can execute arbitrary modified code within that runner. Application loopback guards do not provide an OS egress sandbox. Repository permissions remain read-only and cannot approve PR reviews; organization policy and required checks were not changed by this review.

See [security review](../../docs/experiments/EXPERIMENT_001_SECURITY_REVIEW.md) for observed advisory findings, mitigations, and acceptance limits. Passing CI is experimental evidence, not an independent audit or production approval.
