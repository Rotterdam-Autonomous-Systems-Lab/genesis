# Measurement and reproducibility — Task 018 v1

This is a measurement plan, not results. Use the [adapter](NATIVE_L1_ADAPTER.md), [frozen artifacts](../../research/fixtures/native_l1/README.md) and unchanged [B1–B9 ceilings](NATIVE_L1_RESOURCE_BUDGETS.md). Measurements describe local bounded models, never production throughput, consensus security or adoption.

## Controlled runs

Exactly 21 core configurations plus nine deterministic stress configurations; three measured repetitions each and one unmeasured warm-up per model = **91 runs/model maximum**. Core configurations reset state independently. The fixed stress plan specifies identities, setup accounting, allocation, salts, actions and time. Task 019 expands it once into a public signed input manifest before measurements; all candidates/repetitions replay the same manifest. No RNG-dependent schedule or per-candidate key/input generation. Preserve all artifacts and failures.

Use baseline R, with mandatory L=128 MiB client and S=10 KiB/s proxy overlays assigned to existing configurations, not a cross-product of extra runs. Freeze those assignments, worker/client process boundaries, runtime/dependency locks, source hashes, transport wrapper schemas and invocation commands before timing. Three repetitions must use identical inputs, not three favorable samples. CPU affinity/core limit, OS, architecture, runtime/GC, filesystem/durability settings, instrument versions and competing load are recorded. A second clean environment reruns the same signed artifact set; report platform differences rather than merging incomparable samples.

Enforce worker 1 GiB, client proxy128 MiB, one CPU, 120 CPU/180 wall seconds per <=1,000-action run, persistent storage256 MiB, all client traffic16 MiB, journal1 MiB, <=32 pending, <=3 submissions/8 queries per recovery. Retain B1 wire/transport/list/signature limits and B9 batch30 minutes/cleanup15 seconds. Stop and classify excess as HOLD, never increase caps silently. Wall latency includes injected link delays; report compute time separately. O1 uncontended controls must resolve within10 logical ticks; indefinite blackout has no completion guarantee.

## Required metrics

| Metric | Definition / interpretation |
| --- | --- |
| Invariants | Independently assert supply, ownership, authority, replay, P/F limits and terminal consistency at every barrier, including reverts/rollback. Report any mismatch and minimal failing input; zero observed violations is finite coverage only. |
| Conflicts | Count native wrappers built/submitted, stale/input/version rejects, rebuilds and canonical semantic rejects separately. Denominator is attempted logical intents plus setup explicitly labeled; injected stale faults are excluded from intrinsic conflict rates. |
| Recovery | Expected versus actual client classification, journal phases, held/released exposure, queries/submissions, duplicate fees/payments, bytes and ticks to reconciliation. Expected halt/Unknown is a pass only for its named fault case. |
| Verification work | Count bytes parsed/hashed, signatures verified, script/predicate evaluations, state reads/writes and proof checks separately for accepted/rejected inputs. Count all repeated work; cached checks need measured cache size and eligibility. |
| State growth | Initial/final/peak serialized native state and persistent files, replay/terminal indexes, journal and wrapper bytes. Report payload versus runtime overhead; count helpers even if outside main store. |
| Execution steps | Candidate primitive operations and explicit definitions. Different-language step counts are not comparable machine instructions; use them to explain CPU/bytes, not rank by arbitrary instruction granularity. |
| CPU / memory | Monotonic wall time, process CPU, peak RSS for separate worker/client process trees and disk high-water mark. Record OS units/sampling limitations; Python object estimates alone are not measured RSS. |
| Network / settlement | Logical and transport bytes including rejects, queries and observations; scheduler ticks and modeled delay separately from real elapsed time. Fixed oracle latency does not measure blockchain finality. |

Time input parsing/signature verification, state transition, persistence and client recovery, with component totals plus end-to-end totals. Golden assertion/projection serialization is outside transition timing and reported separately; native indexes and observation production remain inside their relevant costs. Harness RSS is separate, not hidden in the client's budget. If a cost cannot be measured, mark unavailable/HOLD for that criterion, never zero.

## Acceptance

Task 019 BOUNDED MODEL PASS requires all 21 core vectors and nine stress configurations to match independent golden/invariant expectations, deterministic repeats, all ceilings, complete metrics and second-environment reproduction. Task 017's wider suggested boundary/permutation suite is not claimed covered: list follow-up omissions explicitly. Extra coverage needs a reviewed version/run-plan change within caps. A failing adapter does not eliminate a state-model family without evidence of an unavoidable constraint rather than an implementation defect.

Publish model source/dependency hashes, corpus checksums, expanded stress manifest, native attempts, canonical projections, journal/evidence events, timing/resource records and failures. Report three-repeat ranges and environment differences; no statistical superiority claim. Ledger safety and recovery correctness precede any cost comparison. No production TPS extrapolation from this single-process oracle experiment.

### Fixed minimal schedules

All nine v1 stress runs use sequential fresh-reference build/include barriers at tick1, ascending generated action index. Thus they measure shared-state footprints and sequential verification, **not parallel throughput**; report native structural conflicts as zero if none occur, without inferring immunity to contention. V01/V20 test ordered competing authority; V05/V06 test opposite revocation order; V09 tests injected stale transport recovery. A later parallel/batched scheduling factor requires a reviewed successor manifest and remains inside action/run caps. Do not silently add a second 1,000-action phase. Active stress clients are the first c principals sorted by raw ID; allocation/remainder and client indexing use that same order.

Fixed overlays within the 30 configurations: V08/V09 and S07–S09 additionally run the client under L128 MiB; V10/V16 use S10 KiB/s with unavailable evidence respectively prefinal rollback as specified, and S09 uses S10 KiB/s with the unchanged tick1 ledger schedule (wall transmission cost remains measured). These are overlays in those runs, not additional runs. Remaining configurations use R/unlimited-link control. This minimum isolates model behavior; broader Task 017 blackout/delay sweeps remain unexecuted follow-up coverage.
