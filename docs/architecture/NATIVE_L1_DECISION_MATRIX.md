# Native L1 decision matrix — Task 016

**Task 017 follow-up:** [W01–W08 workloads](NATIVE_L1_WORKLOADS.md), [common authority/recovery semantics](NATIVE_L1_AUTHORITY_SETTLEMENT_RECOVERY.md), [consensus assumptions](NATIVE_L1_CONSENSUS_ASSUMPTIONS.md), [experimental budgets](NATIVE_L1_RESOURCE_BUDGETS.md) and [next gate](NATIVE_L1_NEXT_EXPERIMENT.md) supply comparative specifications. G0 review/vector/adapter freeze remains pending; G1 is not run. No final architecture or candidate elimination follows. Earlier next-task language below is historical.

**Research judgments, not measured scores or a selection.** Read the [requirements and primary sources](NATIVE_L1_RESEARCH.md), [risks](NATIVE_L1_RISKS.md) and [gate](NATIVE_L1_DECISION_GATE.md). N-01–N-08 refer to the report. State, execution and consensus remain separable.

## State-model comparison

| Model | Authority / settlement fit (N-01–05) | Conflict, recovery and cost (N-06–08) | Evidence needed |
| --- | --- | --- | --- |
| Plain UTXO / limited scripts | Explicit spend ownership and one-use outputs; constrained expressiveness. | Disjoint spends identifiable; shared input conflicts, change/fragmentation and stale input selection. | Exact contingent sum and deadline semantics may require more expressive validation; do not claim Bitcoin Script ports Experiment 002 unchanged. |
| Extended UTXO | Script/datum successors can encode bounded agreement states and conservation. | Consumed state output serializes competing transitions; transaction construction needs current references. | Show terminal exclusivity, fee/collateral accounting and revocation under stale inputs; measure shared-state contention. |
| Account-based | Balances, nonce domains and agreement records are natural representations. | Concurrent agents compete for sequence/shared state; callbacks and storage growth enlarge analysis. Accounts do not inherently forbid parallel execution. | Explicit nonce allocation, atomic aggregate grants, state-access conflicts and recovery after ambiguous submission. |
| Owned/shared objects | Capabilities and versioned resources make access dependencies explicit. | Owned paths differ from multi-party shared paths; hot shared objects still contend. | Multi-party escrow must work without custody shortcuts; prove version/conflict/authorization rules for shared state. |
| Hybrid UTXO funds + account/object agreements | Potentially combine explicit coin ownership with shared programmable agreement state. | Cross-domain value movement and atomicity add invariants and tooling. | Justify benefit against a single model; no unaccounted conversion, duplicate spend or inconsistent proof/recovery path. Defer an extra hybrid implementation until needed. |

UTXO and object models are not automatically private; input linkage, public state, recipients and timing can reveal activity. “Hybrid” is not a performance or security result.

## Three candidate configurations

| Candidate | Concrete research configuration | Defensible reason to retain | Main disqualifier / falsification |
| --- | --- | --- | --- |
| C1: accounts | Account ledger; narrow deterministic modules initially, EVM control and restricted Wasm alternative; stake-weighted BFT ordering/admission model. | Isolates authority/recovery semantics with familiar shared-state representation; compare restricted execution against general programmability. | Any grant/fee overspend, nonce recovery causing duplicate obligations, nondeterministic execution, or compulsory privileged admission. |
| C2: objects | Explicit owned capabilities plus shared agreement objects; resource VM; same stake-BFT assumptions as C1. | Tests whether explicit ownership improves authority/conservation without hiding multi-party coordination. | Shared agreements need trusted custody, capability duplication/amplification, or contention defeats preregistered workload/resource targets. |
| C3: extended UTXO | Output/state-machine validation; restricted deterministic scripts; cumulative-hash PoW ordering baseline. | Contrasting consumption/conservation and reconnect/fork-recovery behavior; avoids assuming stake-BFT is mandatory. | Cannot encode exact consent/deadline/owner rules, repeated stale construction prevents bounded progress, or modeled hash security/cost fails target envelope. |

These are neither approved stacks nor three novel protocols. C1/C2's BFT core requires a separately justified permissionless scarce-stake admission/rotation mechanism; C3 requires independently justified hash access/security. No actual stake, mining or asset is created. Extended UTXO can also use PoS, and accounts/objects can use other ordering; **do not attribute a paired consensus effect to state representation**.

Hold signed semantics, synthetic balances, fees and ordered traces constant when comparing state models. Hold transition rules/workloads constant when comparing PoW against BFT finality/admission models. Include existing EVM Experiment 002 as a semantic control, Experiment 001 requester-veto as the consent control, and existing-ledger/non-chain baselines as benefit controls. No published vendor TPS is a Genesis score.

## Selection readiness

| Criterion | Current evidence | Gate before selection |
| --- | --- | --- |
| Authorization / deterministic settlement | Narrow Anvil fixture supports N-01–04. | Independent equivalent semantics and counterexamples across candidates. |
| Delegation / durable recovery | Suggested, not demonstrated. | Principal/fee aggregate enforcement and recovery protocol, hostile stale-state analysis. |
| Consensus / Sybil / finality | External families only; no Genesis evidence. | Dynamic participation, partition/rejoin, fixed-resource identity splitting and credible economic security envelope. |
| Hardware / throughput / availability | No native workload budgets or measurements. | Predeclared profiles and resource limits; publish all failed/inconclusive results. |
| Native currency / demand | Research direction, no validated economic outcome. | Low-demand/security-cost sensitivity and independently evidenced use cases against alternatives. |
| Migration / governance / maintenance | Unselected. | Version, state proof, crypto and emergency-authority review; exact dependency/client-diversity assessment. |

No weighted total: weights and missing measurements would create false precision. Eliminate safety failures first; compare trade-offs only inside a declared workload/threat envelope. Multiple survivors or no survivor is an acceptable outcome.
