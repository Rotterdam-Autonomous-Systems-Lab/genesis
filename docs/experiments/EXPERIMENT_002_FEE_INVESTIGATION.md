# Experiment 002 Fee-Evidence Investigation — Task 010

**Task 011 follow-up:** [corrected-node validation](EXPERIMENT_002_ANVIL_VALIDATION.md) supersedes readiness for the explicit verified profile, subject to publication Ubuntu CI. This document preserves the original diagnosis and failed acquisition; the old node still fails the unchanged strict check.

**2026-10-18 — Conclusion: STILL BLOCKED.** The Task 009 contradiction is reproduced and diagnosed as an Anvil v1.0.0 RPC fee-reporting defect. No actual fee-cap violation was observed. The strict reconciliation check is retained; no agent implementation was resumed, dependency adopted, cap raised or authorization semantics changed. Experiment 002 remains unaccepted and its incomplete agent workflow stays paused.

## Scope and reproducible artifacts

Starting point: [Task 009 commit aa484cd](https://github.com/Rotterdam-Autonomous-Systems-Lab/genesis/commit/aa484cd0355131a8fb3cac5db5898bb97a3786a1), [implementation review](EXPERIMENT_002_IMPLEMENTATION_REVIEW.md), original [reproducer](../../research/compatibility/experiment002/check_anvil_fee_receipt.py), [ADR 0002](../adr/0002-experiment-002-fair-exchange.md) and [fee model](EXPERIMENT_002_BOUNDED_COST_MODEL.md).

- [Independent raw-RPC probe](../../research/compatibility/experiment002/investigate_fee_receipts.py) uses Python standard-library HTTP and eth-account signing, not Web3 receipt conversion or the unpublished agents. It starts fresh zero-account loopback nodes; no public RPC, fork, real funds, key files, raw-transaction artifacts or autonomous services.
- [Test-only FeeWitness](../../contracts/test/FeeWitness.sol) emits EVM `GASPRICE` and `BASEFEE` during execution. Its revert entry point tests charged fees on failed execution. It does not modify either escrow or add an agent service.
- [Strict fee oracle](../../research/compatibility/experiment002/fee_evidence.py) independently uses the EIP-1559 reference arithmetic. It rejects contradictory receipts; computed expected values never replace reported values.
- [14 verification/characterization tests](../../research/compatibility/experiment002/test_fee_investigation.py), [22 clean-run raw evidence records](../../research/compatibility/experiment002/task010-fee-evidence.json), and [immutable source-review/provenance references](../../research/compatibility/experiment002/task010-source-review.json).

This is an independently structured reproduction within the same project/trusted host, not an independent audit, different execution-client comparison or formal proof. The opcode and wallet measurements use separate observable paths in the same Anvil EVM, not independently trusted ledgers.

## Original failure reproduced unchanged

The original reproducer again returned **2** on the pinned Foundry commit `8692e926198056d0228c1e166b1b6c34a5bed66c`: type-2 maxFee=3,000,000,000, maxPriority=1,000,000,000, gasUsed=48,076, included block baseFee=2,625,000,000. Receipt price=3,625,000,000; actual debit=144,228,000,000,000; receipt-derived fee=174,275,500,000,000 synthetic wei. Deployment again used 1,632,623 gas, below 2,000,000.

Task 009 set the next block fee to 3 gwei, mined an empty block, then sent its transaction. The following inclusion block's base fee was 2.625 gwei. That decrease is not the discrepancy: the original calculation correctly read the **transaction's inclusion block**. The new probe sets the inclusion fee directly without the extra empty block and checks it against the included header and opcode witness.

## Root cause: missing clamp in RPC construction

For an includable type-2 transaction, [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559#specification) defines:

```text
actualPriority = min(maxPriorityFeePerGas, maxFeePerGas - inclusionBlock.baseFeePerGas)
effectivePrice = inclusionBlock.baseFeePerGas + actualPriority
fee = gasUsed * effectivePrice
```

Equivalently, effectivePrice is min(maxFee, baseFee + maxPriority), provided baseFee <= maxFee. All probe calculations use integer wei; no floating-point gwei conversion or rounding tolerance. The total cap includes the tip; maxPriority is a ceiling, not a guaranteed tip.

The pinned [receipt builder, lines 2348–2366](https://github.com/foundry-rs/foundry/blob/8692e926198056d0228c1e166b1b6c34a5bed66c/crates/anvil/src/eth/backend/mem/mod.rs#L2348) adds the maximum priority fee to the header base fee without applying the total cap. `eth_getBlockReceipts` calls the same receipt builder. The [mined-transaction RPC constructor, lines 2941–2955](https://github.com/foundry-rs/foundry/blob/8692e926198056d0228c1e166b1b6c34a5bed66c/crates/anvil/src/eth/backend/mem/mod.rs#L2941) likewise uses the uncapped sum for mined `gasPrice`; its pending-transaction branch has different semantics.

Therefore three agreeing RPC fields are correlated faulty reporting: receipt effectiveGasPrice, block-receipt effectiveGasPrice, and mined transaction gasPrice. They are not independent corroboration. Raw JSON already contains the incorrect values, excluding Web3 formatting as the cause. The runtime opcode witness and the isolated sender debit instead match the capped EIP-1559 amount. Observed behavior exactly matches the missing clamp in the pinned source.

EIP-1559's consensus receipt payload contains status, cumulative gas, logs bloom and logs; effectiveGasPrice is derived RPC metadata. A canonical block/hash/transaction check alone does not authenticate every RPC-added field. The experiment still requires those fields to agree with independent arithmetic and accounting; “derived metadata” is not permission to ignore a discrepancy.

## Boundary matrix and repeatability

Two fresh nodes/identities per row: **22 cases**, 20 included transactions and two non-inclusions. Each included call is isolated, value=0, with no other transaction in its block and sender distinct from coinbase. Balances are queried at the exact parent/inclusion block numbers and block hashes are rechecked. Logs come only from the deployed witness. Each fixture has one deployer attempt and at most one requester attempt; initial synthetic balances are 6*10^15 and 48*10^15, no top-ups. Per-transaction gas=2,000,000, fee cap=3*10^9 and priority cap <=10^9 remain unchanged.

All prices in the table are **integer wei/gas**. Success witness gasUsed=22,493; revert gasUsed=21,305. These are diagnostic observations, not escrow or performance benchmarks.

| Inclusion base fee | Priority cap | RPC price | Charged/opcode price | Outcome in both repeats |
| --- | --- | --- | --- | --- |
| 0 | 1,000,000,000 | 1,000,000,000 | 1,000,000,000 | Reconciled. |
| 1,000,000,000 | 1,000,000,000 | 2,000,000,000 | 2,000,000,000 | Reconciled. |
| 1,999,999,999 | 1,000,000,000 | 2,999,999,999 | 2,999,999,999 | Reconciled. |
| 2,000,000,000 | 1,000,000,000 | 3,000,000,000 | 3,000,000,000 | Exact clamp boundary reconciled. |
| 2,000,000,001 | 1,000,000,000 | 3,000,000,001 | 3,000,000,000 | Strict contradiction; one wei matters. |
| 2,625,000,000 | 1,000,000,000 | 3,625,000,000 | 3,000,000,000 | Original-price contradiction. |
| 3,000,000,000 | 1,000,000,000 | 4,000,000,000 | 3,000,000,000 | At signed fee cap: contradiction. |
| 3,000,000,001 | 1,000,000,000 | No receipt | No debit or consumed nonce | Not included during bounded observation. |
| 3,000,000,000 | 0 | 3,000,000,000 | 3,000,000,000 | Zero-tip control reconciled. |
| 1,000,000,000; revert | 1,000,000,000 | 2,000,000,000 | 2,000,000,000; debit evidence | Revert charges fees; reconciled. |
| 2,625,000,000; revert | 1,000,000,000 | 3,625,000,000 | 3,000,000,000; debit evidence | Revert also triggers reporting defect. |

Summary: **12 reconciled, eight contradictory, two not included**. Every included debit matched the correct formula and stayed below its signed reservation; zero observed excess debits. No reverts were treated as fee-free. At one wei above the clamp, the fee overstatement equals gasUsed wei, proving the effect is not floating-point noise.

For the direct 2.625-gwei witness case: actual debit=67,479,000,000,000; reported fee=81,537,125,000,000; overstatement=14,058,125,000,000 wei. The original revocation case uses more gas, so its absolute difference is larger. All before/after balances, transaction types/caps, inclusion headers, statuses, gasUsed, raw fee quantities, admin RPC inputs/results, version/binary hash and public transaction identities are in the evidence JSON. Non-inclusion means observed absence, not a guaranteed future rejection; any queued transaction is destroyed with its disposable node. No fee escalation or retry was attempted.

## Assessment of the fee-evidence model

The approved cost equation and rejection of inconsistent canonical evidence are **correct, not overly strict**. The finite reservation does not fail merely because a reporting field is wrong. The original model was incomplete about RPC-added fee metadata and the conditions under which wallet deltas isolate fees.

The diagnostic delta equation is valid only for these isolated zero-value calls, with no incoming funds, concurrent sender transactions, coinbase payment or principal transfer. A future agent funding/withdrawal audit must explicitly account for all principal flows and use canonical anchored state; it must not apply this simplified subtraction universally. This investigation does not implement such an agent auditor.

The strict oracle cross-checks expected price, raw receipt/mined-transaction/block-receipt fee fields, opcode witness for successful calls, wallet debit, gas/reservation and canonical identities. Tests mutate fees, balances, gas, type, cap, priority, value, block/parent/hash and witness fields; contradictions, including a single wei, reject without modifying evidence. Unknown inclusion is separate from valid zero fees. No normalization, tolerance, RPC shim or fallback makes the bad baseline appear accepted.

## Proposed correction and compatibility status

**Preferred correction: a separately reviewed, exactly pinned Anvil with correct RPC fee construction**, retaining the strict checker and existing limits. Upstream [commit 75151e9](https://github.com/foundry-rs/foundry/commit/75151e9cae397d34034c1d03defc4f94b6363a3c), dated 2025-11-24, replaces the receipt arithmetic with Alloy's effective-price helper. That commit alone addresses the receipt path; the mined-transaction field must also be verified before adopting a node.

Source inspection of candidate [v1.8.5 / 51a52c5](https://github.com/foundry-rs/foundry/blob/51a52c59cffd940f76eddd0b4bb1791aa4b5ac7f/crates/anvil/src/eth/backend/mem/mod.rs#L8065) shows helper-based calculation for both the receipt and mined-transaction paths (latter at line 10284). This is a **source-level correction candidate**, not a selected dependency or tested compatible runtime.

One 60-second download attempt for the official macOS x86_64 v1.8.5 archive timed out after 126,533,605 of 133,090,112 bytes. The partial archive's hash did not equal the release asset's published SHA-256 (`b919f69bb4231ad68beaaba9dc8f7d36d9d552cef1a76a8bf69c2bdfd974339a`). It was never extracted or executed; no retry, global installation or baseline replacement occurred. Published digest metadata is not an independent attestation. The candidate has **no binary, macOS/Linux or full-baseline compatibility validation** here. It cannot justify clearing the blocker.

A narrower backport could fix the two reporting paths but introduces a custom node build and provenance/maintenance obligations; it is not implemented or approved. Deriving a fee and replacing a contradictory receipt, suppressing the boundary test, avoiding clamped cases, increasing the cap or reducing tips solely to hide the bug are rejected approaches.

Before resolution, require verified candidate bytes/source pin; both reporting paths agreeing with EVM and wallet evidence across this matrix and the original reproducer; unchanged 86 Solidity/54 Python controls; gas/resource/dependency/CI review; and explicit candidate adoption in the dependency/decision records. No authorization/signature/escrow design change is indicated by the evidence. No node candidate is adopted in Task 010. Candidate testing must explicitly add its reviewed immutable reference to the probe; do not remove the existing version guard.

## Reproduction, regression and CI

Use existing [pinned installation instructions](../../DEPENDENCIES.md), then from the repository root:

```sh
export PATH="$PWD/internal/tools/foundry:$PATH"
scripts/check-toolchain.sh
scripts/check-dependencies.sh
forge fmt --check
forge build --offline
forge test --offline -v
PYTHONPATH=sdk/python internal/agent-venv/bin/python -m unittest discover -s tests/python -v
internal/agent-venv/bin/python -m unittest discover -s research/compatibility/experiment002 -p 'test_fee_*.py' -v
internal/agent-venv/bin/python research/compatibility/experiment002/investigate_fee_receipts.py --repeats 2
internal/agent-venv/bin/python research/compatibility/experiment002/check_anvil_fee_receipt.py
```

Both final diagnostic commands intentionally return **2** on this defective baseline; preserve that status rather than chaining them under a success-only shell without explaining the blocker. Each node has bounded HTTP/startup/receipt/wall/cleanup time, raw responses are size-limited, proxy/redirect fallback is disabled, no key/raw signed bytes are persisted, and all children are stopped/reaped. Tests run without public network calls after dependency installation.

Local validation: **86 Solidity and 54 original Python regressions pass**, plus **14 new research tests**. The existing CI is extended only with a clearly named discrepancy-characterization step, using existing pins/read-only permissions and no new third-party action. Green characterization means the defect is reproduced and rejected as expected; it is **not** green Experiment 002 readiness. The unchanged original reproducer still fails its strict gate. Inspect the Actions run for this publication commit for Ubuntu results; macOS evidence is the committed JSON.

## Conclusion and next task

**STILL BLOCKED.** Root cause is established for the tested baseline: incorrect derived RPC fees, not excess charging, malformed signing, Web3 conversion or wrong inclusion-block selection. Corrected-node source exists, but a compatible verified binary is not established. The fee model and budgets remain unchanged; ADR 0002 remains Accepted for bounded local design only. Task 009's experimental acceptance remains FAIL/unaccepted.

Experiment 002 implementation **may not safely resume on the unchanged baseline** under its required evidence checks. Recommended next task: acquire and verify an explicit corrected-node candidate, run this strict matrix/original reproducer and full compatibility review, then record a reviewed dependency decision. Keep the incomplete agents paused. No future Genesis chain, consensus, token or bootstrapping capability is validated.
