# Native L1 comparative research fixtures — v1

Task 018 freezes public synthetic inputs and expected projections; **no candidate state model is implemented or tested here**. All vectors apply equally to accounts, objects and extended UTXO. Use the [review](../../../docs/architecture/NATIVE_L1_SPEC_REVIEW.md), [adapter](../../../docs/architecture/NATIVE_L1_ADAPTER.md) and [measurement plan](../../../docs/architecture/NATIVE_L1_MEASUREMENTS.md).

## Reproduction

From repository root, using the existing hash-locked Python environment:

```sh
internal/agent-venv/bin/python research/fixtures/native_l1/validate.py
internal/agent-venv/bin/python -m unittest discover -s tests/architecture -v
```

If needed, create that environment with `python3 -m venv internal/agent-venv` and install `sdk/python/requirements.lock` using `pip install --only-binary=:all: --require-hashes -r sdk/python/requirements.lock`. No new dependency; Ed25519 verification uses the already locked PyCryptodome. See [dependency policy](../../../DEPENDENCIES.md). CI runs the same unittest command.

| Artifact | Purpose |
| --- | --- |
| `v1/corpus.json` | 21 ordered vectors, 32 signed logical intents, signed terms, genesis header, public actor keys, initial states, full expected ledger/client snapshots and observations. |
| `v1/schema.json` | Strict data shape and bounds; unknown fields rejected. Validator implements only its explicit JSON Schema subset, not a general validator. |
| `v1/codec_vectors.json` | Independent RFC 8949 CBOR examples and RFC 8032 public signature test. |
| `v1/stress_plan.json` | Nine deterministic configurations; Task 019 expands/fixes signed inputs once before timing. No stress execution is claimed. |
| `v1/checksums.sha256`, `v1/corpus.sha256` | SHA-256 artifact identities. Validation checks both; version changes require reviewed new artifacts. |
| `validate.py` | Data/schema, bytes, signatures, accounting identities and references only; no transition/admission interpreter. |

Portable wire values use arrays, unsigned integers and `{"bytes":"lowercasehex"}`; this is a JSON transport for the ASR CBOR profile, not a JSON signing format. Full encoded unsigned-intent hex/digests and signatures are frozen. Signatures cover the 32-byte digest, without an extra hash. Public key/signature generation occurred before freeze; no retained key or generator is required to replay static bytes. No private key material belongs in this corpus. Independent examples: [RFC 8949 Appendix A](https://www.rfc-editor.org/rfc/rfc8949.html#appendix-A), [RFC 8032 §7.1](https://www.rfc-editor.org/rfc/rfc8032.html#section-7.1). Signature verification API: [PyCryptodome EdDSA](https://www.pycryptodome.org/src/signature/eddsa).

## Canonical vector index

| ID | Scope |
| --- | --- |
| V01 | Shared principal race and exact remainder |
| V02 | Independent fee/principal boundary and ceiling |
| V03 | Logical duplicate and conflicting sequence |
| V04 | Grant authorization replay cannot reset reserves |
| V05 | Revoke before spend |
| V06 | Spend before revoke; reserve return preserves counters |
| V07 | Scope/key/domain/epoch and expiry equality |
| V08 | Lost inclusion reply, crash and safe reconciliation |
| V09 | Fenced non-admission and bounded same-intent retry |
| V10 | Unavailable evidence blocks new spending |
| V11 | Contradictory RPC observations latch halt |
| V12 | Correct work settles/collects without requester return |
| V13 | Wrong work and unauthorized Claim |
| V14 | Claim equality, refund and no renewed grant authority |
| V15 | Conflicting credit owner/terminal observations |
| V16 | Prefinal reorganization and retained uncertainty |
| V17 | Contradictory purported finality |
| V18 | Grant version rotation without renewed caps |
| V19 | Direct principal plus fee solvency |
| V20 | Shared fee exhaustion with principal remaining |
| V21 | Revocation cannot cancel funded work |

Each vector names workloads, invariants, recovery expectation, network/finality assumptions and all three candidates. Initial balances/caps override Task 017 illustrative defaults explicitly; no mint/top-up occurs. V14 uses grant expiry40 versus claim20 to avoid masking renewed-cap defects with expiry. Seeded Funded states account for their locked price and prior funding fee/consumed intent; seeded grants are genesis allocations, not unpaid runtime operations.

Observations reference exact `(vector,step)` ledger snapshots; `patch` fields deliberately corrupt that base, never mutate canonical ledger. `final_pay10` can serve another trace with the same ledger snapshot even when local client histories/ticks differ. Fenced absence is a trusted scheduler delivery-epoch promise, not a production RPC proof. `include` tests ledger semantics; only explicit client events exercise the journal. Expected idle client fields in ledger-only vectors make no autonomous signing assertion.

Changing a signed input requires a new reviewed version and regenerated signatures/expectations; changing hashes to conceal mismatch is forbidden. Keep the original v1 failures and publish any corrected successor. Candidate-specific wrappers and expanded stress manifests must be frozen with source/dependency identities in Task 019 before collecting measurements. Wider permutation, key-rotation execution, parser/fund-boundary and device-policy coverage remains explicitly outside this minimal core; it is not asserted passed.
