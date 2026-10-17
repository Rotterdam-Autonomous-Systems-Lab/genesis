# Experiment 001 escrow

The only implementation is [Experiment001Escrow.sol](src/Experiment001Escrow.sol), a local research escrow matching the [architecture](../docs/architecture/EXPERIMENT_001_ARCHITECTURE.md). No agents, deployment scripts, tokens, or public-chain configuration are provided. Settlement requires both correct on-chain arithmetic and requester-signed Acceptance. A requester can withhold Acceptance after valid work; timeout refunds the requester. This deliberate fairness limitation is preserved.

## Fresh checkout

Prerequisites: Bash, curl, tar, jq, checksum utility, and exact Foundry v1.0.0 (`8692e926198056d0228c1e166b1b6c34a5bed66c`). CI installs that release automatically on Ubuntu 24.04. To install locally without changing global settings, extract the official platform release into ignored `internal/tools/foundry` and add that directory to this shell's PATH; then verify the tool commits. The official x86_64 archives are [Linux](https://github.com/foundry-rs/foundry/releases/download/v1.0.0/foundry_v1.0.0_linux_amd64.tar.gz) and [macOS](https://github.com/foundry-rs/foundry/releases/download/v1.0.0/foundry_v1.0.0_darwin_amd64.tar.gz). Download only from the trusted release source; the commit check verifies version identity, not independent binary attestation.

From the repository root:

```sh
scripts/check-toolchain.sh
scripts/check-dependencies.sh
scripts/bootstrap-solc.sh
forge fmt --check
forge build --offline
forge test --offline -v
scripts/check-anvil.sh
```

The one-time compiler download is checksum pinned. Thereafter build/tests use the local binary and vendored sources without network downloads or RPC access. No VPS or paid service is needed. `foundry.toml` disables FFI/filesystem access and configures no RPC or fork. Forge tests instantiate contracts only inside the in-memory test EVM. The Anvil smoke check starts a loopback node with zero generated accounts, makes an eth_chainId query, and terminates it; it submits no transactions and deploys nothing to Anvil.

Do not use `forge script --broadcast`, public RPC URLs, production wallets, or real funds. No such command is part of CI. The local smoke log, downloaded tools, and any run notes remain under ignored `internal/`; out/cache/broadcast artifacts are ignored.

## Tests and limitations

[Escrow coverage](../docs/experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) maps all 18 requirements to contract evidence or pending integration work. Tests use synthetic in-memory signer fixtures derived by Foundry, not published Anvil keys or production credentials. Avoid verbose execution traces that could display fixture signing inputs. No Python signer/agent, RPC retry harness, fresh-key lifecycle, discovery transport, or end-to-end verification evidence is implemented yet.

The compiler's selfdestruct deprecation warning is intentionally exercised only by a test adversary forcing surplus ETH into escrow. Production escrow contains no selfdestruct. Receiver tests install callback behavior at credited addresses through local test cheatcodes; unsupported smart-wallet signing is not enabled.

No independent audit or production security claim is made. Ethereum tooling remains an experiment choice; Genesis's future network architecture is unresolved. See [dependency pins](../DEPENDENCIES.md).
