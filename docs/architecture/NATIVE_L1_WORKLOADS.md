# Representative native L1 workloads — Task 017

**2026-10-19; baseline `5ebb298138bc222822af07def0e77b9112bd77bc`. Proposed research scenarios, not implemented applications or demand evidence.** These eight workloads extend [N-01–N-08](NATIVE_L1_RESEARCH.md) under the [common authority/settlement/recovery specification](NATIVE_L1_AUTHORITY_SETTLEMENT_RECOVERY.md) (ASR). All state models receive identical logical actions and inclusion order. [Consensus assumptions](NATIVE_L1_CONSENSUS_ASSUMPTIONS.md), [budgets](NATIVE_L1_RESOURCE_BUDGETS.md) and [next experiment](NATIVE_L1_NEXT_EXPERIMENT.md) are shared dependencies.

Experiments [001](../../research/reports/EXPERIMENT_001_REPORT.md) and [002](../experiments/EXPERIMENT_002_FINAL_REVIEW.md) demonstrate bounded signed consent, deterministic public arithmetic and accounting on a trusted local substrate. They do not demonstrate general delegation, durable restart, independently owned machines, physical truth, permissionless consensus, demand or offline finality. Those are new hypotheses here. The full Genesis vision remains the research target; these scenarios do not require application-specific logic in consensus.

## Shared conventions and invariants

H is a human/operator principal, D a delegate, A/B requester/provider, and S a service provider. Identity is a logical principal with registered signing keys, not evidence of independent ownership or a certified device. Numbers below are dimensionless synthetic test units, not currency policy. Each case starts independently; fee is one unit per admitted action unless a fee-boundary case specifies otherwise. Funded obligations and pending actions are included when assessing available budgets.

| ID | Invariant required in every applicable workload |
| --- | --- |
| I1 | Only explicitly authorized key/role, purpose, recipient and network/version may act. Device identity or AI output alone grants no authority. |
| I2 | At most one admitted execution per logical intent; replay cannot create new principal, fee charge or credit. Independently authorized repeated work is allowed. |
| I3 | Atomic cumulative principal and fee caps across concurrent delegates; no refund, crash, revocation or ambiguous reply replenishes spent authority. |
| I4 | Initial supply equals balances + grant reserves + locked agreements + owner credits + fee sink; no unauthorized mint/burn or wrong-owner payout. |
| I5 | Agreed deterministic predicate and exact signed terms; exclusive claim/refund; collection checked separately. |
| I6 | Inclusion order/time controls expiry and revocation. No second A authorization for W03; no automatic action merely because a deadline passed. |
| I7 | Unknown, orphaned or contradictory evidence is not success and cannot authorize a fresh spend. Recovery never changes recipient, amount or policy silently. |
| I8 | Bounded admission/verification/storage/recovery; deterministic rejection and no numeric overflow or unspecified host data. |

Default logical clock is an integer supplied by the test scheduler, not wall time or a claim about native consensus timestamps. Online profile delivers an action within one tick; intermittent profile withholds delivery across an expiry/revocation boundary; partition profile gives contradictory branch observations until reconciliation. Tick-to-seconds mapping is explicitly absent. Required resource constraints are B1–B9 in the [budget document](NATIVE_L1_RESOURCE_BUDGETS.md); latency failure is measured against stated delivery assumptions, not guaranteed transaction inclusion.

## W01 — human-to-human transfer

- **Participants/authority:** H1 and H2 control distinct principal keys; H1 has balance 100, H2 zero. H1 signs transfer 10, intent sequence 1, fee ceiling 1, expiry tick 20. Neither H2 nor a relay can modify it.
- **Transitions:** at tick 1 include `Transfer(H1,H2,10)`; balances become 89/10 and fee sink 1. Deliver the identical intent again; balances and fees must remain unchanged. New sequence with otherwise identical fields is a separate authorized payment.
- **Success/failure/invariants:** I1–I4/I7–I8; success requires authenticated inclusion and chosen finality evidence, not a broadcast acknowledgment. Wrong key/domain, expiry at 20 or insufficient balance rejects. An authorized semantic failure may pay the declared fee under ASR.
- **Recovery/network:** lose the reply after inclusion, restart from journal, reconcile sequence 1 before permitting another payment. During partition report pending/unknown. Probabilistic confirmation and BFT commit are different evidence profiles.
- **Resources/verification:** B1/B2/B3/B7/B8; chain checks signature, replay, balance, recipient and fee; user intent, privacy and UI confirmation remain off-chain. No physical-service oracle.

