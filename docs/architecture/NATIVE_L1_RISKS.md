# Native architecture unresolved-risk register — Task 016

Current evidence: [Task019 comparison](NATIVE_L1_COMPARISON_RESULTS.md) is **G1 HOLD**, with no candidate selected or eliminated. Earlier proposed gates/statuses below retain their historical context.

**Task 017 follow-up:** [W01–W08 workloads](NATIVE_L1_WORKLOADS.md), [common authority/recovery semantics](NATIVE_L1_AUTHORITY_SETTLEMENT_RECOVERY.md), [consensus assumptions](NATIVE_L1_CONSENSUS_ASSUMPTIONS.md), [experimental budgets](NATIVE_L1_RESOURCE_BUDGETS.md) and [next gate](NATIVE_L1_NEXT_EXPERIMENT.md) supply comparative specifications. G0 review/vector/adapter freeze remains pending; G1 is not run. No final architecture or candidate elimination follows. Earlier next-task language below is historical.

**All open.** This registers dependencies, not newly discovered exploits or approved design decisions. IDs support the [decision gate](NATIVE_L1_DECISION_GATE.md); requirement/source context is in the [report](NATIVE_L1_RESEARCH.md).

| ID / exposure | Unresolved dependency or failure | Minimum evidence to retire or bound it |
| --- | --- | --- |
| A-01 / security blocker | Open admission without resource weighting lets one operator multiply influence. Stake distribution or hash security of a new chain is unknown. | Explicit scarce-resource/eligibility model; fixed-budget identity splitting and resource-acquisition sensitivity; concentration/entry analysis. |
| A-02 / safety and availability | Partitions, stale checkpoints, rotating validator sets, long-range histories, eclipse and data withholding defeat naive finality assumptions. | Exact safety/liveness assumptions, membership transitions, authenticated sync and proof/data retrieval; adversarial partition/rejoin model. |
| A-03 / authority | Parallel delegates, fee sponsorship, subdelegation and revocation races amplify authority. | Atomic principal/fee limits across all paths; expiry/order matrices; no restoration after ambiguous delivery. |
| A-04 / recovery | Crash/lost key or stale UTXO/object/nonce causes duplicate intent or stranded value. | Durable public intent format, reconciliation states and key-recovery threat model; distinguish enabled recovery from guaranteed execution. |
| A-05 / verification | Correct output is mistaken for useful/unique work, or sensor signature for physical truth. | Bind task/program/input/evidence; independent verifier cost and collusion analysis; explicit oracle trust. No useful-work consensus weight without separate proof/security gate. |
| A-06 / resources | Cheap admission produces expensive execution/state growth, shared hotspots or signature spam. | Worst-case parser/VM/storage/network bounds; failed-action cost and constrained-client measurements; denial-of-service traces. |
| A-07 / economics | Low demand, volatile fees or subsidy dependence leaves security unaffordable; synthetic traffic masquerades as utility. | Fee-recipient accounting and real-cost/security-budget sensitivity including zero demand; independent service need and alternatives evidence. |
| A-08 / privacy and autonomy | Public machine activity exposes location/intent; gateways, discovery or hardware vendors become trusted gatekeepers. | Data-minimization and metadata threat model; roles can verify/abstain without one hosted provider; discovery remains separate unsolved research. |
| A-09 / implementation trust | VM/compiler/dependency or client monoculture diverges despite sound high-level rules. | Pinned maintenance/advisory review, independent implementation/determinism tests, reproducible artifacts and failure evidence. |
| A-10 / policy capture | Upgrade, recovery or emergency authority changes balances/rights or selects history covertly. | Publish authority and limits, adversarial migration/rollback policy and independent review before adoption. |

## Decisions expensive to reverse

| Commitment | Why migration is costly | Before deciding |
| --- | --- | --- |
| State ownership, transaction encoding and commitments/proof format | Wallets, history proofs, indexers and contracts depend on them. | Canonical vectors, independent parsers and explicit state/history migration. |
| VM/ABI, numeric semantics and metering/storage rules | Existing programs encode behavior and costs; changes can invalidate signed expectations. | Cross-platform conformance, worst-case pricing and versioned execution/upgrade policy. |
| Consensus, admission, finality and checkpoint rules | Determines security constituency, offline trust and incompatible fork/recovery behavior. | Reviewed proof assumptions, dynamic-membership and attack/cost analysis. |
| Signatures/network identity/key recovery | Long-lived machine credentials and authorization depend on compatibility. | Replay/downgrade analysis and algorithm/key migration plan without blanket recovery authority. |
| Currency fee/security roles, distribution and governance | Alters ownership/incentives and is socially difficult to reverse. | Separate explicit economic/governance review; this task selects no monetary policy. |

Modular interfaces reduce some engineering coupling but cannot make consensus history, ownership rights or economic commitments freely reversible. Keep candidate specifications disposable until evidence passes review; preserve failed alternatives.
