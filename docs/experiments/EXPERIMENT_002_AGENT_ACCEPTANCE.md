# Experiment 002 agent integration and security acceptance — Task 012

**Task 013 review notice:** [Adversarial review](EXPERIMENT_002_INDEPENDENT_REVIEW.md) reproduces the narrow no-second-signature result but identifies unresolved credit-owner and RPC re-read validation defects, plus a wall-deadline coverage gap. **Security/evidence closure is BLOCKED pending remediation.** The Task 012 CONDITIONAL PASS and measurements below are preserved historically; they do not establish complete mandatory P2-14/T12/T16 fault detection. [Task 012 CI passed](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39137210473); green regressions alone do not resolve the findings.

**2026-10-18 — CONDITIONAL PASS for the bounded local experiment, conditional on the publication commit's required CI.** This supersedes the historical integration-blocked status after Task 011's [passing compatibility CI](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/actions/runs/39136054716). The narrowed conditional-collectability question is tested; general fair exchange remains unresolved. A failing publication CI reopens acceptance. This is an internal engineering review, not an independent audit, formal proof or production assurance.

## Scope, implementation and unchanged authority

[Specification](EXPERIMENT_002_FINAL_SPEC.md), [ADR 0002](../adr/0002-experiment-002-fair-exchange.md) and [ADR 0005](../adr/0005-experiment-002-corrected-anvil-baseline.md) govern this work. Existing [Solidity escrow](../../contracts/src/Experiment002Escrow.sol), compiler/libraries, frozen signatures, price/authorization caps and fee model are unchanged. [Separate Python agents](../../sdk/python/genesis_experiment002/README.md) complete the previously paused integration; [runner](../../sdk/python/genesis_experiment002/runner.py) deploys locally and independently audits outcomes. No MASTER_PLAN change, native asset, consensus, public deployment, real funds or autonomous discovery implementation.

A signs Terms and bounded Authorization before funding. B signs Advertisement, identical Terms and Claim. The fixed on-chain sum checker accepts only the bound correct result, intended B caller and timely inclusion. There is no Acceptance schema or post-funding A signature. Online A recomputes independently; offline A is not falsely credited with verification. Distinct PIDs/addresses and process-owned ephemeral keys demonstrate software-process separation under a trusted host, not independent ownership or OS security isolation.

Signer policy charges conservative reservations before transaction signing, including reverts/ambiguous sends; keeps closing slots; rejects unexpected final calldata/nonce/target/fees; binds retries to one exact principal intent. Unknown delivery latches the signer. Canonical receipt, block membership, event, immutable record, nonce, exact result, credits and withdrawal are checked separately. The supervisor audits all included transactions, even when an agent dies before producing its final report.

The fee check compares receipt price with integer `min(maxFeePerGas, baseFeePerGas + maxPriorityFeePerGas)`, transaction gasPrice and block-receipt price. Actual sender debit is reconciled after excluding successful outgoing principal and including successful withdrawals; reverts transfer no principal. Whole-run initial/final wallet arithmetic and contract liabilities are independent checks. One transaction per block and no top-ups are explicit closed-fixture assumptions; other ledgers/concurrent spending require separate evidence rules. Task 011's unchanged opcode-witness and negative-control checks remain in CI; the escrow itself has no added GASPRICE witness or altered payment semantics.

## Evidence and reproducibility

Run the exact [agent commands](../../sdk/python/genesis_experiment002/README.md), [existing dependency checks](../../DEPENDENCIES.md) and read-only [CI workflow](../../.github/workflows/foundry.yml). Build before tests; do not rebuild concurrently with artifact consumers. Unit/integration commands:

```sh
forge fmt --check
forge build --offline
forge test --offline -v
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/experiment002 -v
scripts/run-experiment-002.sh
```

The final local milestone runs 86 Solidity tests (58 original, 28 Experiment 002), 54 unchanged Experiment 001 Python tests, and 52 Experiment 002 Python tests. Fuzz 256 and stateful 128 x 64 budgets are unchanged. Additional retained fee/candidate compatibility tests are reported separately. [Public scenario evidence](../../research/experiments/experiment002/task012-agent-runs.json) records fresh nominal/maximum-input successes, refusal/offline controls, invalid results, malformed messages, crashes, disclosure, short slack, no actor and rollback. Inputs/assertions are deterministic; ephemeral keys/run IDs intentionally make hashes vary. Timings/gas are observations, not benchmarks or market-cost claims.

Evidence includes deployment/artifact/compiler metadata hashes, exact node commit/Cancun, signed agreement digest, agent PIDs/public addresses, initial/final balances, fee/attempt reservations, gas/status/transaction/block hashes, inclusion/deadline slack, submission observations where the agent survives, public payload sizes, CPU/RSS/wall observations and cleanup. Terminated agents may lack a local submission timestamp; canonical inclusion is recovered by the supervisor rather than fabricated. Rollback/unknown-delivery cases explicitly lack final payment certainty.

