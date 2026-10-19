# Task 019 — executable architecture comparison

**CONTINUE COMPARISON — G1 HOLD. No candidate selected, eliminated or prioritized.** Three distinct bounded models executed the unchanged [frozen v1 baseline](../../research/fixtures/native_l1/README.md). Measured source is `6872f4b2a208f70074b67bbd47e9095043e0dc18`; the later evidence-publication commit changes reports only. No complete BOUNDED MODEL PASS is justified.

## Evidence and coverage

Each environment executed the full 273-slot plan: 21 core vectors plus nine stress configurations, three measured repetitions and one warm-up/model. All 32 frozen signed intents and the identical 3,330-action public stress expansion were integrity checked. No expected outcome, cap or frozen fixture changed.

| Environment | Model | Measured PASS / HOLD | Complete configurations | Peak worker RSS | Maximum native file |
| --- | --- | --- | --- | --- | --- |
| macOS 12.7.6 | Accounts | 90 / 0 | 30/30 | 27.8 MB | 278,102 B |
| macOS 12.7.6 | Objects | 90 / 0 | 30/30 | 29.8 MB | 461,026 B |
| macOS 12.7.6 | Extended UTXO | 87 / 3 | 29/30 | 64.1 MB | 3,721,046 B |
| Ubuntu 24.04 runner | Accounts | 90 / 0 | 30/30 | 50.0 MB | 278,102 B |
| Ubuntu 24.04 runner | Objects | 90 / 0 | 30/30 | 51.5 MB | 461,026 B |
| Ubuntu 24.04 runner | Extended UTXO | 87 / 3 | 29/30 | 72.3 MB | 3,721,046 B |

Sizes/RSS describe completed runs only, decimal MB. All six HOLDs are extended-UTXO S09 hitting the unchanged 180-second watchdog. Their checked prefixes and failure evidence remain in full traces; a timeout does not prove non-inclusion of the last attempted transition. The slow-link workload fails for this prototype; no family-wide impossibility or unsupported root cause follows.

All 21 core cases passed three times on every candidate in both environments. The 89 complete model/configuration combinations have identical deterministic final hashes, operation counters and event counters across environments. Accounts/objects each executed 10,140 ledger actions across measured completed runs; UTXO executed 7,140, excluding incomplete S09 prefixes. Seven adversarial unit methods passed locally and on Ubuntu; twelve supplemental local boundary controls also passed. Full [raw results, traces, independent offline checks and metrics](../../research/reports/task019/README.md) are retained.

## Implemented behavior and material qualifications

Accounts use explicit mutable tables and atomic copy/commit. Objects use owned/shared resources, versions and replacement sets. Extended UTXO consumes and creates immutable value/datum/lock outputs with replay-registry successors and transaction conservation. Mutation engines are separate; codec, pure admission checks and client are shared. Shared code remains a correlated security risk.

The independent harness checks every core projection against frozen expectations, computes stress accounting separately, audits native ownership/value and enforces conservation, principal/fee caps, replay and terminal consistency. Negative controls detect forged success, wrong ownership/value and real stale wrappers. Finite deterministic work settlement requires no second requester signature. This remains a trusted ordered-model result, not new consensus evidence.

**F019-01 — recipient spending policy incomplete (unresolved).** Existing `pay12` then D2-signed `pay8` consumes S's 12-unit balance output and creates S's 20-unit output without S's signature. Value and beneficiary are preserved; no theft is demonstrated. A public top-up covenant could permit this, but its script and independent validation against untrusted successor proposals are not established. The prototype is a coalesced recipient-pool profile; it cannot receive credit for conventional owner-signature UTXO spending or general script security. Preserve the [counterexample](../../research/reports/task019/recipient-pool-counterexample.json); do not silently fix the measured model.

**F019-02 — resource gate incomplete (unresolved).** S09 watchdog failures alone prevent full acceptance. Additionally, macOS lacks equivalent hard memory/affinity controls; per-process limits do not demonstrate aggregate CPU-group limits, and harness RSS is missing. Signature checks are counted, but total hashing is incomplete, read/write units differ and storage archives differ. Native files exclude the immutable fixture registry; [metrics](../../research/reports/task019/metrics.json) separately report derived registry-inclusive sizes. These are implementation descriptors, unsuitable for architecture rankings. See [measurement qualifications](../../research/reports/task019/METRIC_LIMITS.md).

Fresh-reference stress produces zero intrinsic structural rejects; V09 injects one per repetition/model. Separate real stale-wrapper tests exercise structural rejection and safe rebuild. This does not measure parallel contention or production conflict rates.

## Reproduction, regressions and CI

Two isolated environments used identical source/input hashes, CPython3.12.1 and PyCryptodome3.24.1: a clean local Git archive/fresh environment and a fresh Ubuntu GitHub runner. The local full SDK lock could not resolve `ckzg==2.1.8`; an exact hash-pinned subset containing the model's sole external dependency was installed instead. Ubuntu installed the complete original lock. Reproduction is shared-source behavioral reproduction, with unequal resource profiles; it is not independent implementation review.

[Model CI](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39177558074) concluded **FAILURE**, preserving the expected nonzero resource-HOLD result, not bypassing it. [Regression CI](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39177558069) passed: 86 Solidity tests, nine fixture-integrity tests, 54 Experiment001 tests on each validated node, 14 original-node fee controls, nine corrected-node controls, 73 Experiment002 tests, standalone settlement and signature/fee probes. The final report commit receives ordinary publication regression CI separately.

Use the [pinned runner commands](../../research/native_l1/README.md) and [offline reproduction commands](../../research/reports/task019/README.md). Source-lock, stress-input hashes, complete commands/platforms, repeats, timings, native stores and partial traces are committed. Do not regenerate public signed inputs or raise budgets to accept a failure.

## Remaining dependencies and Task 020

The client uses pre-signed inputs, server-assisted wrappers, a durable journal and trusted scheduler finality/fencing observations. Simulated client restart is not validator power-loss recovery. Native proof construction/verification, authenticated non-execution evidence, permissionless consensus/bootstrap, arbitrary programs, physical delivery, constrained-device signing and organic demand remain untested. AI decisions and useful work provide no assumed protocol security. These limitations apply across the full human/agent/vehicle/robot/drone/satellite research vision.

Recommend **Task020: adversarial adapter and measurement remediation**: explicitly specify and independently validate UTXO top-up spending conditions (or append recipient outputs), complete aggregate resource/metering evidence and failure-boundary capture, then review the changed source and rerun unchanged logical workloads under existing caps. Diagnose S09 with retained evidence; preserve failed results. No native devnet, consensus, token mechanics or final architecture selection follows. Authenticated recovery/finality evidence and viable permissionless bootstrap remain the consequential native-L1 dependencies after this bounded correction.
