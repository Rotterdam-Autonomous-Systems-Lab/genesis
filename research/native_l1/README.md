# Task 019 — bounded native state-model comparison

These are local research models, not nodes, production consensus or wallets. The [frozen v1 corpus](../fixtures/native_l1/README.md) is unchanged. No useful-work consensus, physical service truth or economic demand is asserted.

## Reproduce

Use **CPython 3.12.1**, a fresh virtual environment and the existing `sdk/python/requirements.lock` installed with `--only-binary=:all: --require-hashes`. PyCryptodome is pinned to3.24.1. From repository root:

```sh
python3 -m venv internal/task019-venv
internal/task019-venv/bin/python -m pip install --only-binary=:all: --require-hashes -r sdk/python/requirements.lock
internal/task019-venv/bin/python research/fixtures/native_l1/validate.py
internal/task019-venv/bin/python -m unittest discover -s tests/native_l1 -v
internal/task019-venv/bin/python -m research.native_l1.runner --output internal/task019-results
```

The full command runs 30 configurations three times plus one warm-up per model:91 runs/model,273 total. No frozen inputs, source lock, caps or expected outcomes may be changed to accept a failure. Optional `--cases`/`--models`/`--repetitions 1` are development runs, explicitly ineligible for comparative acceptance. The output path must not exist. JSON summaries, lossless row-delta gzip JSONL traces (initial snapshots and full final native state included) and environment/source identities are retained. Source hashes and the committed signed stress artifact must match `evidence/source-lock.json` before measurement. Do not regenerate stress keys for repeats or another environment.

## Distinct representations and shared boundary

| Model | Native representation / transaction rule | Limitations |
| --- | --- | --- |
| Accounts | Balance/key/grant/agreement/credit tables; actor-sequence outcome map; serial copy/commit of atomic ledger state. | Prototype copies tables rather than a database write set; cost is implementation-specific. |
| Objects | Explicit owned balance/key/credit resources, shared grant/agreement objects, per-resource versions; atomic replacement set. | Shared fee-sink object is a serialization point. No production ownership type system or object VM is implemented. |
| Extended UTXO | Explicit immutable value/datum/lock outputs, live lookup index, spent attribution and consumed/created transaction lists; per-actor replay registry successor and grant successor. Every transaction conserves input/output value including fee outputs. | One coalesced coin output per principal; output selection/indexing is not a full wallet. Registry outputs and history retain storage; no pruning or claimed Bitcoin Script equivalence. |

No model imports another candidate's mutation code. Common `Context` provides **shared pure admission checks** (current-key/domain/replay/scope/fee-solvency), codec/crypto, label conversion and counters; it returns no mutation or delta. These shared checks are correlated implementation risk, disclosed rather than presented as three independent security audits. Candidate-specific economic mutations and atomic commits are separate. Full common projections are only observations, never fed back as model transition state. Object versions and UTXO inputs reject stale wrappers; account execution reads current state. Wrapper schemas are frozen by source identity: account actor/epoch, object target versions, UTXO output references, each bound to exact intent digest. Wrapper JSON plus signed logical input is the illustrative transport; it is not a native protocol selection.

The independent harness sees actual projections and compares every core barrier with frozen expectations, constructs a separate arithmetic stress oracle, checks conservation/caps/beneficiaries/replay/terminal consistency, and audits native ownership/output histories. Deliberate false-success, wrong-owner/value and stale-wrapper tests show failures are detected. Model-reported status alone cannot pass.

## Client, evidence and resource boundary

The same application-level client runs in a **separate process**, without a ledger copy, with public signing inputs only. It verifies pre-signed intents, records/fsyncs intent identity before submission and wrapper identity before broadcast, reloads the durable journal on simulated crash, retains maximum unknown exposure and latches contradictions. Finalized entries compact to outcome hashes; ledger replay/terminal records are never pruned. Crash injection discards volatile Python state; it is not a host-power-loss/filesystem audit. Signing-key protection and signing cost are not measured because inputs are frozen public signatures before timing.

Positive observations are a trusted scheduler oracle. No real proof validation/finality or authenticated absence construction exists. Model reference construction is a metered worker service; constrained clients receive proposed wrappers and verify immutable intent identity, not full native proofs. This is explicit server-assisted wrapper construction, not proof that autonomous constrained devices can independently construct native witnesses. Retain that limitation in acceptance.

Worker/client CPU/RSS, serialized native state/history, journal flushes, verification/read/write counts, transport bytes, IPC/debug bytes and full traces are distinct metrics. Projection/assertion serialization is excluded from transition timing but remains inside process watchdogs. Native persistence includes JSON serialization and fsync of full retained state. OS page cache is uncontrolled; fresh processes and one warm-up are declared, not a cold-cache guarantee.

Linux workers/clients use one shared allowed CPU affinity, RLIMIT_CPU120s, address-space limits1GiB/128MiB (stricter than RSS), plus peak-RSS checks. The parent uses a180s/run watchdog and15s cleanup. macOS cannot supply equivalent hard memory/CPU-affinity enforcement here: report that profile as resource HOLD, never an equivalent budget pass. All state/history <=256MiB, journal <=1MiB, <=32 unresolved and <=3 submissions/8 queries per recovery; fixed v1 slow-link overlays shape total proxy bytes to10KiB/s without advancing tick1 stress semantics. Every request/reply/recovery byte is counted; debug projections use a separately measured harness channel, not a hidden client indexer.

Stress uses sequential fresh references as v1 requires; intrinsic conflict counts may be zero. Separate bounded unit tests construct real stale wrappers; they are not included as production conflict-rate measurements. A shared-budget race is represented by competing ordered intents, not a parallel scheduler throughput claim.

## Interpretation

Pass finite safety separately from resource/reproduction criteria. Keep every failure and HOLD; never silently raise caps or omit cases. Cost differences include language/storage/index design and shared code; they do not establish state-model-family superiority. A model bug cannot eliminate its architecture family. Permissionless admission/bootstrap, consensus security, real authenticated finality/recovery, light-client proofs, physical service evidence, native VM metering and genuine demand remain untested.
