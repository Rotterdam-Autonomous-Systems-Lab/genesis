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
