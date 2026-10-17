# Experiment 001 dependency baseline

Task 003A pins the escrow-only local build below. Installation needs ordinary HTTPS access to source/tool distribution; build and tests then run without public blockchain access, hosting, or credentials. No Python packages are introduced.

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
