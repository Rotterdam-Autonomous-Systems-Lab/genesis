# Proposed next architecture decision gate — Task 016

**Task 017 follow-up:** [W01–W08 workloads](NATIVE_L1_WORKLOADS.md), [common authority/recovery semantics](NATIVE_L1_AUTHORITY_SETTLEMENT_RECOVERY.md), [consensus assumptions](NATIVE_L1_CONSENSUS_ASSUMPTIONS.md), [experimental budgets](NATIVE_L1_RESOURCE_BUDGETS.md) and [next gate](NATIVE_L1_NEXT_EXPERIMENT.md) supply comparative specifications. G0 review/vector/adapter freeze remains pending; G1 is not run. No final architecture or candidate elimination follows. Earlier next-task language below is historical.

**Proposal, not implementation authorization.** Recommended Task 017: **Comparative authority, settlement and recovery specification** for [C1–C3](NATIVE_L1_DECISION_MATRIX.md), with a separate consensus/admission threat model. Status: READY to specify comparative research; **NOT READY to select or implement a native L1**.

## Question and competing hypotheses

Can any candidate represent N-01–N-08 without expanding authority or hiding recovery/finality trust, within realistic machine/operator budgets? C1 may offer sufficient simplicity; C2 may reduce ownership mistakes; C3 may improve explicit consumption/recovery. Competing hypotheses: all add unnecessary complexity compared with an existing ledger; no candidate meets connectivity/security-cost requirements; application-level constraints suffice without changing the base layer.

The outcome may retain multiple candidates, reject all, or require a narrower workload. This is not a contest to select a winner from unmeasured scores.

## Gate G0: comparative specification before models

Task 017 should deliver the following documentation for independent review:

1. **Common state machine and authority:** map each experiment action to each candidate; exact bytes/digest domain, participants, intent identity, grant scope, separate principal/fee caps, nonce/input/object consumption, funding/claim/refund/collection and failure states. Include aggregate grants, concurrent delegates, revocation and recovery extensions as new unproven properties. Preserve Experiment 001 and 002 as distinct consent controls.
2. **Evidence interface:** specify inclusion, finality and per-owner state proofs, data availability, authenticated network identity, and durable recovery record. Separate submitted, included, credited, collected, orphaned and unknown. Define who can rotate/recover keys and invalidate authorizations, with no ability to redirect existing obligations silently.
3. **Common corpus:** enumerate invalid signatures/domain/encoding, replay, wrong result/owner, conservation, claim/refund at deadline minus one/equality/plus one, both revocation orders, crash before/after submission, lost reply, stale record, repeated recovery, parallel budget exhaustion and unbounded-input rejection. Include disclosure/no timely inclusion, no actor and insufficient-slack limitations as expected outcomes, not successes to hide.
4. **Independent security model:** separately specify PoW hash/propagation assumptions and BFT scarce-stake admission, voting-power thresholds, set changes, synchrony, checkpoints, unbonding and censorship. Analyze attacks both within and outside assumptions. Identity splitting must hold scarce resources fixed; acquiring more resources is a different attack. AI task results contribute no default consensus weight.
5. **Workload and budget preregistration:** at least a human payment, deterministic service agreement and intermittently connected device purchase. State conflict rates, independent versus shared agreements, outstanding delegates, proof sizes, offline duration, delay/loss/partitions and initial/cumulative resource budgets. Device roles are client/relay/full verifier/validator, not all validators. Choose target hardware, memory/storage/bandwidth/energy and response/cost envelopes from an explicit use case before measuring. No throughput target is currently justified.
6. **Economic envelope:** compare zero/low genuine demand, congestion, reduced subsidy, concentrated stake/hash access and volatile purchasing power. Separate customer fees, security-provider receipts, destroyed fees, external subsidy and real operating/attack costs. Include existing-chain/existing-asset and non-chain controls; no issuance/allocation schedule or token launch.

**G0 passes only if** all candidates have traceable semantics or an explicit documented rejection; the corpus, fault envelope, measurement plan and resource ceilings are reproducible; A-01–A-10 have owners assigned by the future task and evidence plans; an adversarial review finds no hidden permission gate or unchecked authority. Missing budgets/semantics mean HOLD, not an implicit pass. Passing G0 authorizes no code automatically.

## Gate G1: subsequently authorized bounded reference experiments

Only a separate task may implement disposable local state-machine models or use reviewed existing runtimes. No peer-to-peer native chain, production keys, real funds, public deployments or currency mechanics are needed. Compare state models with **identical ordered histories**, and consensus models with **identical transition workloads**; otherwise causal attribution is invalid.

Predeclare finite enumeration/property budgets, seeds, exact dependencies and host budgets. Use independently authored oracle/encoding checks. Measure CPU, peak memory, bytes/state growth, fees/resource reservations, conflict/reconstruction rates, restart reconciliation, verification latency and finality/inclusion delays; retain every timeout/rejected/inconclusive trace. A model-passing result is evidence about that model, not secure deployed consensus or demand.

| Falsifiable criterion | Reject or hold when |
| --- | --- |
| Authority/conservation (N-01–05) | Any unauthorized principal/fee debit, duplicate obligation/payment, wrong owner, incorrect result acceptance, conflicting terminal result, or grant amplification. Zero tolerated in corpus. |
| Evidence/recovery (N-06–07) | Contradictory/unknown evidence is promoted to success, or restart creates fresh spending authority before reconciliation. |
| Determinism/resources (N-08) | Independent implementations disagree, admission/verification exceeds fixed limits, or liveness requires raising ceilings after observing results. |
| Consensus claims (A-01–02) | Safety breaks within declared assumptions, identities gain influence at fixed total resource, or required honest/synchrony/checkpoint assumptions are omitted. Outside-assumption failure must be reported. |
| Practical benefit (A-06–08) | Candidate misses preregistered device/operator cost/availability targets or offers no evidenced advantage over simpler controls. Do not infer adoption from synthetic throughput. |

Before **final architecture selection**, additionally require independent consensus/proof review including dynamic participants, network/economic adversary analysis, concrete dependency/client-maintenance assessment, authenticated light-client/data-availability design, native-currency necessity/security-funding evidence and an upgrade/migration governance proposal. The [expensive commitments](NATIVE_L1_RISKS.md) need explicit approval and an ADR at that time. Finite reference models alone cannot close those dependencies.
