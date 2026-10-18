# Task 019 — executable architecture comparison

**Measurement pending; no architecture selection or elimination.** Implementation starts from `ce4a8211df64ed73a28ec16c0418aa4660905f52`. The [frozen v1 baseline](../../research/fixtures/native_l1/README.md) is unchanged. This publication supplies three bounded local models, an independent harness and a pinned public stress expansion; it does not claim the full comparison has passed before its evidence is collected.

## Implemented boundary

[Source and reproduction](../../research/native_l1/README.md): mutable account tables, versioned owned/shared objects, and explicit consumed/created extended-UTXO outputs with replay-registry successors. Economic mutations/commits are separate; pure authorization/codec/crypto helpers and the application-level client are explicitly shared. Shared admission logic is a correlated implementation risk, not three independent security audits.

The independent runner checks frozen full projections, separately computes stress accounting, asserts supply/authority-cap/replay/beneficiary/terminal invariants, audits native outputs/ownership and compares repeat signatures. Seven bounded test methods cover all21 core vectors on all candidates, signed stress integrity, real stale-wrapper behavior, wrong-signature/no-debit controls, durable reload/latching and deliberately corrupted model evidence.

Full measurement is 21 core+9 stress configurations, three repeats and one warm-up/model. Linux CI uses a fresh hash-locked CPython3.12.1 environment. A separate clean local source/environment is required for reproduction; repeated runs in one process or on one host are not a second independent environment. Docker's installed client has no running daemon and is not claimed as a reproduction environment.

## Evidence acceptance

Full results, traces, source hashes, platform/runtime/command metadata and HOLDs will be retained and reviewed before replacing this pending disposition. macOS does not supply equivalent hard memory/affinity enforcement in this harness; its resource profile must remain qualified. The separate client is server-assisted for wrapper construction and consumes pre-signed inputs; autonomous native witness construction, live signing cost and real proof verification are not established.

No production throughput, permissionless consensus/finality, physical-service validity, organic adoption or secure useful-work consensus follows. Real authenticated recovery/non-execution evidence and permissionless bootstrap/security remain the most consequential native dependencies. Proposed Task020 depends on the measured findings; no native devnet is authorized here.
