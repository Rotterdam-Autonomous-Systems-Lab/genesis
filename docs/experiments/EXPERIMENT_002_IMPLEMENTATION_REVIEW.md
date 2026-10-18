# Experiment 002 — Task 009 Partial Implementation and Blocking Review

**2026-10-18 — Acceptance gate: FAIL / implementation BLOCKED.** The accepted design remains unchanged. Task 009 separately authorized local implementation, but a required fee-evidence assumption failed on the pinned Anvil baseline. Implementation stopped rather than changing dependencies, trusting contradictory receipts, increasing caps or weakening tests. This is a project-assisted review, not an independent audit or formal security assurance.

## Completed and published work

- Isolated [Solidity escrow](../../contracts/src/Experiment002Escrow.sol), with the exact Terms/Authorization/Claim types, separate EIP-712 domain, fixed service/policy, nonce consumption/revocation, upfront consent, deterministic addition, strict deadlines, exclusive refund and own-credit guarded withdrawals. No Experiment 001 code, tests, signatures or published evidence changed.
- [Contract tests](../../contracts/test/Experiment002Escrow.t.sol): positive and negative transitions; every Terms/Authorization/Claim field mutated without resigning; invalid signatures, wrong domain/chain/contract/identity; cap/value/expiry/replay/revocation; exact deadline boundaries; zero/maximum operands; concurrent repeated-work accounting; forced surplus; test-only callback/rejected-transfer harness. Two new stateful invariants use an independent liability/owner model.
- [Frozen-vector Solidity tests](../../contracts/test/Experiment002Vectors.t.sol): seven public fixtures, 21 typed digests and 28 signatures, including correctly signed zero-price/over-cap/wrong-policy rejections. Fixed-address test impersonation uses public signatures, never recovered private keys. The unchanged compatibility probe additionally covers 25 digests/34 public signatures using Cast and Python/EVM recovery.
- A bounded [fee-receipt reproducer](../../research/compatibility/experiment002/check_anvil_fee_receipt.py) and [observed evidence](../../research/compatibility/experiment002/task009-fee-receipt-evidence.json). The reproducer exits **2** for the contradiction; this is a blocking observation, not a passing acceptance test.

The partial agent/signer/runner draft and its tests are retained under ignored `internal/task009/unpublished/`, not released as an accepted or complete workflow. Before stopping, preliminary separate-process runs exercised settlement/refund/offline/crash controls. A draft Python suite ran 36 test methods: 35 completed successfully and one fee-boundary method had two failing subtests. These are development observations, not a published reproducible agent milestone. No assertions were weakened to turn that result green. Future work must review/retest that draft, not assume it is ready.

## B-ANVIL-FEE-EVIDENCE — confirmed blocker

**Severity: High for acceptance/evidence integrity; no demonstrated excess wallet debit or unauthorized escrow payout.** Dependency compatibility and fee-reconciliation readiness are reopened. B-FEE's finite principal/attempt/reservation policy remains specified; its complete implementation acceptance is blocked. ADR 0002 remains Accepted for bounded local design, not experimentally accepted.

Reproduction uses Foundry/Anvil v1.0.0 commit `8692e926198056d0228c1e166b1b6c34a5bed66c`, unchanged compiler/libraries/lock, chain 31337, no fork, fresh ephemeral in-memory keys and synthetic balances. One permitted deployment and one requester `revokeUnused(9009)` transaction; no principal transfer in the latter, no top-ups. The trusted test sets the next block base fee to 3 gwei and mines it; the transaction block subsequently has 2.625 gwei base fee. This deliberate fault schedule is not public-network pricing evidence.

| Observation | Synthetic wei or gas |
| --- | --- |
| Signed gas limit / max fee / max priority fee | 2,000,000 / 3,000,000,000 / 1,000,000,000 |
| Transaction block base fee | 2,625,000,000 |
| Canonical receipt gasUsed | 48,076 |
| Expected EIP-1559 effective price: min(maxFee, baseFee + priority) | 3,000,000,000 |
| Canonical receipt effectiveGasPrice | **3,625,000,000** |
| Actual requester wallet debit, value=0 | **144,228,000,000,000** |
| Receipt-derived fee | **174,275,500,000,000** |
| Worst-case authorized reservation | 6,000,000,000,000,000 |

The actual debit equals gasUsed times the signed 3 gwei cap; it remains within the reservation. The receipt's effectiveGasPrice exceeds that cap and disagrees with the debit. Thus this is **not evidence that the wallet was charged above its cap**. It is a reproducible contradiction in required canonical fee evidence on this fixture. The draft signer detected it and latched an inconclusive stop. Its subsequent fee-boundary subtest could not send because that uncertainty remained latched, as intended.

The normative [final specification](EXPERIMENT_002_FINAL_SPEC.md) and [cost model](EXPERIMENT_002_BOUNDED_COST_MODEL.md) require canonical gasUsed/effectiveGasPrice reconciliation and all fee-boundary controls. Silently replacing the receipt value with a locally calculated value, ignoring the contradiction, raising fee limits or upgrading the pinned node would change the accepted evidence/dependency assumptions. None was done. The root cause has not been independently attributed upstream; the observed trigger is the pinned local node with controlled base-fee manipulation.

## Reproduce without agent implementation

Install the existing checksum/hash-pinned dependencies using [DEPENDENCIES.md](../../DEPENDENCIES.md) and the [Python instructions](../../sdk/python/README.md). Build before Python/probe execution; do not run a forced rebuild concurrently with artifact consumers.

```sh
scripts/check-toolchain.sh
scripts/check-dependencies.sh
forge fmt --check
forge build --offline
forge test --offline -v
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
internal/agent-venv/bin/python research/compatibility/experiment002/check_vectors.py
internal/agent-venv/bin/python research/compatibility/experiment002/check_fee_bounds.py
internal/agent-venv/bin/python research/compatibility/experiment002/check_anvil_fee_receipt.py
```

