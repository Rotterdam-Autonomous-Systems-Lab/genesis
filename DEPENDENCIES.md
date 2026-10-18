# Experiment 001 dependency baseline

Task 003A pins the escrow-only local build below. Installation needs ordinary HTTPS access to source/tool distribution; build and tests then run without public blockchain access, hosting, or credentials. Task 003B adds the hash-locked Python fixture below; no production dependency claim follows.

| Component | Exact reference | Role |
| --- | --- | --- |
| Foundry (Forge and Anvil) | v1.0.0; commit `8692e926198056d0228c1e166b1b6c34a5bed66c` | Local compiler driver, test VM, local node smoke check. |
| Solidity | `0.8.28+commit.7893614a` | Exact pragma; Cancun EVM, optimizer 200 runs, via IR. |
| OpenZeppelin Contracts | v5.2.0; commit `acd4ff74de833399287ed6b31b4debf6b2b35527` | Non-upgradeable EIP712, ECDSA, ReentrancyGuard and required source closure. |
| forge-std | v1.9.6; commit `3b20d60d14b343ee4f908cb8079495c07f5e8981` | Test helpers, assertions, local cheatcodes, stateful test targeting. |
| actions/checkout | v4.2.2; commit `11bd71901bbe5b1630ceea73d27597364c9af683` | Read-only checkout, no persisted Git credentials. |
| foundry-rs/foundry-toolchain | commit `908c540300062bd5a7e473851cdb4282204cee09` | CI install of exact v1.0.0; caching disabled; installed tool commit checked. |

## Compiler integrity

`scripts/bootstrap-solc.sh` downloads the versioned official solc-bin artifact into ignored `internal/tools/solc`, checks SHA-256 before execution, and avoids the global compiler cache. Supported platforms:

- macOS x86_64: `81515b0e53deaa266d549545ccaac0a5a96e6d4e8201c77f673b2c710976d9ea`.
- Linux x86_64: `9a0fb7e0db2c0641dbae1c5cc645dc686820c83af516226abb1c0a2f76636f25`.

These hashes were checked against the official platform manifests for 0.8.28; the local macOS binary was checked before execution. Unsupported platforms fail without silently choosing another compiler. Do not commit binaries or compiler caches.

## Vendored source and review boundary

`lib/` contains only the unmodified transitive source closure needed by the contract and tests, plus upstream license files and provenance records. `dependencies.sha256` records the file hashes; `scripts/check-dependencies.sh` detects accidental source drift. It is not a signed upstream attestation. Fresh checkout does not require a submodule or dependency installation.

Source archives were fetched by immutable commit. OpenZeppelin archive SHA-256 is `7ca6287b8a0d0db67b5923c047365025e612dbaf58a49cbe74d05aa5213e36f9`; forge-std archive SHA-256 is `eb94c3bd026342ae6955ce08f76aad648c586c003acebf5ee5d9b419a417076c`. See each dependency's PROVENANCE.md. Third-party licenses remain theirs; Genesis's project license remains undecided. First-party source is marked UNLICENSED rather than silently selecting a license.

The consumed cryptography and guard code was inspected for the specified EIP-712 domain, 65-byte low-s/v validation, and non-transient reentrancy behavior. Exact pins and tests do not constitute an independent security audit, a comprehensive advisory review, or a guarantee that dependencies are vulnerability-free. Review the pinned release and advisory/audit scope before expanding use. Relevant primary references: [OpenZeppelin cryptography](https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography), [OpenZeppelin utilities](https://docs.openzeppelin.com/contracts/5.x/api/utils), and [EIP-712](https://eips.ethereum.org/EIPS/eip-712).

## Task 003B Python fixture

CPython **3.12.1** is the exact local and CI runtime. Direct dependencies are Web3.py **7.14.0** and eth-account **0.13.7**, with all transitive versions and permitted distribution SHA-256 hashes in [requirements.lock](sdk/python/requirements.lock). Install with `pip --require-hashes`; [requirements.in](sdk/python/requirements.in) records intent. The lock was generated on Python 3.12 with pip-tools **7.5.1**, then installed and tested. Lock regeneration is a reviewed maintenance action, not part of execution. Package hashes verify distribution integrity against the recorded lock, not publisher trust or absence of vulnerabilities.

CI uses actions/setup-python **v5.6.0**, immutable commit `a26af69be951a213d495a4c3e4e4022e16d87065`, verified against the upstream tag. Existing pinned actions and minimal read-only workflow permissions remain. No production credentials or public chain RPC are used. Initial tool/package installation needs HTTPS; runtime communicates only over literal loopback and local files.

Standard APIs: [eth-account typed-data signing](https://eth-account.readthedocs.io/en/v0.13.7/eth_account.html) and [Web3.py transactions](https://web3py.readthedocs.io/en/v7.14.0/transactions.html). Exact pins are not a comprehensive advisory review; independent dependency/security review remains pending. The older pinned Python patch and toolchain should be reviewed before any expansion beyond this disposable local fixture.

## Task 003C advisory and supply-chain review

The [security review](docs/experiments/EXPERIMENT_001_SECURITY_REVIEW.md) records the compiler/Foundry/OpenZeppelin/Actions assessment and an OSV query of all 39 locked PyPI package versions. Web3.py 7.14.0 matches [GHSA-5hr4-253g-cpx2](https://github.com/ethereum/web3.py/security/advisories/GHSA-5hr4-253g-cpx2); the fixture disables its unused CCIP Read feature and tests that no secondary HTTP lookup occurs. This mitigates the selected application's exposure while retaining the affected package pin; it is not a general library fix. No unrelated dependency upgrades were made. Installation now uses hash-locked binary distributions only; publisher trust, old runtime/compiler maintenance, binary provenance and independent review remain explicit limitations.

## Task 011 isolated corrected-node profile for Experiment 002

[ADR 0005](docs/adr/0005-experiment-002-corrected-anvil-baseline.md) explicitly selects **Anvil v1.6.0-rc1 / b272ce3366987406406e9eb1b82596653a3ad628 with --hardfork cancun** for bounded Experiment 002 infrastructure, conditional on publication Ubuntu CI. Only this node changes; original Experiment 001 defaults and the Forge/Cast/compiler/library/Python pins above stay unchanged. No global/PATH replacement or cryptographic/authorization/fee-limit change follows.

[Manifest](research/compatibility/experiment002/anvil-candidate.json) pins immutable source SHA plus official macOS/Linux x86_64 archive and extracted-binary hashes. [Installer](research/compatibility/experiment002/install_anvil_candidate.py) verifies before execution and writes only ignored internal tools; [loader](research/compatibility/experiment002/anvil_candidate.py) rechecks binary identity/version. Unknown platforms/bytes fail closed. Tests explicitly select the verified profile without changing old version guards. See [validation/reproduction](docs/experiments/EXPERIMENT_002_ANVIL_VALIDATION.md), [provenance](research/compatibility/experiment002/task011-provenance.json) and both-node regression evidence.

No successful attestation or reproducible-build claim: attestation lookup returned 404. Integrity depends on pinned hashes/HTTPS/upstream publisher trust. New node/Rust dependency provenance, existing host libraries, rc1 status and unreviewed advisories remain bounded local-only risks, not production endorsement. No Rust/OS package/credential installation or old dependency upgrade occurred. Compiler/source restrictions and CCIP-disable controls remain. Compatibility, integrity or scope changes reopen review.
