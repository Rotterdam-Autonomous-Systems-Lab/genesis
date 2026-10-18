# Architecture-neutral comparison adapter — v1

Normative for the [Task 018 corpus](../../research/fixtures/native_l1/README.md), refining [Task 017 ASR](NATIVE_L1_AUTHORITY_SETTLEMENT_RECOVERY.md). This specifies interfaces, not their implementation. Accounts, objects and extended UTXO must retain distinct mutation/version/spend mechanisms; shared encoding, signature verification and instrumentation are permitted and disclosed. No shared candidate state-mutation engine.

## Interface and barriers

| Operation | Shared behavior | Candidate responsibility |
| --- | --- | --- |
| initialize(manifest, snapshot) | Validate initial supply/authority; return handle and projection. | Represent balances, seeded grants, replay records and agreements; count every registry/index. Seeded state pays no retrospective creation fee. |
| build(intent, references) | Preserve exact signed logical intent; return wrapper identity and build metrics. | Account references, object versions or input selection; freeze wrapper encoding before runs. |
| attempt(wrapper) | Report structural rejection or pending submission; never imply financial admission. | Record real stale references/conflicts, bytes and verification work. |
| include(wrapper, tick, slot) | Atomic success, semantic revert, pre-admission rejection or duplicate/conflict. | Apply native representation rules; only canonical fresh-reference barriers must equal the golden projection. |
| observe(anchor, query) | Return ledger/outcome evidence with provenance and cost. | Expose candidate state and all dependencies; RPC response alone is not authenticated truth. |
| client(event, observation) | Prepare, submit, crash, recover and refuse unsafe new intents; persist journal. | Candidate wrapper recovery/rebuild within shared bounds. |
| checkpoint / rollback(anchor) | Scheduler-only O2 branch rollback; not a client command. | Restore ledger branch, retain client's uncertainty and journal. |
| project / trace | Exact common ledger/client fields plus separately labeled native attempts. | Include internal records/bytes/work; never hide an indexer or outcome registry. |

Canonical `include` events specify ordered ledger barriers, not automatic client sends. Client events are explicit in the corpus; unchanged idle client projections in ledger-only cases are intentional. All aliases resolve through the manifest. Snapshots use human-readable labels, while signatures and candidate inputs use the frozen binary IDs. Expected consumed-intent labels resolve to their exact intent hashes.

## Admission and accounting freeze

Use ASR wire bytes/digests exactly; verify against the **actor's current registered key**, never the descriptive fixture `signer` field. Wrong-key vectors are correctly signed by an unauthorized key. Terms verify under current A/B keys. Numbers are checked uint64 except the fixed 16-byte uint128 result. Terminal codes are None=0, Funded=1, Settled=2, Refunded=3; credits hash `[agreementId,terminalCode]` as ASR specifies.

Order checks: (1) bounded exact parsing/network/current key/epoch/signature; (2) consumed actor/sequence lookup: identical intent returns duplicate without fee, different intent is sequence conflict; (3) intent expiry; (4) operation target/principal authority, grant version before delegate membership, root epoch, active status, scope/recipient and expiry; (5) fee ceiling and fee solvency; (6) semantic execution. Candidate structural validity must hold before economic admission; count its checks separately. For multiply invalid inputs, the first applicable check in this order determines classification; unspecified sub-reasons within one stage need not match. Golden single-fault reasons must match. A duplicate after revocation still returns duplicate if its current-key authentication remains valid; old-epoch authentication cannot use this shortcut.

Claim/Refund/Collect require the stored B/A/credit owner respectively before fees. Revoke/RotateGrant/ReturnReserve require the stored root. New Grant reserves P+F and its creation fee from root atomically. Direct spending reserves the entire ceiling from its own balance before testing principal solvency. Delegated spending reserves from F, principal from P. Every admitted success/revert consumes its sequence and charges exactly 1; revert changes no principal or beneficiary. Failed admission, duplicate and structural rejection change nothing and cost no ledger fee. Fee-free rejection still consumes measured compute/bandwidth.

Maintain `principal_cap = principal_used + principal_pool + principal_returned` and the analogous fee identity. ReturnReserve increments returned counters, zeroes pools and cannot reset used values. Refunded agreement value becomes root credit, never new grant authority. Credit collection retains a consumed tombstone; terminal agreements and consumed sequences remain available. Sum spendable funds, remaining reserves, Funded prices, outstanding credits and fee sink equals initial supply. Collected credits do not count twice. Concurrent mutations must satisfy all identities atomically.

Time is scheduler-provided integer, monotonic within a branch: intent/grant expiry and funding/claim use strict less-than; Refund uses greater-than-or-equal claim deadline. Revoke/rotation applies at included order; revocation cannot cancel already-funded work. Correct sum permits B settlement and collection without a new A intent. It proves the agreed predicate, not charging, parking, navigation or any physical delivery.

## Recovery and evidence

Journal intent identity/maximum principal and fee exposure durably before submission, then wrapper identity durably before broadcast. Task 019 specifies filesystem flush/crash injection and measures overhead. Private keys and raw transport transactions never enter public traces. Frozen signed logical fixtures are deliberately public; do not treat them as live authorization.

`prepare` reserves exposure; `submit` increments submission count; lost reply or crash retains it. Querying unavailable or contradictory evidence must not release reservations, declare success or issue a fresh logical intent. Only authenticated fixture final outcome releases exposure. Prefinal inclusion is not final; rollback restores ledger but not spending certainty. Contradictory purported finality is an assumption breach and sticky halt for that trace, never a ledger rewrite. A subsequent convenient reply cannot reset that latch.

The positive oracle is explicit laboratory infrastructure. A fenced-absence observation closes the delivery epoch, confirms non-admission for **all journaled wrappers**, and invalidates pending old wrappers before permitting bounded rebuild of the **same** signed intent. “Not found”, spent input or stale object version alone cannot do this. Reject retry when prior inclusion contradicts absence. Maximum three submissions/eight recovery queries and existing journal/client budgets apply. V09's injected stale-reference event tests this rule; it is not evidence that all state models incur that structural conflict.

O1 uses trusted fixture finality; O2 allows scripted prefinal rollback; O3 injects contradictory finalized claims. Native proof formats, consensus attacks and actual light-client authentication remain unresolved outside this adapter. RotateKey execution and guardian recovery are outside v1; stale-epoch rejection is included. Expanding v1 requires a reviewed version change, not ad hoc implementation choices.

Invoice/reference reuse alone is not a protocol duplicate: changing sequence creates a new explicitly authorized intent. V1 deduplicates exact intent identity and forbids conflicting reuse of actor/sequence; it does not invent a global physical-service invoice registry. Applications needing one-payment-per-invoice must bind that policy in separately specified state. Unknown-outcome recovery may not evade deduplication by creating a new sequence.