Initial development failures are preserved here: an incorrect nodeInfo field path caused setup errors before any agent run; it was corrected to the already documented top-level hardFork. The first malformed-message matrix failed in the supervisor's JSON reader before reaching the requester; the supervisor now waits only for file existence and the requester performs the rejection. An initial security-test import failed before execution and was corrected. No assertion, scenario or cap was removed. Earlier Task 009 fee failure and Task 010/011 evidence remain unchanged.

## Observed local costs and outcomes

The archived 18 process runs comprise five Settled outcomes (including one provider crash leaving exactly one unwithdrawn credit), eleven Refunded, one Unfunded and one explicitly Inconclusive rollback. These are intended scenario outcomes, not an empirical network reliability estimate. Additional security tests repeat disclosure/late cases and inject RPC/ledger faults; their unittest results are separate from this archive.

Observed deployment gas ranges 1,632,611–1,632,623; funding 326,236–326,428; claim attempts 37,022–121,103 (including deliberate reverts); refunds 85,209–85,221; withdrawals 35,928. All are below the unchanged two-million ceiling. The largest measured collective fee burn is 4,157,771,973,453,059 synthetic wei, below the 102*10^15 allowance; actual burn never replenishes conservative reservations. Nominal principal is 10^12, with signed cap 2*10^12 and contract ceiling 10^15. Maximum observed elapsed time is 3.209 seconds, sampled aggregate RSS 238,301,184 bytes and cleanup about 0.021 seconds; none is a production benchmark or hard resource guarantee.

Local retained compatibility suites also pass: 14 original fee-investigation tests and nine candidate tests. Together with 86/54/52, this is 215 test definitions at the final validation milestone; reruns, standalone executions and signature/fee probe cases are not added to that count. CI additionally repeats the unchanged 54 original Python tests on the corrected node, retaining the old negative control and opcode-witness checks.

## Mandatory scenario coverage

Contract identifiers below refer to existing `contracts/test/Experiment002Escrow.t.sol` and `Experiment002Vectors.t.sol`; Python identifiers refer to [integration tests](../../tests/experiment002/test_experiment002.py) and [security tests](../../tests/experiment002/test_security002.py).

| Plan | Evidence / observed outcome |
| --- | --- |
| T01 | `test_two_fresh_success_runs_nominal_and_maximum`: separate keys/PIDs, 18 and 2^65-2, canonical settlement/withdrawal, exact ledger and cleanup. |
| T02 | `test_requester_refusal_cannot_veto`: A funds only; B settles/withdraws. Unchanged Experiment 001 refusal remains a refund control. |
| T03 | `test_requester_offline_provider_collects`: A exits after funding; B collects and supervisor recomputes. |
| T04 | `test_wrong_result_rejected_then_refunded`; strict scalar codec rejects out-of-range evidence; contract wrong-result checks cannot be overridden by A. |
| T05 | Every field mutated without re-signing in Python Terms/Authorization/Claim/Advertisement tests and contract all-field mutation tests. |
| T06 | Python domain/chain/contract/name/version/run/key/encoding negatives; seven frozen cross-language fixtures; contract domain/cross-experiment/encoding tests. |
| T07 | Contract replay/revocation/vector tests; Python funded replay, duplicate terminal/withdrawal attempts and unknown-outcome retry latch. |
| T08 | Contract ordering matrix and live-node revoke-before-fund / consumed-revoke-then-valid-claim tests. |
| T09 | Contract -1/equality/+1 funding/claim/refund matrices; live equality expiry/refund and late-workflow inclusion tests. |
| T10 | Contract unauthorized mutation/copied-claim tests; Python method policy rejects wrong actor before signing, duplicate terminal actions revert. |
| T11 | Contract price/cap/operands fuzz, mixed concurrent/repeated agreements, forced surplus and callback/failing-transfer harness; Python wallet/closing-budget/final-transaction checks. Callback evidence is defense in depth, not EOA contract-wallet support. |
| T12 | Timeout before/after broadcast, temporarily lost receipt, wrong hash, altered event/receipt/fee/transaction/block-receipt/balance/record/credit evidence; no blind replacement/new nonce. |
| T13 | Provider killed before computation, after result and after canonical claim; A killed before funding. Refunded/unfunded/exact unwithdrawn-credit outcomes recorded. |
| T14 | `early_disclosure`: A verifies public output, B is stopped before submission, A refunds. Copied-claim contract test cannot redirect funds. Expected strong-fairness counterexample. |
| T15 | Real-process malformed/oversized/truncated/outsider-signed/duplicate evidence rejects and refunds; codec tests unknown/nonregular/symlink/FIFO/no-clobber; finite waits/cleanup. |
| T16 | Revert after observed claim yields explicit inconclusive result and stops withdrawal; pre-funding snapshot, code/hash/event/record mutations reject. No durable finality claim. |
| T17 | Startup failure, KeyboardInterrupt and cooperative RSS threshold tests reap children/remove files; loopback/proxy/CCIP and final target checks bound destinations. SIGKILL/host failure remains excluded. |
| T18 | Signed fundBefore=t0+120, claimBefore=t0+121; fund at t0+119, observe 2 seconds slack; delay to deadline, reject valid late claim then refund. Normal 300-second control collects. |
| T19 | Suspend both processes, advance beyond deadline: remains Funded; resume A, refund/withdraw exactly once. No automatic progress. |
| T20 | Existing repeated-work vector and concurrent-record contract tests permit separate authorized identical work. This proves neither work uniqueness, distinct owners nor mining eligibility. |

