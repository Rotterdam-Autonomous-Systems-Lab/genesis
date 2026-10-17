# Task 003A — Escrow evidence and remaining coverage

Date: 2026-10-17. Scope: Solidity escrow only. The [architecture](../architecture/EXPERIMENT_001_ARCHITECTURE.md) remains the behavioral specification; [ADR 0001](../adr/0001-experiment-001-architecture.md) is accepted only for the separately authorized local escrow component. No Python agents or end-to-end service transaction have been implemented.

## Local evidence

Pinned Foundry v1.0.0 and Solidity 0.8.28 built the escrow successfully on macOS x86_64. All **55 tests passed, zero failed/skipped**: 36 unit tests, 15 fuzz properties configured for 256 runs, and four stateful invariants with 128 runs x 64 calls each (8,192 calls per invariant, zero unexpected reverts). Some fuzz properties also exercise an initial dictionary case, so individual output may show 257 executions. See `contracts/test/` and `foundry.toml` for reproducible evidence rather than treating these counts as an audit.

Stateful tests compare liabilities, credits, deposits/withdrawals, immutable records, and terminal nonce states with an independent test-side accounting model. The handler targets six valid lifecycle actions and fails on unexpected reverts; dedicated adversarial tests check rejected calls, including each signed-field mutation, callbacks into every mutator, and transfer failure. Flat-field EIP-712 encoding checks cover all five message types independently of the contract's tuple encoder; they still share Solidity hashing machinery and are not the future Python interoperability vectors.

Local `forge fmt --check`, offline build/tests, dependency checks, Bash syntax checks, and actionlint v1.7.7 workflow validation passed. The loopback Anvil smoke test used zero generated accounts and queried only eth_chainId; no transactions or Anvil deployments were made. Foundry test-contract creation occurs only inside its in-memory VM. CI repeats build/tests and the smoke check on a fresh Ubuntu runner. Its result is an external check available on the pushed commit, not a claimed local result.

An initial run had 49 passing tests and one fixture failure: the zero-requester invalid-terms case lacked synthetic balance and could not reach contract validation. The fixture now funds the simulated sender before asserting rejection. No contract check or security assertion was weakened. Compilation emits one expected selfdestruct deprecation warning from the forced-ETH adversary only; the escrow has no selfdestruct.

The [initial CI run](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39054100038) rejected the first pin check before build/tests: the preinstalled macOS `1.0.0-stable` snapshot (`e144b820…`) differs from official release `v1.0.0` (`8692e926…`). The correction pins the official Git tag commit and reruns locally with that release installed under ignored internal/. The strict commit check and security tests are retained.

## Invariant-to-evidence map

“Contract tested” applies only to the stated contract property under the trusted local VM assumptions. No row asserts production security or complete enforcement of environmental/agent behavior.

