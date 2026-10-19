# Task 019 evidence index

Measured model source: `6872f4b2a208f70074b67bbd47e9095043e0dc18`. Both complete 273-slot run plans, full compressed traces, runtime/source/input identities, HOLDs and offline checks are committed here. [Results and decision](../../../docs/architecture/NATIVE_L1_COMPARISON_RESULTS.md) and [metric limitations](METRIC_LIMITS.md) govern interpretation. `SHA256SUMS.json` covers the public evidence files; source/input hashes are also embedded in results.

Local reproduction used a clean Git archive and fresh CPython3.12.1 virtual environment. `model-requirements.lock` is the exact PyCryptodome3.24.1/hash subset of the unchanged SDK lock: the complete lock failed locally with no matching distribution for `ckzg==2.1.8`. Ubuntu CI independently installed the complete SDK lock. No dependency version/hash was relaxed. Docker had no running daemon and is not counted. Different operating systems/control support prevent an equivalent resource-profile claim.

Reproduce models using [the pinned commands](../../native_l1/README.md), unchanged signed inputs and source lock. The runner intentionally exits nonzero for HOLD. Check the retained evidence without model dependencies, from repository root:

```sh
python3 research/reports/task019/verify_evidence.py research/reports/task019/local-results.json --second research/reports/task019/ubuntu-results.json --trace research/reports/task019/local-traces.jsonl.gz
python3 research/reports/task019/verify_evidence.py research/reports/task019/ubuntu-results.json --trace research/reports/task019/ubuntu-traces.jsonl.gz
```

The offline checker imports no candidate code, reconstructs lossless traces, compares every core barrier with frozen expectations, checks accounting, complete plans and deterministic repetition/reproduction. It does not certify an arbitrary script engine or turn HOLD into acceptance. `supplemental_controls.py` and `probe_recipient_pool.py` were local postmeasurement probes using existing public signed inputs, outside benchmark counts. Their outputs preserve twelve successful boundary controls and the unresolved recipient-pool counterexample. CI links/status are in `ci-status.json`; hosted artifacts additionally have 30-day retention, but committed evidence remains available.
