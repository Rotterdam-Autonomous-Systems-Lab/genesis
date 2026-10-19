# Task 020 — restricted balance-pool spending policy

This is a bounded model policy, not adoption of a native script/VM or conventional owner-signature coin design. The frozen logical corpus, signed inputs, deadlines, fees and caps remain unchanged. Task019's old outputs and counterexample remain historical evidence.

## Policy and trust boundary

Each balance output is explicitly locked to `script:balance-pool-v1:<owner>`. The typed ledger first authenticates the current actor's key, domain/epoch/sequence, target role and delegated scope, and reserves principal/fee authority. It then proposes successors. A separate pure covenant checks every balance input and successor before atomic consumption: exactly one current pool per touched owner, exactly one continuing output for that same owner/script, integer uint64 value bound to datum, and the **exact** authorized delta. Unrelated owner inputs, missing successors, owner/script rewrites, debit/over-credit and merging are rejected.

The authenticated operation authorizes these deltas, independently reconstructed again by the harness from signed inputs and native transaction records:

- All non-delegated admitted outcomes debit the actor's fee of1; rejected admission/duplicate/stale wrappers consume nothing.
- Successful direct Transfer debits actor principal; delegated Transfer debits the grant reserve instead. Only the named recipient receives that amount.
- Grant creation debits the root's P+F; direct Fund debits its price. Delegated Fund uses reserved grant principal.
- Collect credits only the stored credit owner; ReturnReserve credits only the stored root with remaining P+F. Semantic reverts transfer no principal.

A recipient signature is unnecessary for a top-up because the output is script-controlled: its full prior claim must continue unchanged plus the exact incoming amount. This grants no permission to debit a third party, merge different recipients or spend grants/credits/registries. Output/input IDs, complete spent attribution and owner identity remain available. Coalescing preserves aggregate spendable ownership but serializes incoming payments; it does not preserve independent input-level concurrency. No ordinary UTXO independence advantage is credited to this profile.

The public model entrypoint accepts a signed logical operation and exact wrapper. It does **not** accept arbitrary general-purpose transactions/programs. Typed grant/escrow/replay transition checks remain part of the trusted modeled rules. The covenant's arbitrary-successor adversarial tests therefore establish only its restricted balance conditions, not correctness of an unspecified general script engine. The independent harness imports no covenant and checks exact frozen projections, invariants and native pool deltas separately.

## References, retries and alternatives

Wrappers bind the exact intent hash plus sorted, unique dependencies encoded as full32-byte base64url hashes (no truncation). A delegated Transfer/Fund does not reference unused delegate coin state; it still references actor epoch/replay, grant, root epoch and recipient/agreement state where applicable. Stale actual references reject before fee admission. Rebuild requires the same signed intent and existing final-outcome/fenced-absence recovery rules; neither spent references nor ordinary RPC absence authorize a new intent.

A [non-coalesced two-payment control](../../research/reports/task020/append_only_control.py) retains two separate recipient claims and refuses a different signer consuming either. It isolates the alternative's zero recipient-input top-up requirement. It is **not a fourth full candidate or benchmark**; a complete append-only coin-selection/consolidation adapter would be a separately reviewed representation factor. The original Task019 source/evidence is also retained. No fourth-model runs or extra full-model stress sweeps are introduced within this task's three-model scope.

Correctness coverage includes all frozen authority/accounting/recovery cases, plus arbitrary balance-successor mutations, current/stale references and duplicate top-ups. Crash recovery still concerns the fsynced client journal and fixture finality/fencing oracle; validator power-loss durability and real native proofs remain untested.