Foundry must be on PATH (locally, `export PATH="$PWD/internal/tools/foundry:$PATH"`). The last command intentionally returns 2 when the blocker reproduces. It prints public numeric evidence only and stops/reaps its local node in `finally`. A different outcome does not automatically clear the blocker; retain exact versions, receipts and wallet accounting for review. No complete Experiment 002 runner is published; the unchanged `scripts/run-experiment-001.sh` still reproduces the control.

## Test and gas evidence

Local Solidity: **86 passed, 0 failed, 0 skipped** = original 58 + new 28 (18 unit/fuzz, 7 frozen-vector, 1 callback, 2 stateful). Original fuzz/stateful budgets remain unchanged; new fuzz tests run 256 each, new stateful properties 128 runs x 64 calls = 8,192 calls each, zero unexpected reverts. This is bounded test evidence, not exhaustive exploration.

Local Experiment 001 Python regression: **54 passed**. These are the original controls, not 54 Experiment 002 agent tests. Vendored hash checks, pinned toolchain checks, `pip check`, formatting, 25-digest/34-signature compatibility and 20 fee-arithmetic cases pass. Final published CI exercises the original workflow plus automatically discovered new Solidity tests; it does **not** establish Experiment 002 agent, fee-boundary or end-to-end acceptance. Inspect Actions for the publication commit rather than treating prior runs as new evidence.

Deployment with an actual signed 2,000,000-gas transaction used **1,632,623 gas** in the local diagnostic. Preliminary unpublished workflow observations were fund 326,272, claim 120,983 and withdraw 35,928 gas for one nominal run. They are not worst-case guarantees or production benchmarks. Acceptance remains blocked despite these observed values being below the ceiling. The public reproducer independently verifies the deployment and the fee-revocation path; full per-scenario gas/resource evidence must be regenerated by a reviewed integrated workflow.

## Security property and scenario disposition

| Properties / scenarios | Published evidence and remaining gate |
| --- | --- |
| P2-01/02/03/04/05/06/07/08/09/10 | Contract tests cover authority/caps/replay/expiry/revocation/terms/domain/parties/result/callers. Python interoperation/peer-message workflow acceptance remains pending. |
| P2-11/12 | Contract boundary, terminal exclusivity, no-actor state, liabilities, credits, callbacks and repeated-work tests. Agent-driven recovery and exact integrated withdrawals need published evidence. |
| P2-13 | Contract settlement requires no post-funding A signature; valid B claim succeeds. Separate-process offline/refusal controls remain unpublished and must be repeated. |
| P2-14 | **BLOCKED:** canonical fee receipt conflicts with wallet debit. Full ambiguous-send/reorg/event/state recovery evidence remains pending. |
| P2-15/16 | Diagnostic uses local-only transport, pinned Anvil, synthetic keys/balances and cleanup. Complete agent budget/runtime/RSS/no-top-up/isolation controls remain pending. |
| T01–T03 | Contract baseline exists; mandatory two-fresh-run, requester-refusal/offline integrated acceptance pending. |
| T04–T11 | Contract negative/binding/deadline/accounting tests supplied; required complete cross-component vectors/transport and actor matrix remain acceptance work. |
| T12–T19 | Fee contradiction blocks accepted recovery/cost evidence. Disclosure/no-caller/late-funding limitations demonstrated in contract tests, not claimed as complete integrated coverage. |
| T20 | Contract pays separately authorized repeated inputs under distinct digests/nonces; this supplies no unique-work, mining, Sybil or independent-ownership guarantee. |

All 18 Experiment 001 invariants and published requester-veto limitation retain their original assessment. P2 properties are a separate policy; no claim that Experiment 002 inherits the post-result Acceptance invariant. Missing mandatory integration evidence and the fee contradiction prevent PASS or CONDITIONAL PASS for Task 009.

## Source/dependency review and limits

New production Solidity uses only the existing EIP712/ECDSA/non-transient ReentrancyGuard source closure, fixed structs/mappings and explicit reverts. No recursion, transient storage, custom optimizer flags, user storage arrays/manual slots, byte-element deletion, new assembly or dependency introduced. Test-only receiver credit seeding reaches withdrawal defenses without introducing supported contract-wallet signing or an escrow admin. Forced-surplus tests intentionally use deprecated selfdestruct; this is a test helper, not production logic.

Compiler, Python, CCIP-disabled Web3 and installer/supply-chain residual risks from [Task 008](EXPERIMENT_002_BLOCKER_RESOLUTION.md) remain. No upgrades, workflow permissions, production credentials or public deployments occurred. The existing read-only, immutable-action-pinned CI was left intact. Same-host keys/processes do not establish separate ownership or hostile-OS isolation; a trusted host/RPC can defeat the fixture. Public results, censorship, timestamp/inclusion ordering, absent actors and key loss still prevent strong fairness. EVM/Anvil results validate neither Genesis's future independent L1, consensus, native asset nor organic adoption.

## Required review before resuming

1. Independently reproduce the pinned-node receipt/debit contradiction and identify its scope/root cause.
2. Review an explicit resolution: a separately tested/pinned corrected node, or a revised independently justified fee-evidence policy. No selection is made here; recheck dependencies and reproducibility before accepting either.
3. Reopen and resolve dependency/fee-evidence readiness through the ADR/register, then separately resume Task 009 implementation. Retest the partial Solidity and unpublished agent draft against all T01–T20, P2 properties, cost/resource cases and unchanged Experiment 001 controls.

The recommended next task is this bounded compatibility/evidence review. No Experiment 003, bootstrap experiment, production system or token is authorized.
