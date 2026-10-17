# Tests

The escrow's Foundry unit, fuzz, and stateful tests are under `contracts/test/`; run them from the repository root with `forge test --offline -v` after the pinned compiler setup in [contracts/README.md](../contracts/README.md). No external RPC, paid compute, or real-fund fixture is required.

See [the coverage map](../docs/experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) for named evidence against all 18 requirements and the checks that still require Python/environment integration. Tests do not establish an independent audit, agent interoperability, or production security.

Task 003B adds [Python unit and local integration tests](python/) alongside the existing Solidity suite. See [commands and boundaries](../sdk/python/README.md) and [invariant coverage](../docs/experiments/EXPERIMENT_001_ESCROW_COVERAGE.md). All chain interaction is temporary literal-loopback Anvil with synthetic funds; no public network or production credentials.
