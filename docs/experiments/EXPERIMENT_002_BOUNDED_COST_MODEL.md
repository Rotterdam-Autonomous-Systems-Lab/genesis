# Experiment 002 Bounded Cost Model — Task 008

**Task 011 current profile:** [corrected-node validation](EXPERIMENT_002_ANVIL_VALIDATION.md) and [ADR 0005](../adr/0005-experiment-002-corrected-anvil-baseline.md) replace only the Experiment 002 Anvil selection with v1.6.0-rc1 / b272ce3366987406406e9eb1b82596653a3ad628, explicit Cancun, conditional on publication Ubuntu CI. Forge/Cast/compiler/libraries/Python, source restrictions, signed types and all economic/security limits remain unchanged. Old blocker evidence below is historical. This is infrastructure PASS, not complete agent implementation or experiment acceptance.

**Task 009 current disposition: partial contract implementation; acceptance FAIL / implementation BLOCKED.** [Fee-evidence review](EXPERIMENT_002_IMPLEMENTATION_REVIEW.md) supersedes earlier READY status without changing the frozen design or budgets. Pinned Anvil receipt effectiveGasPrice conflicts with the actual capped wallet debit; dependency/fee-evidence compatibility is reopened. ADR 0002 remains accepted design only.

**2026-10-18 — B-FEE RESOLVED as a local operator policy; not yet implemented/enforced by Experiment 002.** All amounts are synthetic wei on a temporary local chain. No real assets, paid hosting, native-token issuance or production pricing is authorized. See [blocker resolution](EXPERIMENT_002_BLOCKER_RESOLUTION.md), [final specification](EXPERIMENT_002_FINAL_SPEC.md) and [arithmetic check](../../research/compatibility/experiment002/check_fee_bounds.py).

## 1. Independent authorities and assumptions

Signed service Terms/Authorization cap **principal**, not transaction fees. A separately approved local operator policy authorizes gas for each role. The escrow cannot universally limit fees a participant spends through other keys, clients, contracts, chains or replacement transactions. Bounds below assume the specified honest signer/supervisor, correct EIP-1559 ledger, one chain/run, no unauthorized top-ups and only the allowed transaction targets/methods. Compromised keys/host/RPC can bypass off-chain policy; do not claim universal containment.

Fixed EIP-1559 cap values are inherited from the existing tested signer, not invented as market prices: `gasLimit <= 2,000,000`, `maxFeePerGas <= 3,000,000,000`, `0 <= maxPriorityFeePerGas <= 1,000,000,000`, with priority also <= maxFee. No legacy, blob, sponsored, access-list-added or automatic replacement transactions. Constructor deployment is the one designated deployer transaction; agent calls target only the verified escrow/ABI. This single-agreement fixture authorizes no other transfer or new agreement principal.

Under [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559), an included transaction's actual gas cost is gasUsed times its effective gas price, no greater than gasLimit times maxFeePerGas. A revert/out-of-gas can consume fees while restoring contract state; a non-included transaction does not pay chain gas. If base fee exceeds the signed cap, wait/abort under the runtime budget rather than raise fees. Finite fees cannot guarantee inclusion or refund liveness.

## 2. Explicit budgets and maximum loss

Per-attempt worst-case reservation is **6,000,000,000,000,000 wei** (2,000,000 x 3,000,000,000). Charge this conservative reservation before signing/submission; do not rely on a purported receipt or a future refund to restore run budget. Count failed and ambiguous attempts. No automatically fresh authorization/nonce/replacement or retry loop. Any permitted identical-hash rebroadcast also consumes an attempt/reservation conservatively. Unresolved broadcast uncertainty blocks further sends by that signer.

