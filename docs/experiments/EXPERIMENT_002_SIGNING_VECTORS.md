# Experiment 002 Public Signing and State Vectors

**2026-10-18 — Normative proposal fixtures; not executed contract-test evidence.** See the [final specification](EXPERIMENT_002_FINAL_SPEC.md) and [JSON fixture](EXPERIMENT_002_SIGNING_VECTORS.json).

## Format and provenance

The JSON contains exact public addresses, domain, ordered EIP-712 schemas, integer-string payloads, domain separators, struct hashes, final digests and 65-byte signatures. Signers were generated once in a local ephemeral process and discarded; **no signing keys, wallet files or raw transactions are included**. No need to recreate private keys: recover and verify the frozen public signatures. These are synthetic verification identities, not real wallets or funded chain addresses. Future end-to-end runs create their own identities and never import these identities as live signers.

Generation used existing eth-account 0.13.7, eth-abi 6.0.0 and eth-utils 6.0.0. Explicit ABI type/field hashing was cross-checked against eth-account's domain/struct hashes and signed-message digest; signature recovery matched each public signer. This reduces encoding mistakes but shares cryptographic primitives and is not independent audit or formal proof. No package was installed or adopted for Experiment 002. JSON is public research data, not escrow/agent implementation.

Reproduction of this evidence is verification of the fixed data, not regeneration of identical keys/signatures. The type hash is keccak256 of the exact ordered type string; dynamic domain strings hash their UTF-8 contents; all other struct fields encode as standard ABI scalars. The full digest is keccak256 of `0x1901 || domainSeparator || structHash`. Use standard maintained libraries. Recompute from typedData, verify expected hashes, then recover the required signer; never trust a stored digest after mutating the payload. Solidity unit tests may impersonate fixture public callers while verifying real public signatures; no funded private key is necessary.

## Signed fixtures

| ID | Exact distinguishing data | Expected result |
| --- | --- | --- |
| V01-nominal | x=7, y=11, value=18; price=10^12, cap=2*10^12; nonce=0; expiresAt=fundBefore=1120, claimBefore=1300. | Eligible for funding/claim at valid timestamps, not at expiry. |
| V02-max-operands | x=y=18446744073709551615, value=36893488147419103230, nonce=1, different salt. | Valid uint64 bounds and uint256 result. |
| V03-zero-price | Correct signatures for price=0, nonce=2. | Semantic rejection at funding; None/Unused preserved. |
| V04-price-over-cap | Correct signatures for price=2000000000001 and cap=2000000000000, nonce=3. | Funding rejects cap violation despite signature validity. |
| V05-wrong-policy | Correct signatures for unsupported policyId=0x77 repeated 32 bytes, nonce=4. | Funding rejects unsupported semantics. |
| V06-late-funding | fundBefore=expiresAt=1299, claimBefore=1300, nonce=5. | Funding at 1298 permitted; no guaranteed time for claim; at 1299 funding rejects. |
| V07-repeated-work | Same x/y/value as V01; different salt/agreement and nonce=6. | A separately authorized payment is allowed; no work-uniqueness/mining inference. |

Additional artifacts: signed B advertisement; B-signed incorrect value **19** for the nominal agreement; dual-signed nominal Terms under chain ID **31338**; dual-signed nominal Terms under verifyingContract **0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa**. Their signatures are valid under their own payload/domain, but the intended deployment rejects the mismatched domain or false result. No unverified “evidence” flag can override this.

M01–M05 retain the original signatures while altering price, Authorization.agreementId, provider, zeroing the A signature or truncating it to 64 bytes. They are expected rejections, not freshly consented terms. The fixture mutation path specifies what changes; original cached hashes must be recomputed, not reused. Also require the full T05/T06 field/domain/encoding matrix, including high-s/v/compact/wrong-run tests, even where not materialized as separate JSON artifacts.

## Concrete transition/timestamp cases

Each independent row starts with a fresh fixture unless an action sequence is stated. t denotes canonical block time; balance effects exclude gas. None records and Unused nonces are zero-valued initially.

| Case | Action / exact time | Expected protocol state/accounting |
| --- | --- | --- |
| S01 | A funds V01 with exact 10^12 at t=1119. | Funded; nonce 0 Consumed; locked=10^12; credits=0. |
| S02 | A funds V01 at t=1120 or 1121. | Revert; None; nonce 0 Unused; no principal received. |
| S03 | After S01, B claims valid 18 at t=1299. | Settled; locked=0; B credit=10^12; result=18; no A post-funding action. |
| S04 | After S01, B claims at t=1300 or 1301. | Revert; Funded remains, no B credit; A refund enabled. |
| S05 | After S01, A refunds at t=1299. | Revert; Funded/locked unchanged. |
| S06 | After S01, A refunds at t=1300. | Refunded; locked=0; A credit=10^12; authority still Consumed. |
| S07 | After S01, no caller; advance time to 1301. | Still Funded/locked=10^12; no automatic refund/withdrawal. |
| S08 | Revoke A nonce 0 then try V01 funding before 1120. | Revoked; no funding or nonce reset. |
| S09 | Fund V01 then revoke nonce 0. | Revoke rejects; Funded/Consumed preserved; timely B claim still eligible. |
| S10 | Fund V01 twice, or try its same consumed nonce for another digest. | Second successful obligation impossible; principal/credit unchanged on rejection. |
| S11 | Settle V01, then claim again or refund. | Both reject; no duplicate credit or terminal transition. |
| S12 | Refund V01, then claim or refund again. | Both reject, including with original valid signatures; authority not restored. |
| S13 | B submits signed invalid value 19 before 1300 after S01. | Reject despite valid B signature; Funded and locked principal unchanged. |
| S14 | Third party submits B's valid claim, A-only fund/refund, or withdrawal of peer credit. | Reject unauthorized transition or no own credit; no payment redirection. |
| S15 | Exact-price, zero/under/overpayment; cap price-1/exact/+1 in separately signed Terms/Auth. | Value mismatch rejects; cap below price rejects; exact/above cap permits only agreed price, never unused allowance. |
| S16 | B withdraws after S03, then withdraws again. | First transfers exactly 10^12 and clears credit; second rejects. Transfer failure restores credit atomically. |
| S17 | V01 and V07 both validly fund/settle with separate nonces. | Two independently authorized obligations/payments allowed; aggregate liabilities conserved. |
| S18 | First fund attempt has insufficient balance for value plus gas. | RPC pre-execution rejection or canonical revert must be classified; no invented receipt/state transition. An ambiguous response is not assumed to be a rejection. |
| S19 | At t=1300 order A refund before B claim, or B claim before A refund. | B claim always invalid at equality; only included valid A refund succeeds. At t=1299 inverse eligibility holds. |

Mutations, wrong-domain proofs and correctly signed semantic-invalid terms must be rejected with unchanged escrow state. Final tests must also cover maxAmount>10^15, x/y=2^64, uint256 overflow encoding, expiry ordering violations, refund/withdraw reentrancy, forced surplus and ambiguous sends. Gas/transaction nonce behavior is distinct from Authorization nonce state. For an insufficient-funds case, no fixed wallet balance/gas price is fabricated until the B-FEE policy is resolved.

## Acceptance evidence boundary

Local fixture validation checks syntax, scalar widths, hashes and signer recovery. Contract/E2E acceptance requires independent Solidity/Python checks and all T01–T20, plus canonical accounting/receipt evidence. Future code cannot claim these scenarios pass merely because this specification lists expected outcomes. Frozen fixtures support interoperability; changing them requires a reviewed diff and updated provenance.
