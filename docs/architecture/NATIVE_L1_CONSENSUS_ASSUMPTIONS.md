# Consensus requirements and security assumptions — Task 017

**Research requirements, not a protocol selection or security proof.** Applies independently of account/object/extended-UTXO representation. [Workloads](NATIVE_L1_WORKLOADS.md) require authenticated ordering/evidence; the [proposed reference experiment](NATIVE_L1_NEXT_EXPERIMENT.md) supplies a declared ordering oracle and cannot validate consensus.

## Required interface

A native design must specify transaction validity versus ordering, genesis/network identity, fork choice, committed/finalized state, evidence authenticity/data availability, time/expiry rules, client trust anchors, membership changes and recovery from faults. No AI score, device identity or useful-work result is privileged consensus evidence. A rejected transaction is not a censorship observation; a valid non-included transaction may be censored, delayed, underpriced or unknown.

| Requirement | Observable test obligation / limit |
| --- | --- |
| Safety | No two honest clients finalize contradictory histories within stated assumptions. Per-owner/grant/intent invariants hold on every accepted history. |
| Liveness | Under declared timely-delivery, honest-resource/online-power and fee/admission conditions, valid transactions can progress; specify inclusion bounds separately from block progress. No unconditional guarantee under partitions. |
| Sybil resistance | Fixed total scarce resource must not acquire extra consensus influence by splitting keys or AI identities. Resource acquisition/concentration is a separate attack. |
| Availability | Clients can retrieve enough transaction/state evidence to verify outcomes; a certificate without required data is insufficient. |
| Recovery | Distinguish legitimate prefinal reorg from finalized-state contradiction; late joiners and long-offline clients need explicit trusted/untrusted checkpoint rules. |
| Permissionlessness | Define who can submit, verify, propose and join/leave the active set, and costs/gates for each. Open RPC does not prove open validator membership. |

## Family comparison

| Family | Actual premises and costs | Failure/recovery and small-network implications |
| --- | --- | --- |
| Cumulative-hash PoW | Honest effective hash resource plus propagation assumptions; energy, equipment and ongoing operating costs. Settlement confidence is probabilistic, not absolute at a universal number of blocks. | Majority hash can reorder/censor; minority strategy/eclipsing/propagation can also hurt security/incentives. Partitions produce competing histories; clients re-evaluate accumulated work and inclusion. A new chain with little hash may be cheaply attacked/rented relative to value at risk; Bitcoin's security does not transfer. [Whitepaper §§4–6,11](https://bitcoin.org/bitcoin.pdf), [Backbone analysis](https://eprint.iacr.org/2014/765), [selfish-mining model](https://arxiv.org/abs/1311.0243v5). |
| Stake-weighted BFT ordering | CometBFT-style active voting power: less than one-third Byzantine for safety; more than two-thirds commit power; progress needs sufficient online responsive honest power and eventual synchrony. Capital, connectivity, signing protection, bandwidth and state validation cost. | One-third withholding can obstruct progress in the fixed-set model; conflicting commits violate its assumptions. Membership/rotation/unbonding are additional specifications, not provided by the threshold alone. Small bootstrap allocation or delegated stake can centralize control despite many keys. [Consensus spec v0.38.17](https://raw.githubusercontent.com/cometbft/cometbft/v0.38.17/spec/consensus/consensus.md). |
| PoS fork choice plus finality gadget | Ethereum is a distinct example: stake-weighted head selection and checkpoint finality/penalties. Stake capital and online operation replace hash competition; they do not eliminate operational/economic assumptions. | Reorg exposure differs before/after finality; long-offline synchronization needs a recent trusted checkpoint. Long-range old-key histories and correlated stake/control require recovery policy. Slashing does not automatically recover availability or reimburse users. [PoS](https://ethereum.org/developers/docs/consensus-mechanisms/pos/), [weak subjectivity](https://ethereum.org/developers/docs/consensus-mechanisms/pos/weak-subjectivity/). |

These descriptions do not prove every PoS design uses identical thresholds/checkpoints or every PoW design shares identical security. References were inspected 2026-10-19; formal models have narrower assumptions than operational deployments. No new benchmark, proof audit or calibrated economic attack cost exists here. Storage-weighted consensus and other scarce-resource mechanisms remain [Task 016 research comparators](NATIVE_L1_RESEARCH.md), not evidence for arbitrary useful-AI-work consensus. Fixed-authority committees are transparent simulation/devnet controls, not permissionless-security successes.

Fees/rewards must make honest operation feasible without assuming value/adoption. Model security-provider receipts separately from burned fees, market revenue, issuance/subsidies and real resource costs. Preserve zero-demand, subsidy withdrawal, stake/hash concentration, bribery and censorship outcomes. No reward/allocation/monetary policy is chosen. A small initial network needs a credible scarce-resource bootstrap and independent-operator threat model before calling itself permissionlessly secure; counts of bots, machines or addresses are not that evidence.

## Failure profiles independent of state representation

Use the same logical workload and adversary ownership/resource distributions when later comparing consensus models. Cases: timely connectivity; loss/reordering; finite partition; partition without a known end; targeted eclipse; offline period exceeding checkpoint trust window; conflicting finalized evidence; data withheld; membership changes while a client is offline. Quantify effective hash share or voting power and corruption timing, not just faulty node count. State whether validator-set/keys can change during a trace.

For reference semantics, run three *oracle profiles*: O1 stable authenticated order; O2 reversible prefinal suffix; O3 conflicting purported-final observations. O2 must restore all balances/counters/consumed intents consistently on rollback while clients retain unresolved journal exposure; O3 must halt clients, not fabricate consensus recovery. These fault schedules are not PoW/PoS simulations or measurements of fork probability.

Native finality timing, tolerated offline duration, censorship bounds, full-node hardware, dynamic membership, randomness/leader-selection, unbonding/slashing, long-range defense and emergency authority remain unresolved. The [budget document](NATIVE_L1_RESOURCE_BUDGETS.md) defines lab delay classes only. Supporting a high-latency satellite *client* does not require a satellite validator, and does not remove online quorum requirements.