## W02 — human-to-agent delegated authority

- **Participants/authority:** H funds a grant G with principal cap 20, fee cap 5, expiry 20, delegates D1/D2, allowed action Transfer and recipient S. Root H is never shared with D. No subdelegation. H has sufficient balance for grant creation and reserve locking.
- **Transitions:** grant creation locks 25 plus pays H's creation fee; D1 spends 12 at tick 2, D2 attempts 9 at tick 3 (cannot succeed), then 8 at tick 4 (can succeed if fee reserve remains). No further principal spend is possible. Test fresh G independently with `Revoke(G)` before/after a spend and expiry at 19/20/21.
- **Success/failure/invariants:** I1–I4/I6–I8; no repeated human approval for in-scope actions. Compromised D may spend all remaining authorized resources but cannot reach H's other funds or another recipient. Grant balance return does not renew lifetime caps.
- **Recovery/network:** stale local grant status cannot override an included revoke. Root-only rotation invalidates old-epoch delegates for future admissions, without canceling funded obligations. Root loss has no assumed recovery service.
- **Resources/verification:** B1–B4/B8; grant/caps/epoch/revocation are ledger-checked; key protection and the agent's purchase decision are operational. Compare one shared G against explicitly partitioned sub-budgets without granting extra aggregate authority.

## W03 — agent-to-agent verifiable work

- **Participants/authority:** A and B sign immutable terms for public sum 7 + 11, price 10, funding deadline 10 and claim deadline 20; A authorizes and funds, B alone can claim. Direct or delegated funding uses the same authority constraints.
- **Transitions:** fund at 9; B claims value 18 at 19, creating B credit 10; B collects that credit. A goes offline after funding. In fresh cases: value 19 rejects; valid claim at 20 rejects and A may refund/collect at 20; no actor leaves the agreement funded. Fund at 10 rejects.
- **Success/failure/invariants:** I1–I8; valid timely claim needs no second A signature. At most one terminal outcome. Disclosure plus no timely claim may leave B unpaid; separately signed identical work may legitimately pay again.
- **Recovery/network:** crash before claim, after claim inclusion and before collection; reconcile actual agreement/credit by owner. Test two-tick funding slack and delivery held until deadline; report refund, not guaranteed provider progress.
- **Resources/verification:** B1–B4/B7–B9; chain recomputes fixed sum and verifies parties/terms; useful demand, effort, confidentiality and AI quality remain unproved. Experiment 001's requester-Acceptance policy is a separate control, never silently substituted for W03.

## W04 — autonomous vehicle payment

- **Participants/authority:** vehicle V uses H's grant capped at principal 10/fees 3, recipient charging station S, Transfer only, expiry 20. A device certificate, if supplied, identifies a device but is not a spending grant.
- **Transitions:** V signs payment 10 with invoice digest/service identifier, then disconnects. Include once at 19 and lose reply; deliver duplicates after reconnect. Fresh case: withhold until 20, so payment is rejected and service cannot be described as paid.
- **Success/failure/invariants:** I1–I4/I6–I8; exactly one payment and bounded fees; no claim that energy was delivered. Invoice remains fixed across recovery. Service supplied against unconfirmed payment is S's explicitly accepted credit risk.
- **Recovery/network:** intermittent, no assumed trusted payment relay; reconnect authenticates grant, intent and finality before retry. No duplicate physical charging guarantee without a separately specified station-side service journal, which receives no architecture credit here.
- **Resources/verification:** B1/B2/B5–B8; chain checks financial authority and stores invoice commitment; meter correctness, service price agreement, safety controls and energy delivery stay off-chain. Station attestations prove assertions, not physical truth.

## W05 — drone or robot coordination