| Invariant | Contract evidence / named test examples | Coverage boundary |
| --- | --- | --- |
| SI-01 authorization | `test_SuccessSettlementAndWithdrawal`, `testFuzz_WrongFundingSigners`, `testFuzz_WrongEvidenceSigners`, `test_CorrectResultWithoutAcceptanceRefunds` | Contract tested; independent agent signer ownership remains integration work. |
| SI-02 maximum principal | `test_CapEqualityAtMaximum`, `testFuzz_FixedServiceAndCaps`, `testFuzz_FundingValueAndCapRejections` | Contract tested; no aggregate wallet/gas cap is claimed. |
| SI-03 replay | Replay/existing-ID tests, `test_ConsumedNonceCannotBeReusedAfterRefund`, `invariant_ImmutableRecordsAndTerminalNonces` | Contract state replay tested; chain-reset/reorg monitoring remains environmental. |
| SI-04 expiry | `testFuzz_FundingExpiryBoundary`, `testFuzz_FundingDeadlineBoundary` | Contract -1/equality/+1 boundaries tested; timestamps remain trusted chain data. |
| SI-05 revocation | `test_RevokeBeforeFunding`, `test_FundBeforeRevocationObligationSurvivesExpiry`, `test_StrangerRevokesOnlyOwnNamespace` | Contract execution order and namespace tested; pending RPC transaction ordering is not simulated as public consensus. |
| SI-06 immutable terms | `testFuzz_MutatedAgreement`, record/model invariant | All ten signed Agreement fields tested; off-chain negotiation/parser not implemented. |
| SI-07 domain/type/run | Wrong-domain fuzz test, cross-chain/contract/run tests, purpose substitution and flat encodings | Contract tested; Python golden vectors and environment domain validation remain pending. |
| SI-08 participants/agreement | Authorization/Acceptance mutation tests, `test_CrossAgreementAcceptanceCannotReleaseSecondEscrow` | Contract tested; addresses do not establish real-world separate ownership. |
| SI-09 valid result | `test_WrongResultEvenWithBothValidSignatures`, max/zero operand tests, sum fuzz property | Contract arithmetic tested; provider effort/general computation is not proven. |
| SI-10 failure/timeout | Settlement/refund boundary tests and correct-result/no-Acceptance refund | Contract tested; communication failure and caller liveness remain integration assumptions. |
| SI-11 independent verification | Valid/wrong result and missing/wrong-domain Acceptance tests | Partial: contract checks consent plus sum; no Python verifier execution or independent agent evidence yet. |
| SI-12 caller authority | Unauthorized funding/settlement/refund/withdrawal tests, own revocation namespace | Contract tested; no relayer/admin bypass exists. |
| SI-13 refunds | Refund/withdraw tests, terminal-state tests, requester-veto path | Contract tested; no provider-cost compensation, automatic refund, or key recovery. |
| SI-14 conservation/reentrancy | Three withdrawal adversary tests and all four stateful invariants | Contract tested, including forced surplus and receiver failure; code has not been independently audited. |
| SI-15 no AI validity authority | Entire suite runs fixed arithmetic/signatures without model services; unsupported service rejected | Contract scope tested; Genesis consensus security is not implemented or evaluated. |
| SI-16 local-only environment | Constructor chain/run guards; zero-account loopback Anvil smoke script; CI has no fork/RPC/deployment command | Partial environmental check only; future agent endpoint/redirect/proxy/code-hash/key-lifecycle guards are absent. Chain ID is not proof of locality. |
| SI-17 retries and reconciliation | `test_RetryAfterRejectedFundingKeepsNonceReusable`, replay/terminal/failed-withdrawal tests | Partial: contract idempotence/rejection tested; ambiguous RPC outcomes, reorg/reset detection, serialized transaction nonce handling and reconnect logic await integration. |
| SI-18 bounded inputs/execution | uint64 ABI rejection, max inputs, supported-service rejection, hard cap/window checks | Partial: contract bounds tested; JSON limits, discovery limits, transport retries, agent transaction/gas/wall-time budgets await integration. |

## Review and unresolved concerns

No blocking specification contradiction was found. Task 003A explicitly authorizes this component and preservation of requester veto. A malicious requester can still refuse Acceptance after correct work, then refund; a compromised key can create new authorizations, and gas/aggregate wallet spend are not contract bounded. Shared-host/RPC control, EVM/compiler/library correctness and key secrecy remain assumptions. No independent audit, comprehensive dependency advisory review, agent interoperability result, public-chain finality guarantee, or network-security claim is made.

Before any Python work, separately authorize that task and retain the remaining SI-07/SI-11/SI-16–SI-18 integration checks. Before wider use, independently review this implementation, the pinned dependency/audit scope, and all residual threats. Production and public-network deployment remain outside scope.

## Task 003B — Independent-agent integration (2026-10-17)

The sections above preserve Task 003A's historical scope and pending work at that time. Task 003B separately authorizes and implements Python requester/provider integration without changing the escrow source or contract tests. See [fresh-checkout instructions and trust boundaries](../../sdk/python/README.md), [Python tests](../../tests/python/), and [dependency pins](../../DEPENDENCIES.md). A successful local EVM experiment does not validate a future Genesis consensus mechanism, native blockchain, permissionless discovery system, or final network architecture.

### Local evidence

All 55 existing Solidity tests passed again with the pinned toolchain. The Python suite has 30 tests: codec/signing/policy unit tests, live Python-to-Solidity interoperability/adversarial tests on temporary Anvil, and process-level integration scenarios. The successful process test performs two independent clean runs; another uses maximum uint64 operands. Separate provider/requester PIDs and addresses are asserted. Each process creates its own fresh signer in memory; no agent keys are supplied to or collected by the harness. Same-user processes are not a security sandbox against a malicious host.

