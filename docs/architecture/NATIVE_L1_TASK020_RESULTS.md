# Task 020 — spending policy and measurement closure

**Measurement pending; G1 remains HOLD until both scored batches are checked.** Baseline `4c7d71d214f53fc3edac2be019b534003ae115fa`. Original Task019 evidence remains unchanged. No architecture selected or eliminated.

The original extended-UTXO S09 timeout reproduced before modification. An isolated diagnostic computes2,242,702 original proxy bytes: at10KiB/s,219.014 seconds are required even with zero compute, exceeding the180second ceiling. The memory-only profile completes1,000 actions without conflicts/retries and is dominated by signature verification. Full-state persistence and growing spent-output/replay history are additional implementation work, separately measured rather than removed. This is a representation/link-budget limitation, not evidence that extended UTXO cannot support the workload.

[Spending policy](NATIVE_L1_SPENDING_POLICY.md) replaces the implicit owner-lock claim with an explicit, exact-delta balance-pool covenant and independent native transaction audit. Compact full-width dependency hashes and removal of an unused delegate-balance dependency reduce wrapper traffic; no signed intent, meaningful state dependency, fee, fsync or resource cap is removed. [Measurement contract](NATIVE_L1_MEASUREMENT_CLOSURE.md) defines successor instrumentation and two clean Linux environments.

Scored evidence, repetition ranges, failures and a final disposition will be added after both batches complete. Remaining native dependencies include authenticated state/outcome/non-execution/finality evidence, permissionless admission/bootstrap, network availability and recovery, secure signing and genuine service demand. Trusted fixture finality and AI choices supply none of those guarantees.
