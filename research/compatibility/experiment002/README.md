# Experiment 002 compatibility checks

Task 008 compatibility tooling only: no Experiment 002 escrow/agents, native token or new research-experiment implementation. The vector check reads public fixtures, runs ABI/Keccak with pinned Cast, and calls only Anvil's existing ecrecover precompile. It creates no signing keys, sends no transactions, deploys no contracts and kills/reaps its loopback zero-account node. The fee check evaluates integer specification bounds; it does not implement or test an agent budget manager.

From the repository root, use the exact installed baseline in [DEPENDENCIES.md](../../../DEPENDENCIES.md). For fresh installation follow the existing [contract](../../../contracts/README.md) and [Python](../../../sdk/python/README.md) setup; no latest-version substitution. Build **before** Python integration tests, because a forced rebuild removes their required artifact.

```sh
set -e
PATH="$PWD/internal/tools/foundry:$PATH" scripts/check-toolchain.sh
scripts/check-dependencies.sh
internal/agent-venv/bin/python -m pip check
PATH="$PWD/internal/tools/foundry:$PATH" internal/tools/foundry/forge fmt --check
PATH="$PWD/internal/tools/foundry:$PATH" internal/tools/foundry/forge build --offline --force
PATH="$PWD/internal/tools/foundry:$PATH" internal/tools/foundry/forge test --offline -v
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
internal/agent-venv/bin/python research/compatibility/experiment002/check_vectors.py
internal/agent-venv/bin/python research/compatibility/experiment002/check_fee_bounds.py
scripts/run-experiment-001.sh --scenario success
scripts/run-experiment-001.sh --scenario requester_refusal
```

The final two commands deploy only the unchanged **Experiment 001** control onto temporary local Anvil with synthetic funds, then stop children. They are not Experiment 002 execution or organic economic activity. Build and tests need no public blockchain. Initial installation is a distinct HTTPS-dependent phase.

Task 008 local evidence: 58 Solidity tests, 54 Python tests, 25 Cast digests/34 EVM-plus-Python recoveries, 20 fee-formula cases and both end-to-end control paths passed. The first premature Python run failed on the temporarily absent artifact; the sequential rerun passed. See the [blocker resolution](../../../docs/experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md) and [bounded costs](../../../docs/experiments/EXPERIMENT_002_BOUNDED_COST_MODEL.md) for assumptions and residual risk. Current GitHub CI continues to test Experiment 001; it does not automatically run these new research checks.

## Task 009 blocking fee-evidence diagnostic

The [partial implementation review](../../../docs/experiments/EXPERIMENT_002_IMPLEMENTATION_REVIEW.md) records an isolated contract but **FAIL / BLOCKED** acceptance. After building, run:

```sh
internal/agent-venv/bin/python research/compatibility/experiment002/check_anvil_fee_receipt.py
```

This new diagnostic differs from the Task 008 stateless probes: it creates fresh in-memory development keys, prefunds only synthetic initial allowances, deploys the isolated Experiment 002 contract and sends one zero-value revocation on temporary loopback Anvil. It sets a controlled base fee and compares receipt fee with the actual wallet debit. No keys/raw signed transactions are printed or persisted; child cleanup is mandatory. **Exit 2 records the known contradiction and blocks acceptance.** See [observed numeric evidence](task009-fee-receipt-evidence.json). It is not silently added as a passing test or used to overwrite Experiment 001 results. Existing CI runs the discovered contract tests and original agent controls; full Experiment 002 CI remains blocked.