- **Participants/authority:** two fleet delegates D1/D2 share H's grant principal 20/fees 6, recipients S1/S2, Fund only, expiry 20. H and providers sign distinct deterministic sum-u64 coordination-stub agreements upfront; physical mission performance is outside the predicate.
- **Transitions:** both propose funding 12. Fixed order admits at most one successful funding; the other may retry *the same intent* only after authenticated non-admission. A later refund returns funds to H and does not permit the losing 12 under spent G. Interrupt the winning provider after claim, before collection.
- **Success/failure/invariants:** I1–I8; shared reserves include locked work, so concurrency cannot overcommit. Distinct intents/agreements must not overwrite each other. Correct sum is not proof of safe navigation or completed delivery.
- **Recovery/network:** duplicate, delay and reorder both requests; providers resume independently. Recovery collects existing credit once or reports outstanding obligation; no assumption that both machines stay online.
- **Resources/verification:** B1–B4/B6/B8–B9; chain validates budget and fixed work relation. Dispatch, scheduling, physical safety and service truth remain applications. No fleet-wide trusted coordinator is assumed in the model.

## W06 — satellite or remote-machine participation

- **Participants/authority:** remote D holds a grant to S, principal 10/fees 3, expiry 20; role is a light or relayed client, not necessarily a validator. A relay is untrusted and can drop/reorder messages.
- **Transitions:** prepare payment at tick 2; deliver once at 19 in one case and at 21 in another. Separately include revoke at 5 before delivery. D reconnects with a stale checkpoint while an attacker supplies an alternative history.
- **Success/failure/invariants:** I1–I4/I6–I8; timely unrevoked included payment can succeed; late/revoked payment rejects. No final success based on stale history or relay consensus claims. Long disconnection may require a new independently established trust anchor.
- **Recovery/network:** delay sweeps and long partitions in B7; identify which proof/checkpoint source and data are missing, then abstain. Do not claim secure offline transfer, eventual delivery or satellite-wide consensus liveness.
- **Resources/verification:** B1/B5–B8; chain checks current authority at inclusion; client verifies finality/inclusion/state under its declared trust profile. Link availability, clock discipline and physical antenna/security controls are outside the ledger.

## W07 — adversarial authority and recovery

- **Participants/authority:** adversary obtains D's key, not H's; scope and reserves as W02. RPC/relay may equivocate; honest finality evidence is available only in the recovery control.
- **Transitions:** submit wrong recipient, over-cap, old epoch and cross-network intents; fork observation after a valid spend; crash before/after journal write, signature, submission, inclusion and credit observation. Restore old journal snapshot and attempt a fresh sequence.
- **Success/failure/invariants:** I1–I8; all out-of-scope financial actions reject; valid malicious in-scope spend is expected, not a prevention claim. Any conflicting success observations latch signing until authenticated reconciliation.
- **Recovery/network:** revoke/rotate races obey canonical order. Root compromise defeats its granted policy; stolen data, hostile OS, erased journals and physical service against stale authority require operational controls. A coherently dishonest proof/trust-anchor provider is outside the authenticated-evidence premise, not “fixed” by repeated matching RPC reads.
- **Resources/verification:** all budgets, especially B2/B8/B9; chain prevents replay/overspend using durable state, while journal/key isolation and stopping on uncertain evidence are client obligations. Invalid-message CPU/DoS exposure is separately measured.

## W08 — concurrent autonomous economic activity

- **Participants/authority:** 1/8/32 synthetic clients, independent principals or two delegates per root; every root has the *same total* initial resources at each concurrency level. These are fixtures, not users or adoption evidence.
- **Transitions:** mix W01 transfers and W03 independent agreements; run disjoint-state, half-shared and all-shared grant/recipient cases. Hold logical intent set and acceptance order fixed across models. Repeat with lost replies, stale references and reconnect; compare shared grant with partitioned reserves of the same total size.
- **Success/failure/invariants:** I1–I8; independent valid intents must not be lost or double-executed. Conflicting intent order may change the winner, not budgets. No throughput benefit may come from extra authority, dropping failed requests or omitting recovery.
- **Recovery/network:** all partitions/delays explicitly scheduled; fairness is measured, not assumed. Distinguish logical semantic rejection, candidate structural conflict, non-inclusion and unknown outcome.
- **Resources/verification:** B1–B9; measure conflicts, retries, serialized bottlenecks, state/bytes per logical success and independent verification. Market discovery, real service demand and machine ownership stay off-chain and unvalidated.
