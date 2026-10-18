# Experiment 002 local agents

A disposable, synthetic, two-process experiment in upfront authorization to a fixed public arithmetic predicate. This is not a stable SDK, general fair exchange, native Genesis asset or final network architecture. Read the [final specification](../../../docs/experiments/EXPERIMENT_002_FINAL_SPEC.md) and [integration assessment](../../../docs/experiments/EXPERIMENT_002_AGENT_ACCEPTANCE.md).

## Reproduce

From the repository root, first follow the existing [dependency setup](../../../DEPENDENCIES.md) and [Python hash-locked setup](../README.md). Retain Forge/Cast v1.0.0, Solidity 0.8.28, Cancun/viaIR/optimizer 200 and existing library/Python pins. Install the separately verified node; never replace Experiment 001's default Anvil:

```sh
forge build --offline
internal/agent-venv/bin/python research/compatibility/experiment002/install_anvil_candidate.py
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/experiment002 -v
scripts/run-experiment-002.sh
scripts/run-experiment-002.sh --x 18446744073709551615 --y 18446744073709551615
scripts/run-experiment-002.sh --scenario requester_offline
scripts/run-experiment-002.sh --scenario early_disclosure
scripts/run-experiment-002.sh --scenario late_funding
```

The loader rechecks the exact platform binary SHA-256 and commit b272ce3366987406406e9eb1b82596653a3ad628 before execution. Startup explicitly passes `--hardfork cancun`, checks the reported fork and refuses a public fork URL. Initial installation needs HTTPS; the experiment uses only local files and literal loopback, with proxies, redirects and CCIP Read disabled. Unknown platforms or missing/unverified binaries fail; there is no PATH fallback.

Success prints public JSON with `outcome=settled`, `state=2`, `value=expectedValue`, zero provider credit after withdrawal, `ledger` fee/balance/attempt reconciliation and `childrenStopped=true`. A terminated provider after a valid claim can instead leave a precisely recorded unwithdrawn credit. Refund cases print state 3. Reorganization is explicitly inconclusive. Tests retain successful scenario evidence in ignored `internal/task012/agent-runs.json`; command output can be redirected into `internal/`.

## Trust and control boundaries

The trusted supervisor owns only the deployment key. Requester and provider independently create ephemeral in-memory keys in separate OS processes, publish public addresses, and exchange signed bounded regular-file messages. No key is exported, passed through environment/arguments or shared with the supervisor/peer. Trusted operator/barrier files schedule the test; they are not economic authorizations. Each agent checks signatures, terms, deployment/run, canonical state and its own wallet policy. The provider needs no post-funding requester message or signature; requester observation is a local research log and cannot gate the contract claim.

Only the supervisor initially sets synthetic balances: deployer 6*10^15, requester 48*10^15 + exactly 10^12 principal, provider 48*10^15 wei. There are no top-ups. Signer policy reserves 6*10^15 before each attempted transaction, keeps closing slots, binds funding retries to one exact intent and forbids fee escalation/replacement/new-principal intents. Signed principal authorization and operator fee authority remain separate. Gas limit 2,000,000, max fee 3 gwei, priority cap 1 gwei, attempts 1/8/8 and maximum principal 10^15 remain unchanged.

Receipts are checked against canonical blocks, transaction membership, EIP-1559 arithmetic, individual/block receipt prices, reported transaction gasPrice and integer wallet deltas accounting for principal/withdrawals. The closed fixture requires one transaction per block; it is not a general concurrent-wallet fee oracle. The supervisor independently audits every included transaction and all role balances, including transactions from subsequently terminated agents. Ambiguous broadcasts latch the signer; there is no blind retry or new nonce. Keys/raw signed transactions are never retained in evidence.

A run is bounded to 120 seconds plus 15 seconds cleanup; RPC calls use one-second timeouts. The cooperative 2 GiB RSS watchdog records samples, not a hard OS memory quota. Messages are limited to 16 KiB; deliberately oversized/truncated fault messages are confined to the temporary test directory. All children are terminated/reaped and files removed on normal/exception/interrupt exits; SIGKILL or host failure can defeat application cleanup.

The host, filesystem supervisor and privileged Anvil RPC are trusted. Process separation does not resist a hostile administrator. Public outputs can be learned before payment; absent/censored/late claims may never pay. No automatic closure, compensation for work/gas, finality guarantee, objective AI-quality/physical-truth verification or production assurance follows. Independent review and supply-chain risks remain open.

## Task 014 hardening

[Remediation and limitations](../../../docs/experiments/EXPERIMENT_002_REMEDIATION.md) document owner/state reconstruction, pinned/repeated observations, cross-source receipt/own-intent checks and a sticky evidence-failure latch. Agents share the supervisor's cooperative monotonic deadline; RPC/signing/ready-barrier phases check it without increasing any budget. The late-funding fault scenario alone holds automining until a transaction is pending and explicitly includes it at the original last-valid time; this is a trusted test control, not a censorship/inclusion guarantee. Funding errors report cached public observations as not currently verified, without raw signed transactions or extra recovery RPC calls. Acceptance remains pending independent re-review.