The standalone end-to-end runner executed real signed funding, settlement, and withdrawal against the existing contract on temporary zero-account Anvil. Example local settlement transaction: `0xce656c7ed5117870a541681b646191f59f3e01d08a0cd9913c9ab44b58d4a810` (ephemeral chain, not a public explorer link). Result 18 for inputs 7 and 11; exact principal 10^12 synthetic wei; record Settled; no remaining escrow balance, locked principal, or credits. The run finished in about 1.71 seconds on the local host and all children stopped. This is a single fixture observation, not a performance benchmark. Fresh keys/run IDs intentionally change transaction hashes.

Initial process tests exposed a harness/client comparison mismatch between ABI-decoded bytes32 and wire hex strings. Normalizing their representation corrected the state check; no contract predicate or assertion was removed. Positive and adversarial paths were rerun. No false success result from that initial run is claimed.

### Additional invariant-to-evidence mapping

This supplements, rather than replaces, the contract evidence above. Named Python tests are under `tests/python/`; no row claims a proof or complete security review.

| Invariant | Task 003B named evidence | Scope / residual limit |
| --- | --- | --- |
| SI-01 | `test_success_separate_processes_and_two_clean_runs`, `test_result_signature_and_domains` | Separate signers and actual escrow flow; key control is not legal ownership or verifier execution proof. |
| SI-02 | `test_spending_above_cap`, success principal/accounting checks | Signed cap rejects overspend on-chain; gas and aggregate wallet spending remain separate. |
| SI-03 | `test_replay_consumed_nonce_new_agreement` | Existing record and reused nonce/new agreement reject without state changes; chain state remains trusted. |
| SI-04 | `test_funding_immediately_before_expiry`, `test_expired_authorization_equality_and_plus_one` | Actual execution timestamps checked at -1/equality/+1; Solidity tests also cover funding/settlement deadlines. |
| SI-05 | Existing Solidity revocation/race tests retained | Full agent-mediated revocation lifecycle and transport race matrix not added. |
| SI-06 | `test_agreement_tampering_rejected_before_countersigning`, `test_altered_signed_terms` | Agent policy/signatures reject altered terms; exhaustive contract field mutation tests retained. |
| SI-07 | `test_all_five_python_solidity_digest_vectors`, `test_fixed_public_golden_vectors`, `test_result_signature_and_domains`, `test_signature_encoding_and_run_rejected` | All five types match deployed Solidity hashes; static public vectors protect encoding regressions. Exhaustive Python cross-type/domain/run mutation matrix remains pending. |
| SI-08 | `test_wrong_participant_and_agreement_binding`, invalid result/agreement unit checks | Authorization and Acceptance binding checked; no real-world identity claim. |
| SI-09 | `test_invalid_result_rejected_and_refunded`, `test_invalid_result_never_creates_acceptance`, `test_maximum_operands` | Invalid B-signed result creates no Acceptance; on-chain arithmetic remains an independent payment predicate. |
| SI-10 | `test_provider_process_termination`, `test_requester_veto_valid_work_timeout_refund` | Missing service/refusal cause no payment and chain-deadline refund. Liveness requires A and chain availability. |
| SI-11 | Success and invalid-result process tests, requester-only `result_acceptance` unit test | Requester recomputation now executed separately from B's computation; signatures alone still do not prove execution. |
| SI-12 | Separate-process direct callers and existing unauthorized-caller Solidity tests | No relayer or unlocked-account signing bypass; shared privileged RPC remains trusted. |
| SI-13 | `test_refund_boundary_and_duplicate`, three process rejection/refund scenarios | Exact requester refund/withdrawal and zero provider payout; no provider-cost compensation. |
| SI-14 | Final accounting assertions on every process scenario; all original stateful/reentrancy tests | No contract redesign; Python does not replace EVM callback/adversary tests. |
| SI-15 | Fixed-service end-to-end runs, strict unknown-field/schema tests | No AI calls or executable wire payloads; no Genesis consensus result. |
| SI-16 | `test_remote_rpc_rejected_before_connection`, `test_proxy_and_redirect_refused`, `test_changed_deployment_refused` | Local-only guards, zero-account node, fresh process-owned signers and redacted evidence; host/dependency compromise out of scope. |
| SI-17 | `test_dropped_send_response_reconciles_exact_funding`, `test_rpc_interruption_aborts_without_new_authorization`, `test_reorg_after_funding_is_inconclusive` | Exact-hash reconciliation, no fresh authorization retry, reverted transaction handling and canonical evidence checks. RPC faults are injected at the client boundary, not a comprehensive network chaos suite. |
| SI-18 | Codec/transport/discovery bounds tests, `test_transaction_budget`, `test_maximum_operands`, all process cleanup assertions | Fixed one-agreement run, message and transaction limits, timeouts and cleanup; no OS resource isolation or malicious-host DoS protection. |