| Role | Maximum attempts per run | Covered actions | Fee allowance / maximum chain gas cost |
| --- | --- | --- | --- |
| Trusted deployer | 1 | One deployment attempt, including failure. | 6,000,000,000,000,000 wei (0.006 synthetic ETH). |
| Requester A | 8 | Funding, unused revocation if selected, rejected/reverted calls, refund and own withdrawal. | 48,000,000,000,000,000 wei (0.048 synthetic ETH). |
| Provider B | 8 | Result claim/submission, rejected/reverted calls and own withdrawal. | 48,000,000,000,000,000 wei (0.048 synthetic ETH). |
| Combined | 17 | All roles, all success/failure schedules. | 102,000,000,000,000,000 wei (0.102 synthetic ETH). |

Reserve two A attempt slots/fee reservations for refund plus withdrawal before optional funding/revocation retries; reserve one B slot for withdrawal before claim retries. Reservation is not an inclusion guarantee: a failed closing transaction or lost key can still leave principal/credit uncollected. No additional spending to force completion once a budget is exhausted.

Let P be the single signed agreed price, `0 < P <= authorization.maxAmount <= 10^15`. A's worst principal exposure is P even if escrow never returns it; nominal P=10^12. A's combined exposure <= P + 48*10^15; B's fee exposure <=48*10^15, with no promised reimbursement for work; deployer <=6*10^15. With maximum permitted P, the sum of initial role-wallet balances must not exceed **103,000,000,000,000,000 wei (0.103 synthetic ETH)**. Prefund only these allowances plus A's exact P, never top up during a run. Escrow withdrawals only move this starting supply among the test roles; principal transfer is not additional collective fee burn. Do not double-count locked principal and its eventual provider/requester credit as two losses.

The collective fee bound is 0.102, while the conservative sum of per-role fee-plus-principal exposure is at most 0.103. Key/host compromise invalidates signer-policy assurances; in a closed fixture without extra credits/top-ups, remaining wallet balances still limit what is available, not what a contract can enforce. Synthetic chain reset destroys test balances and proves no real-value recovery property.

## 3. Measured control evidence versus limits

Task 008 ran unchanged Experiment 001 success/refusal controls after a fresh build. These are **not Experiment 002 gas estimates** and do not prove its future code fits the ceilings.

| Action | Observed gasUsed in control | Per-action maximum permitted for Experiment 002 |
| --- | --- | --- |
| Deployment | 1,784,980 in both controls. | 2,000,000. |
| Funding | 323,878 success; 323,866 refusal. | 2,000,000. |
| Provider settlement | 105,301 success; requires Experiment 001 Acceptance. | 2,000,000 for the new claim, to be measured. |
| Refund | 82,360 refusal control. | 2,000,000. |
| Own-credit withdrawal | 54,699 in both paths. | 2,000,000. |

The unchanged control fixtures retain their original prefunding and do not enforce the new role-wallet/reservation policy; only their observed existing fee fields and gas usage are compatibility evidence. Success used four transactions including deployment; refusal/refund used four. Both asserted exact principal and stopped children; local elapsed times were 2.424 and 4.735 seconds. Calldata/run/signature variation can change gas; these are observations, not benchmarks or economic efficiency claims. Failed transactions remain conservatively charged up to the full reservation, regardless of lower observed gas. Future code exceeding a ceiling must fail acceptance or trigger a reviewed design change, never an automatic cap increase.

## 4. Runtime and local compute costs

Per integrated run: one supervisor, one Anvil and two agent processes maximum; no persistent agents, replication, model calls, public RPC/fork, hosted service or external compute. Existing normal wall-clock budget remains **120 seconds**; require bounded termination and kill/reap within a further **15 seconds** (up to three children, each using a 2-second graceful plus 2-second forced-stop wait). RPC timeout <=5 seconds, message <=16 KiB, finite polls, fixed arithmetic and capped signer attempts. A stalled chain/fee spike/deadline cannot extend those limits. Setup/build/full regression batch has a separate **900-second** ceiling, matching the existing CI job budget; it is not free work outside accounting.

