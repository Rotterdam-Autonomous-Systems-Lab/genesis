# Common authority, settlement and recovery specification — Task 017

**Proposed laboratory semantics, not a selected native protocol.** Applies to [W01–W08](NATIVE_L1_WORKLOADS.md) and extends Task 016's [comparison](NATIVE_L1_DECISION_MATRIX.md). Experiments 001/002 remain unchanged. Delegation, durable journals and native authenticated proofs are new requirements, not inherited experimental guarantees.

## 1. Common logical state and signed intent

State contains principal balances, registered public keys/epochs, grants, agreements, owner credits, consumed intent identifiers and a fee sink. Initial synthetic balances are fixed by each case; no issuance or top-up operation exists. Amounts, epochs, sequences and logical time are unsigned 64-bit integers; checked arithmetic rejects overflow. Grant/intent/agreement identifiers are 32-byte digests. Network identity commits to a fixed genesis-fixture header before intents/corpus are generated (not a hash of a self-referential final corpus manifest); perfect cloned ledgers with the same identity remain indistinguishable without an external trusted anchor.

For a future reference model, define unsigned intent as the fixed-order array:

```text
[1, networkId, actorId, keyEpoch, sequence, validBefore,
 feeCeiling, operationCode, arguments]
```

Use RFC 8949 core deterministic CBOR: definite-length arrays/byte strings, shortest unsigned integers, no maps, tags, text, floats, null, trailing items or unknown fields. IDs are exactly 32-byte strings. `intentId = SHA-256(CBOR([h'47454e455349532d4c41422d303137', unsignedIntent]))`; the byte literal is the ASCII lab domain GENESIS-LAB-017. RFC 8032 Ed25519 signs the 32-byte intentId in the illustrative shared codec profile. Actor ID is stable across key rotation; `(actorId,keyEpoch)` selects its authorized key. Consume `(actorId,sequence)` on admitted inclusion, even on semantic revert. The same sequence with different bytes is a conflict, never new authority. This lab codec/signature choice selects no native-chain cryptography. Publish independent byte/digest/signature vectors before any experiment; do not count shared-library agreement as independent verification. [CBOR §4.2.1](https://www.rfc-editor.org/rfc/rfc8949.html#section-4.2.1), [Ed25519 §5.1](https://www.rfc-editor.org/rfc/rfc8032.html#section-5.1).

| Code / argument array | Required authority and effect |
| --- | --- |
| 1 Transfer `[grantId,to,amount,invoiceDigest]` | Actor spends own balance when grantId is 32 zero bytes; otherwise authorized G delegate. Immutable recipient/amount/reference. |
| 2 Grant `[grantId,delegates,actions,recipients,P,F,expires]` | Root owner only; delegates are sorted unique `[actorId,keyEpoch]` pairs, actions sorted unique codes, recipients sorted unique IDs. Lock P+F; cap/deadline/scope immutable; initial grant version 0. |
| 3 Revoke `[grantId,version]` | G root only; disable future delegated admission and permit unused reserve return. Cannot cancel funded agreements. |
| 4 RotateGrant `[grantId,version,newDelegates]` | G root only, G active; increment version and replace delegate list only. No renewed limits, expiry, resources or used counters; signed delegated intents must name current version. |
| 5 Fund `[grantId,version,terms,requesterTermsSig,providerTermsSig]` | Requester root or G delegate with Fund authority; exact signed agreement, price and first-use deadline; lock price. For direct root use version 0. |
| 6 Claim `[agreementId,value]` | Stored B principal only, valid predicate, Funded state, time strictly before claimBefore; create exact B credit. |
| 7 Refund `[agreementId]` | Stored A principal only, still Funded, time at/after claimBefore; exact A credit. |
| 8 Collect `[creditId]` | Stored credit owner only, consume exact credit to its own balance; no arbitrary destination or second A approval. |
| 9 ReturnReserve `[grantId]` | Root only, revoked or expired G; transfer remaining unlocked reserves to root once. |
| 10 RotateKey `[newPublicKey]` | Current root key of actorId only; increment epoch and replace its own registered key. Cannot seize another principal. Root-issued grants bind creation root epoch and require explicit revocation/reserve return after rotation. |

For delegated Transfer, arguments are `[grantId,version,to,amount,invoiceDigest]`; direct Transfer omits version. The opcode, zero/nonzero grant ID and exact array length select the form, not a permissive parser. All other array lengths are exact. GrantId is SHA-256(CBOR([labDomain,2,networkId,ownerId,creationSequence])); it must be nonzero and unique for owner/network. Terms signatures at funding verify against A/B’s current registered keys; old-key signatures cannot bypass key rotation. Grant action scope is a subset of codes 1 and 5; other operations retain their explicit root/provider/owner checks. Maximum delegates/actions/recipients are in B1; Ed25519 public keys/signatures are exactly 32/64 bytes, and the pinned verifier must reject noncanonical encodings as specified by its reviewed RFC 8032 profile. Reject sorted-list duplicates. Root grant-control operations pay from root's own balance, not the agent's locked fee allowance. Root key loss has no assumed external recovery authority; recovery via threshold/guardian policy is deferred.

`terms = [networkId,A,B,agreementSalt,serviceId,x,y,price,fundBefore,claimBefore]`; x/y are uint64, public predicate is widened integer addition and must not overflow the result representation. The sole result is uint128 encoded as a fixed 16-byte big-endian string (other numbers stay uint64). `agreementId = SHA-256(CBOR([labDomain,5,terms]))`; both A/B sign that digest. ServiceId is the manifest's fixed 32-byte ID for sum-u64; salts/network IDs are supplied in corpus manifests. Price is positive, A/B distinct, fundBefore less than claimBefore. A provider signature commits to price/terms, not its effort. Fund's outer intent supplies A/delegate's first-use authority; delegate funding requires G.root=A and still requires A's upfront terms signature. For future unattended work, a broader operator-approved policy could replace per-agreement terms consent, but is explicitly outside this first comparison.

## 2. Budget and transaction semantics

A grant locks disjoint principal P and fee F pools from H's balance at creation. Overlapping grants cannot reserve the same funds. Successful Transfer/Fund increases monotonically `principalUsed`; price leaves G's principal reserve. A funded price remains locked in the agreement, not available to another delegate. Refund credits **H/A**, never replenishes G's lifetime principal cap. Fees increment monotonically `feeUsed`. Rotate/revoke/return cannot reset either counter; no subdelegation or automatic replenishment. Independent partitioned grants must sum to the same P/F as their shared-grant control.

Admission requires canonical bounded encoding, valid key/domain/sequence, active unexpired grant and matching version/root epoch/scope/recipient (where applicable), feeCeiling at least 1 and sufficient fee reserve for that entire ceiling, and a valid candidate state reference. Authentication or structural rejection produces no state/fee change. Expiry is `time < validBefore` and delegated action additionally `time < G.expires`; pending revocation has no retroactive effect. Once admitted, reserve the fee ceiling atomically; run semantic checks (balance/principal limit, agreement state/result/deadline); charge the fixed laboratory fee 1, release unused fee ceiling, and consume the intent sequence on both success and semantic revert. A revert changes only fee accounting/intent outcome, not principal/credits/grant principalUsed. No actor may be charged for someone else's unauthenticated traffic. The lab fee rule is an accounting control, not proposed economic pricing.

Thus an authorized wrong-result claim or over-budget principal attempt can incur the declared fee; an invalid signature, revoked grant or stale candidate reference cannot. Failed admission cannot be treated as a mined revert. Bytes/reject CPU still cost resources even when no fee is collected; measure that DoS exposure separately. Collection/refund by A/B uses its own bounded fee balance; reserving closing resources is a client policy, not an automatic external payer.

Invariant: initial supply equals spendable balances + G remaining reserves + agreement locked prices + uncollected owner credits + fee sink. At most one Fund per agreement; Funded transitions once to Settled or Refunded; credit IDs are `SHA-256(CBOR([agreementId,terminalCode]))`. Collect consumes a credit exactly once. No actor implies no transition. Grants/keys can expire/rotate without changing beneficiaries or enabling early refunds. Terminal records, consumed sequences and revoked grant IDs need retained state or authenticated non-replay accumulators; pruning without such a design is unsupported.

A simple executable specification is not a permissionless chain. The common ordered engine is a semantic oracle; clients require independent finality/evidence, not the engine's assertion in a real network.

## 3. Model-specific representation, identical observable effect

| Concern | Accounts | Objects | Extended UTXO |
| --- | --- | --- | --- |
| Authority / replay | Owner balance and grant records; consumed actor-sequence map separate from transport nonce. | Owned credentials plus shared grant/intent registry; versioned agreement objects. Shared access is not permission. | Scripted grant/state output successors and identity/intent registry output(s); consumption alone does not prevent replay of rewrapped logical intent. |
| Atomic cumulative limits | One transaction touches G budget, payer and recipients/escrow. | One transaction touches G shared budget and relevant owned/shared funds. | Consume G state/reserve inputs and create exact successors/change atomically; scripts validate the whole required transition. |
| Concurrent grants | Shared record may serialize; disjoint records can be independent. | Owned resources can be independent; shared grant is a hotspot. | One grant-state input serializes spenders; disjoint inputs can be independent. |
| Settlement | Record state machine with explicit credits. | Shared multi-party agreement and owner credit objects; no trusted custodian shortcut. | Datum/script state machine with provider/refund branches, output recipient/value constraints and retained terminal evidence. Plain Bitcoin Script equivalence is not assumed. |
| Recovery | Reconcile logical intent and transport nonce; never allocate fresh intent to resolve unknown send. | Fetch authenticated current versions and outcome; never infer failure from stale version alone. | Fetch authenticated unspent/spent state and intent outcome; a spent input might mean this or another operation executed. |
| Storage / cost | Balance/nonce/grant indexes and permanent replay data; shared writes and callback surface if VM allows. | Version/ownership indices, shared-object history and replay data; resource typing does not prove business logic. | UTXO/datum/witness/change growth plus terminal/replay indices; script verification and input-selection costs. |
| Constrained client | Needs authenticated account/storage/outcome proof and finality, not merely RPC balance. | Needs owned/shared object version/ownership/outcome proofs and finality. | Needs spend/unspent/outcome evidence and validated chain context; an output inclusion proof alone does not prove unspent status. |

These are design obligations, not claims all named platforms already provide these interfaces. [Ethereum account fields](https://ethereum.org/developers/docs/accounts/), [Sui object ownership](https://www.docs.sui.io/develop/objects/object-ownership), [Extended UTXO §§2–4](https://www.iog.io/api/research/pdf/T24L95MI) are primary model references, reviewed 2026-10-19. No VM or consensus choice follows from them.

Adapters must retain the actual model's spend/version/conflict rules rather than implement the same dictionary three times. They project to a common owner/intent/grant/agreement/credit snapshot after each ordered action; internal roots/layouts need not match. Structural conflicts are recorded separately from logical rejection. Rebuilding non-admitted transport references may retain the same signed intent, never change terms/fee ceiling/recipient. Only do so after authenticated non-execution and no unresolved envelope, with a finite attempt budget. Even late delivery of an older wrapper must not execute an already consumed logical intent twice. If a candidate needs a new replay registry or authenticated lookup, count its storage/proof/verification costs; no free external indexer.

## 4. Durable recovery and evidence contract

Journal before signing/submission: network, intent bytes/ID, actor/sequence/epoch, grant/version, maximum principal/fee reservation and all transport envelope hashes. Never log secret keys/raw signed transactions in public artifacts. Flush durable intent and then signed-envelope identity before broadcast; a crash between these phases remains an explicit recovery state. Compare:

```text
Prepared -> Submitted/Unknown -> IncludedSuccess or IncludedRevert
         -> Final under chosen evidence profile -> Collected (when applicable)
Included -> Orphaned on admissible reorg -> Unknown/Reconciled
Any contradictory evidence -> Halted until authenticated resolution
```

“Not found” from one RPC is Unknown, not proof of non-execution. Required observation bundle binds network, authenticated head/checkpoint, intent/envelope inclusion or non-execution evidence, outcome, grant counters/version, immutable agreement/state, owner credits and fees at a consistent anchor. Multiple matching replies are not authentication. Before new signing after restart, reconcile all unresolved intents and reserve their maximum exposure locally; replayed journal snapshots cannot undo the ledger's consumed sequence/cap state. If finalized success disappears, stop as an assumption breach; do not silently reset authority.

For the proposed laboratory experiment only, the scheduler provides an authenticated fixture checkpoint/outcome table and can deliberately corrupt observations. This is an explicit oracle, counted as an unimplemented real-network dependency. State models receive **no credit for solving light-client proofs or consensus** using it. A production non-execution proof, proof format/availability and checkpoint recovery policy remain open.

Revocation takes effect at included ordering. RotateGrant invalidates old grant versions without replenishing authority. RotateKey changes the owner's key epoch; older signed intents reject, while credit remains payable to the same principal under its new key. A removed delegate cannot sign new operations but may already have valid admitted ones; include-first wins. Rollback may restore pre-revocation authority on a nonfinal branch; clients must honor their declared finality policy. Offline physical actions cannot learn a new revoke instantaneously. Host compromise/journal erasure and root-key compromise need operational controls; no magical key-recovery service is credited.

## 5. Layer boundary

Consensus orders and authenticates ledger state under its own assumptions. Deterministic ledger/application validation enforces transfers, signatures, caps, replay and agreed settlement; these need not be hardcoded native opcodes. Delegation/escrow can be metered application logic if atomicity and independent verification hold. Discovery, negotiation, invoice/meter truth, robot dispatch, device attestation, local signing policy, journals, confidentiality and physical safety stay outside consensus. No oracle, relay, sequencer, custodian or watcher may be silently assumed; specify and charge it or mark the function unresolved.