### Explicit pending Task 003C candidates (not authorized here)

- Exhaustive Python signature/domain/type/run/field mutation and independently sourced vector review across all five types; full agent-driven unused-nonce revocation and ordering scenarios.
- A real local RPC fault proxy/process-level network chaos suite: reordered/dropped transport messages, pending transaction replacement/rebroadcast, resets during every lifecycle step, outage during settlement/withdrawal, and successful recovery after reconnection. Current injected lost-send/outage and snapshot-reorg tests cover specific cases only; unresolved delivery aborts rather than automatically creating a new intent.
- Broader property-based parser/spam and time/gas-budget boundary matrices, process failure before funding, host SIGKILL/restart cleanup analysis, and systematic artifact/key-leak instrumentation. No secure memory erasure or adversarial same-user process isolation is claimed.
- Independent source/dependency/advisory review and audit. No production-key custody, global discovery, public-chain finality, general service verification, fair exchange, Sybil resistance, or new consensus implementation is present.

Requester veto remains unresolved and deliberately preserved: an honest provider may do correct work yet receive no payment if A withholds Acceptance. These residual research questions do not authorize redesign or Task 003C implementation.

## Task 003C — Adversarial validation and acceptance gate (2026-10-17)

The Task 003A/003B sections above remain historical evidence. The current [security review](EXPERIMENT_001_SECURITY_REVIEW.md) records threat-driven methodology, seven scoped findings/mitigations, dependency/CI review, assessment of all 18 invariants, and **CONDITIONAL PASS** conditions. No contract logic, signature schema, deadline rule, cap, or requester-veto behavior changed.

The expanded suite passes **58 Solidity tests** (including all original 55, 15 fuzz properties, and four stateful invariants still at 128 x 64 calls) and **54 Python tests** (all original 30 plus 24 new adversarial methods with bounded mutation/process subcases). New contract cases cover concurrent mixed settlement/refund, price extremes, and unauthorized copied settlement calldata. New Python cases are in [test_adversarial.py](../../tests/python/test_adversarial.py), with a temporary [RPC fault proxy](../../tests/python/rpc_faults.py). They cover all five types' signed fields/domains/encodings, FIFO/publication races, forged/incomplete provider evidence, loss before/after broadcast, retry latching, receipt/event mutation, actual process crashes, malformed/oversized/truncated evidence, workflow deadline expiry and snapshot/revert before Acceptance.

Implementation fixes reject nonregular transport without blocking, atomically preserve the first published message, require actual canonical settlement and withdrawal evidence, disable unused CCIP Read, latch unresolved transaction outcomes, abort immediately on chain uncertainty, and clean up interrupted fixture startup. The review distinguishes source-traced component reporting gaps from financial exploits; no unauthorized contract payment was confirmed. Formatting of the reviewed Python modules also improves readability without changing protocol semantics.

Remaining gaps are listed in the review rather than silently considered complete: lifecycle-wide network/message schedules and transaction replacement/rebroadcast, hard host failure/restart, comprehensive key-leak/resource-limit instrumentation, and independent compiler/dependency/source review. Key-loss crashes may end inconclusive with synthetic principal abandoned on chain reset; they are not claimed successful refunds. Requester veto and all long-term network/consensus questions remain unresolved. This review does not authorize Experiment 002 or a final research report.
