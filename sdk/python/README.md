# Local Experiment 001 agents

This is a bounded research fixture, not a stable Genesis SDK. Two separate OS processes create independent ephemeral EOA signers, discover a signed offer, countersign terms, and exchange public JSON messages through a temporary directory under ignored `internal/`. No Python framework, AI model, hosted service, public RPC, or shared in-memory agent state is used.

## Fresh checkout

Use CPython **3.12.1**, official Foundry **v1.0.0** commit `8692e926198056d0228c1e166b1b6c34a5bed66c`, and the [pinned compiler/dependencies](../../DEPENDENCIES.md). Foundry must be on PATH, or installed at ignored `internal/tools/foundry/`. Supported compiler platforms are macOS x86_64 and Linux x86_64. Installation downloads tools/packages; the experiment itself uses only loopback.

From the repository root:

```sh
scripts/bootstrap-solc.sh
scripts/check-toolchain.sh
scripts/check-dependencies.sh
forge build --offline
python3.12 -m venv internal/agent-venv
internal/agent-venv/bin/python -m pip install --require-hashes -r sdk/python/requirements.lock
internal/agent-venv/bin/python -m pip check
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
scripts/run-experiment-001.sh
```

The runner starts zero-account Anvil on an available literal `127.0.0.1` port, deploys the existing escrow, starts provider and requester, assigns synthetic balances, checks terminal state/accounting, and shuts down all children in a `finally` boundary. It prints public evidence JSON: run/deployment identifiers, process IDs, addresses, transaction and canonical block hashes, gas, verifier time, message count, and elapsed time. Redirect it into `internal/` to retain local evidence. Process errors report safe categories; no key, raw signed transaction, or library exception is logged. Child stdout/stderr and Anvil startup output are suppressed.

Additional bounded fixtures:

```sh
scripts/run-experiment-001.sh --scenario invalid_result
scripts/run-experiment-001.sh --scenario requester_refusal
scripts/run-experiment-001.sh --scenario provider_killed
```

These must end in a requester refund, with no Acceptance file and no provider credit. Only the trusted harness advances chain time to the immutable settlement deadline. Refund and withdrawal remain actual signed contract calls. Each run has a 60-second harness budget and 45-second agent budget; forced shutdown escalates terminate to kill after two seconds. No process persists after the runner exits normally or raises an ordinary exception. SIGKILL/host failure cannot be cleaned up by Python.

## Boundaries and safety

- Each agent generates its own fresh key in memory. The harness sees only public addresses and owns a separate deployment signer. No mnemonic/default Anvil keys, key arguments, environment keys, key files, or `.env` are supported. Inputs and assertions are deterministic; keys/run IDs and therefore hashes vary intentionally, as required by the architecture. This is not isolation against the shared host administrator or privileged Anvil RPC.
- The public config/deployment manifest is trusted harness input. Offers and agent messages are untrusted. All message filenames are fixed by code; an offer cannot select paths, URLs, types, executable code, or domain definitions. Messages are atomic, write-once, UTF-8 JSON, at most 16 KiB; duplicate keys, extra fields, malformed types, and noncanonical decimal integers are rejected. Polling for a fixed file is bounded; messages are submitted once, with zero retransmission retries (below the three-retry ceiling).
- RPC is HTTP literal `127.0.0.1` only. DNS destinations, proxy configuration, redirects, unexpected chain ID, code hash, or run ID are refused. There is no remote endpoint override. A trusted host can still falsify local evidence.
- Transactions are locally signed, sequential per process, limited to eight submissions per signer and at most 16 across the standard run including deployment. Each transaction has a two-million gas limit and a three-gwei maximum fee. Escrow principal has its separate signed cap. These local gas budgets are not a contract-enforced aggregate wallet limit.
- Receipts must succeed, match their canonical block, and contain the expected escrow event/fields; terminal records and accounting are checked separately. A lost send response is reconciled using the locally computed transaction hash for at most four seconds; it does not create a fresh authorization or automatically resend. Unresolved delivery aborts as inconclusive. Public transaction hashes, nonces, amounts, and expected events are journaled under the ignored run directory before broadcast; raw transactions and keys are excluded. Previously observed receipts are rechecked before subsequent actions and final evidence.
- The provider loads inputs from the funded immutable record. The requester recomputes independently and constructs Acceptance only after valid signature, binding, and arithmetic checks. The contract also recomputes. Requester veto remains: correct work without Acceptance cannot settle, and the requester may refund at timeout. No provider-cost compensation or fair-exchange guarantee exists.

See [coverage](../../docs/experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) for tested cases and explicitly pending Task 003C candidates. No EVM experiment validates a future Genesis consensus mechanism or native blockchain. Independent review and broader security gates remain incomplete.
