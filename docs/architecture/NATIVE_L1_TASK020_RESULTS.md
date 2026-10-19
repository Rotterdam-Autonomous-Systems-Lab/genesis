# Task 020 — spending policy and measurement closure

**Measurement pending; G1 remains HOLD until both scored batches are checked.** Baseline `4c7d71d214f53fc3edac2be019b534003ae115fa`. Original Task019 evidence remains unchanged. No architecture selected or eliminated.

The original extended-UTXO S09 timeout reproduced before modification. An isolated diagnostic computes2,242,702 original proxy bytes: at10KiB/s,219.014 seconds are required even with zero compute, exceeding the180second ceiling. The memory-only profile completes1,000 actions without conflicts/retries and is dominated by signature verification. Full-state persistence and growing spent-output/replay history are additional implementation work, separately measured rather than removed. This is a representation/link-budget limitation, not evidence that extended UTXO cannot support the workload.

[Spending policy](NATIVE_L1_SPENDING_POLICY.md) replaces the implicit owner-lock claim with an explicit, exact-delta balance-pool covenant and independent native transaction audit. Compact full-width dependency hashes and removal of an unused delegate-balance dependency reduce wrapper traffic; no signed intent, meaningful state dependency, fee, fsync or resource cap is removed. [Measurement contract](NATIVE_L1_MEASUREMENT_CLOSURE.md) defines successor instrumentation and two clean Linux environments.

Scored evidence, repetition ranges, failures and a final disposition will be added after both batches complete. Remaining native dependencies include authenticated state/outcome/non-execution/finality evidence, permissionless admission/bootstrap, network availability and recovery, secure signing and genuine service demand. Trusted fixture finality and AI choices supply none of those guarantees.


## Premeasurement correction

Checkpoint `dc589ba` full batches were cancelled after review found that proxy build requests charged only an intent hash while the server actually required its preimage. Its local172.1second S09 result is a superseded lower-bound diagnostic, **not an accepted resource pass**. Partial CI artifacts and the cancellation remain evidence. The corrected service receives and charges the actual preimage-only build input (no outer signature is needed for non-financial reference construction); inclusion still verifies the complete signed intent. No implicit preloaded future-intent registry/cache receives free credit. Both clean-environment scored batches restart from the corrected source lock. Additional network cost may cause further HOLDs under unchanged caps; those must be retained.


Corrected-source run39235894960 subsequently exposed a cleanup defect: a killed client's buffered stdin raised `BrokenPipeError` during close and masked the watchdog. Both incomplete plans and their traces/logs are retained; the independent checker rejected them. A deterministic regression reproduces the error before the fix. Cleanup now suppresses only this expected pipe-close error, preserves the original watchdog/validation exception and closes all pipes. An end-to-end forced-watchdog control verifies the resource error survives cleanup. No candidate or budget is weakened; final scored batches restart from the corrected cleanup source.