## Security property assessment

| Property | Enforcement and experimental evidence | Assumption / limitation |
| --- | --- | --- |
| P2-01 authorization | Established EIP-712/ECDSA; dual Terms and A Authorization; signature/tampering vectors. | Keys/host/compiler/library correctness; no formal proof. |
| P2-02 caps | Exact funded principal <= signed max <=10^15; wallet policy separately bounds fees and one intent. | Contract cannot universally bound external wallet gas. |
| P2-03 replay | Nonce consumed atomically; immutable record/terminal state; retries latch. | Cloned identical chain/run identity is outside cryptographic discrimination. |
| P2-04 expiry | Strict first-use/claim bounds, refund equality; boundary tests. | Canonical inclusion timestamp, not send/completion time. |
| P2-05 revocation | Unused only; ordering tests preserve funded obligations. | Revocation inclusion can race funding. |
| P2-06 terms | Full typed digest, dual signatures, exact schema/unchanged calldata. | Upfront consent to this narrow predicate only. |
| P2-07 domain/run | Chain/contract/domain/run binding and verified runtime. | Trusted fresh fixture and honest RPC; no arbitrary-chain portability. |
| P2-08 parties | A-only fund/refund, B-only claim; claims bind parties/agreement/auth nonce. | Distinct keys do not prove independent ownership. |
| P2-09 result | Contract fixed arithmetic; independent requester/supervisor recomputation. | Not AI quality, physical truth, effort or unique contribution. |
| P2-10 callers | Caller checks, own credits; unauthorized calls/policy tests. | Compromised authorized key can exercise its authority. |
| P2-11 terminal/refund | Exclusive Settled/Refunded transitions; deterministic exact-price credit. | No actor/inclusion means no automatic closure. |
| P2-12 accounting | Locked/credit conservation; clear-before-transfer guard; exact ledger/withdrawals. | Forced surplus possible; callback harness is test-only. |
| P2-13 veto resistance | Refusal/offline controls collect with no second A authorization. | Valid B claim must be included before deadline; not unconditional compensation. |
| P2-14 evidence/recovery | Canonical receipt/state/events, exact fees/balances, rollback and ambiguity rejection. | Trusted RPC/host, single-tx blocks, no production finality assurance. |
| P2-15 bounds | Gas/fees/attempts/principal/closing/time/message limits; cleanup/resource tests. | Cooperative sampled RSS is not hostile-process containment. |
| P2-16 local-only | Explicit verified no-fork Cancun node, literal loopback, synthetic prefunding; no keys/logged raw transactions. | Host/network/CI supply chain remains trusted. |

## Residual risks and outcome

CONDITIONAL PASS means the scoped experiment demonstrates removal of the second-signature veto for an objectively valid, timely included claim, with bounded synthetic principal/fees and explicit failure outcomes. It does not solve requester/provider fairness when inclusion is absent or late. Public output leakage, censorship/ordering, deadline slack, absent callers/lost keys, rollback, trusted host/RPC and dependency compromise remain limitations. Tests are finite and cannot establish absence of vulnerabilities.

Dependency versions/hashes and accepted local-only compiler/advisory restrictions are unchanged. New code uses existing maintained signing/RPC libraries with CCIP disabled, standard non-transient guard in the unchanged contract, no custom cryptography, arbitrary evaluation or shell execution. No new package/download is introduced by integration. CI retains immutable third-party action SHAs, contents:read, no production secrets/deployment/public RPC; installation uses upstream HTTPS and existing verified hashes. The rc1 node has no successful attestation/reproducible-build assurance; hashes rely on the reviewed publisher/source trust. PRs execute untrusted code on disposable hosted runners without repository write credentials; this is not protection against every supply-chain compromise.

Next recommended task: independently review this implementation and evidence, then select a separately authorized research question about useful-work verification or fair delivery/inclusion assumptions. Do not infer authorization to expand into native-token rewards, independent L1 implementation or autonomous public bootstrapping.
