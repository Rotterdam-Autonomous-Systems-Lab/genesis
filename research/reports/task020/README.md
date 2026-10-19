# Task 020 evidence

[Results](../../../docs/architecture/NATIVE_L1_TASK020_RESULTS.md), [spending policy](../../../docs/architecture/NATIVE_L1_SPENDING_POLICY.md), [measurement contract](../../../docs/architecture/NATIVE_L1_MEASUREMENT_CLOSURE.md). No frozen logical fixture or signed stress artifact changes.

Before modification, CPython3.12.1/PyCryptodome3.24.1 ran from baseline4c7d71d:

```sh
internal/task019-clean-venv/bin/python -m research.native_l1.runner --output internal/task020-original-s09 --models eutxo --cases S09 --repetitions 1
internal/task019-clean-venv/bin/python -m research.reports.task020.profile_original
```

The selected S09 also becomes the original runner's warm-up and times out at180seconds, aborting before scored repeats. `original-s09-results.json`/compressed prefix and `original-source-lock.json` retain this negative result; it is not a complete comparative run. `original-profile.json` is an unscored memory-only cProfile diagnostic, excluding persistence, IPC, client and harness; replay the helper against the original model source (Git archive/worktree at4c7d71d, with its repository root on PYTHONPATH). Do not compare its elapsed timing to scored runs. Its exact traffic arithmetic independently proves the219second link floor.

`append_only_control.py` is a two-payment non-coalesced ownership control, not a fourth complete adapter. `append-only-control.json` preserves its output. `verify_evidence.py` performs independent offline resource/trace/reproduction checks. Full scored run manifests, traces, hashes and CI provenance are added after both fresh Ubuntu environments finish.

Reproduce successor models with the pinned commands in [model README](../../native_l1/README.md). Install the complete unchanged SDK dependency lock; do not regenerate signed stress inputs or relax resource limits. Both CI jobs start fresh VMs and virtual environments using the same input/source lock. Host hashes and separate replica/job provenance qualify independent environment provisioning, not independent implementation authorship.