Record elapsed/CPU time, child exit status, peak memory and host logical CPU count C. Under a cooperative host/supervisor the run consumes at most `135 * C` CPU-core seconds of host capacity, a capacity bound rather than an OS quota or measured CPU usage. Monitor aggregate RSS with a 2 GiB termination threshold; watchdog sampling can overshoot and is not hostile-code memory isolation. Record failures rather than claim hard containment that the OS does not supply. No monetary electricity/hardware price is assumed: for an explicitly assumed host cost rate r, incremental accounting cost is bounded by r times allowed elapsed time under that rate model. Existing hardware/electricity costs are not zero merely because no paid service is provisioned.

No real-money asset loss is authorized; zero real-fund exposure relies on local-only endpoints, synthetic keys/funds and no paid-service credentials. Host failure, SIGKILL of the supervisor or an adversarial OS can defeat cleanup/resource accounting. Such cases are outside the cooperative-host bound and must be inconclusive, not quietly treated as safe success.

## 5. Required measurable controls and tests

1. Operator-approved configuration is supplied out of band by the trusted harness, never through peer-controlled transport; read it once, freeze it for the run and record its public hash. The run manifest freezes principal P, role addresses, chain/deployment/run/code identity, per-role attempts/gas/fee/total reservations, targets/methods and time limits. Validate integers before signing; fail closed on missing/mismatching budget. Never trust fee fields supplied by a peer or RPC without cap checks.
2. Reserve/charge worst-case cost **before every signing/submission attempt**, including reverts/ambiguous broadcasts; do not release reservations from unauthenticated evidence. Confirm remaining wallet balance for value plus worst-case gas. No top-ups, other transfers or fresh authorities to bypass exhaustion.
3. Positive/negative tests at gasLimit=2,000,000 and +1; fee=3,000,000,000 and +1; priority cap and priority>maxFee; exact remaining budget and one wei/one attempt over; count failed, withheld, ambiguous and identical-rebroadcast schedules. Assert over-budget actions produce no signature/send. Parameter values are policy ceilings, not recommendations for a public network.
4. Test base fee at 0, 1, 2, 3 and above 3 gwei; no cap escalation and no liveness claim when inclusion is unavailable. Test insufficient balances, reserved closing slots, out-of-gas/reverts, fee spikes during refund and ambiguous receipts. Reconcile canonical gasUsed/effectiveGasPrice and principal separately; measured cost must not exceed reservations.
5. Execute T01–T20 plus these controls, measure future component gas against ceilings, run wall-time/child cleanup tests and report all incomplete outcomes. The [integer arithmetic check](../../research/compatibility/experiment002/check_fee_bounds.py) currently covers 20 formula cases and role-bound exhaustion; it is not an implemented budget manager, signer test or empirical inclusion experiment.

B-FEE is resolved because meaningful finite policy limits are now specified and numerically checked. Implementation readiness does not assert those controls already exist in Experiment 002; their enforcement is mandatory acceptance evidence in the separately authorized implementation task.

## Task 010 — derived RPC metadata and isolated balance evidence

[Investigation](EXPERIMENT_002_FEE_INVESTIGATION.md) confirms the cost equation and strict gate are correct: effectivePrice = baseFee + min(priorityCap, feeCap - baseFee) for includable type-2 transactions. Pinned Anvil instead reports baseFee + priorityCap in receipt/mined-transaction RPC fields; raw RPC and opcode/balance evidence establish a reporting defect, not observed excess charging. The same error exists at the one-wei clamp boundary and on reverts. Do not normalize or bypass it.

Fee-added RPC metadata is not authenticated merely by checking block/transaction membership. Require independent arithmetic, canonical anchors and appropriate wallet/accounting evidence to agree. BalanceBefore - BalanceAfter equals fee only for isolated zero-value calls without incoming transfers, another sender transaction or coinbase payment. Real fixture funding/withdrawal accounting must include principal flows; the new diagnostic oracle deliberately does not implement that general audit.

No fee/attempt/reservation/principal/run limits change. **Compatibility remains BLOCKED** pending a verified corrected-node decision. A mathematical bound and green defect-characterization tests do not establish complete signer enforcement or agent readiness. No dependency or agent code is adopted by this investigation.
