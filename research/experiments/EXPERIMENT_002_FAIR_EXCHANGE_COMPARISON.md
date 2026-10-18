# Experiment 002: Fair-Exchange Research Comparison

**RASL / Genesis — 2026-10-18 — research proposal, not implementation or a result.**

## Question, scope and evidence boundary

Can an independently controlled provider collect a previously authorized payment for objectively correct work without a second requester approval? [Experiment 001](../reports/EXPERIMENT_001_REPORT.md) achieved **CONDITIONAL PASS**, with 58 Solidity and 54 Python tests at its published validation milestone. Its requester can learn the correct result, withhold Acceptance, and recover the principal after timeout. Those findings and semantics remain unchanged.

This focused review compares six established mechanism families. Primary papers, specifications, documentation and selected public source files were inspected on 2026-10-18. It is not an exhaustive literature review, code audit, proof reproduction, implementation benchmark or claim of novelty. Source descriptions below report what was inspected; architecture suitability and the recommendation are **research judgments**, not measured findings. No Experiment 002 tests have run.

Genesis remains research into permissionless economic infrastructure for humans, AI/software agents, robots, machines, vehicles, satellites, sensors, distributed systems and future participants. An independent network remains an open direction; service payment is one bounded research instrument.

## What “fair” means here

Distinguish four properties rather than reporting one fairness score:

1. **Payment safety:** an invalid or unauthorized claim cannot acquire requester principal.
2. **Conditional provider collectability:** once funded, a valid claim included before its deadline can pay without further requester cooperation.
3. **Delivery:** the requester can recover the specified output from available evidence.
4. **Strong exchange fairness:** neither party obtains the other's agreed benefit while withholding its own, under an explicitly stated model.

Property 2 does not establish property 4. Public transaction data can reveal work before successful inclusion; censorship or a deadline may then prevent payment. No finite timeout simultaneously guarantees eventual payment and eventual refund under arbitrary communication failure. This is a limitation of the proposed environment/model, not a claimed universal impossibility theorem.

## Work classes

| Work class | What can be checked | Remaining trust or gap |
| --- | --- | --- |
| Cheap deterministic digital service | Exact public program/input/output relation, recomputed by the settlement verifier. | Correct program specification, input provenance and ledger behavior; checking addition does not demonstrate useful outsourcing. |
| Expensive deterministic computation | Execution traces, fraud proofs or cryptographic computation proofs for a fixed program and bound inputs. | Proof/VM correctness, data availability, costs and potentially honest monitoring; execution truth differs from useful or correct task specification. |
| Committed digital goods | Delivered bits match an agreed digest or publicly checkable relation. | Buyer must know what the digest means; commitments alone cannot establish quality or correctness of an unknown result. |
| Subjective AI output | Format, deterministic scoring rubric, or agreed evaluator judgment. | Rubric gaming and disagreement remain; reproducible model execution does not prove helpfulness, truth or satisfaction. |
| Physical work and sensing | Signed measurements or external testimony. | Sensor authenticity, calibration, location and oracle/adjudicator trust; a signature proves who asserted something, not that it happened. |

## Mechanism comparison

Costs below are qualitative dependencies, not measured gas, latency, throughput or economic-security estimates. “No fixed chain” means portable required primitives, not universal compatibility.

### M1 — Direct deterministic verification with contingent escrow

**Operation:** both parties sign exact service terms; requester prefunds an immutable obligation. The provider submits the result, and a deterministic settlement predicate checks it without requesting another requester signature. Experiment 001 already checks arithmetic but additionally requires Acceptance; this proposal explicitly removes that additional gate in a separate experiment. [EIP-712](https://eips.ethereum.org/EIPS/eip-712) supports typed consent and domain separation, not replay prevention or fairness by itself.

**Trust/work:** program and input correctness, signature libraries, verifier and ledger execution/inclusion. Suitable for cheap objectively checkable digital relations. **Dishonesty:** requester silence cannot veto a timely valid claim; an incorrect provider result fails the predicate. **Cost/latency:** full predicate execution per claim, funding/claim/withdraw transactions and deadline wait for refund. **Limits:** expensive recomputation scales poorly; public work may leak before payment, deadlines/censorship can deny compensation, and effort is not proven. **Architecture:** needs programmable escrow, authenticated consent and bounded time/order semantics; no particular L1 or consensus follows.

### M2 — Optimistic assertion, challenge period and fraud-proof resolution

**Operation:** accept assertions after a window unless challenged; disputes reduce a deterministic execution disagreement to an objectively adjudicated step. The [OP Stack dispute specification](https://specs.optimism.io/fault-proof/stage-one/fault-dispute-game.html) is a concrete rollup example, not a ready-made autonomous-service settlement protocol. Its [honest challenger specification](https://specs.optimism.io/fault-proof/stage-one/honest-challenger-fdg.html) documents the monitoring/trace role.

**Trust/work:** at least one appropriately informed, online, funded challenger with timely inclusion, correct VM and available trace/input data. **Dishonesty:** false provider assertions need effective challenges; false requester challenges must lose by objective adjudication rather than impose a veto. **Cost/latency:** monitoring and bonds, mandatory dispute window, potentially many dispute transactions and worst-case verification costs. **Limits:** silence is not truth; offline/censored challengers and griefing undermine guarantees. Incentives alone do not establish honest participation. **Architecture:** timed disputes and proof adjudication required; OP's implementation is EVM/rollup-specific, the family is broader. Deferred until workload costs justify its extra assumptions.

### M3 — Committed encrypted delivery and FairSwap-style disputes

**Operation:** exchange encrypted digital goods bound to commitments, lock payment, reveal a key, and allow objectively checkable complaints. [FairSwap, Dziembowski, Eckey and Faust, CCS 2018](https://eprint.iacr.org/2018/740) studies smart-contract-mediated digital-goods exchange. The [author-associated prototype](https://github.com/lEthDev/FairSwap/tree/07f5664de64e232a0e1a8c0a84eefc223b45ae8b) contains key revelation, file-root checks and complaint paths, and explicitly warns that it is unaudited.

**Trust/work:** agreed meaning of the goods/root, ciphertext availability, correct judge and timely complaint inclusion. **Dishonesty:** incorrect encryption/content relations can be disputed; buyer inactivity can allow payment once the prescribed conditions hold. **Cost/latency:** ciphertext distribution, commitments, key release and complaint window; disputes add proof checks. **Limits:** a hash binds bits, not usefulness or unknown computation correctness; key leakage and timing require the construction's exact model. **Architecture:** the inspected prototype uses Ethereum; adapting its protocol requires reviewing ledger assumptions. Its security claims do not transfer to an improvised Genesis variant. Deferred for a future confidential or large-goods question.

### M4 — Optimistic trusted-third-party fair exchange

**Operation:** parties exchange verifiable conditional artifacts; an external resolver handles abort/resolve when normal exchange fails. [Asokan, Shoup and Waidner, S&P 1998](https://research.ibm.com/publications/asynchronous-protocols-for-optimistic-fair-exchange) documents asynchronous exception resolution and temporary channel failures.

**Trust/work:** correct, available and consistent third-party behavior plus the protocol's cryptographic relations. Suitable for specified digital artifacts; subjective services additionally require an agreed human or machine judgment process. **Dishonesty:** either side may invoke resolution instead of depending on its peer's final cooperation; resolver inconsistency or collusion remains a risk. **Cost/latency:** ordinary exchange can avoid the resolver, but disputes add availability, operational and judgment costs. **Limits:** centralized censorship/capture, evidence ambiguity and resolver trust do not disappear by calling it decentralized arbitration. **Architecture:** no blockchain inherently required. A federated or community resolver is another assumption, not a cryptographic solution. Useful comparison, deferred from the permissionless bounded baseline.

### M5 — Payment channels and hash-time-locked exchange

**Operation:** lock conditional payment to a hash preimage, exchange signed channel updates, and use ledger timeout/settlement fallback. [Lightning BOLT 2](https://github.com/lightning/bolts/blob/1aadb719b4007c4cea0ba6e36b08c4fb53788dee/02-peer-protocol.md) specifies preimage checks; [BOLT 3](https://github.com/lightning/bolts/blob/1aadb719b4007c4cea0ba6e36b08c4fb53788dee/03-transactions.md) specifies transaction and timeout constructions.

**Trust/work:** correct channel state, liquidity, monitoring or delegated watchers, and fallback transaction inclusion. **Dishonesty:** valid preimage fulfillment can collect despite requester silence; stale-state and timeout attacks require channel defenses. **Cost/latency:** channel setup/close, locked liquidity and monitoring; ordinary updates may avoid per-service ledger transactions, disputes do not. **Limits:** a valid preimage alone proves neither correct computation nor useful delivery; associating it with correct encrypted work needs an additional reviewed protocol. **Architecture:** Lightning specifically uses Bitcoin transaction primitives; other channels have different ledger requirements. Deferred until repeated-exchange economics and delivery binding are the research question.

### M6 — Proof-verified computation with contingent payment

**Operation:** bind agreed program, input commitments and output to a computation proof; a verifier checks it before escrow release. [RISC Zero receipts](https://dev.risczero.com/api/zkvm/receipts) bind public journal output to an expected program image ID. This is an example of verifiable execution, not a fairness protocol by itself.

**Trust/work:** proof-system soundness, exact program/input binding, verifier/compiler correctness and whatever setup assumptions the chosen proof composition needs. **Dishonesty:** invalid executions should not verify; requester silence need not veto a funded proof-based claim. **Cost/latency:** proof generation, verification, proof data and possibly substantial hardware demand; no measurements made here. **Limits:** a proof of execution does not prove truthful physical inputs, subjective quality, output availability or actual payment. Wrong image IDs or development-mode receipts defeat intended assurances. **Architecture:** proofs can be verified off-chain or in compatible settlement systems; on-chain cost and supported cryptography vary. Deferred until direct verification has a demonstrated bottleneck.

## Comparative selection

| Family | Handles requester veto? | Principal extra assumption | Suitable first workload | Recommendation |
| --- | --- | --- | --- | --- |
| M1 direct predicate | Yes, for a funded valid claim included in time. | Correct cheap predicate and ledger. | Public bounded arithmetic. | Propose as Experiment 002 baseline. |
| M2 optimistic disputes | Conditionally, after objective dispute resolution. | Effective honest monitoring and trace availability. | Expensive deterministic VM execution. | Defer; larger failure model. |
| M3 encrypted goods | Under the reviewed exchange protocol's assumptions. | Committed goods relation and complaint availability. | Known-digest digital file. | Defer; different delivery question. |
| M4 external resolver | If resolver correctly resolves. | Trusted dispute authority. | Agreed verifiable artifacts or judged work. | Comparison only. |
| M5 channels/HTLC | For the payment condition, not arbitrary service truth. | Live channel defense and service/preimage binding. | Repeated payments or reviewed key exchange. | Defer. |
| M6 computation proof | For funded, timely, correctly bound proof claims. | Proof/verifier stack and output availability. | Expensive deterministic computation. | Defer pending cost evidence. |

**RESEARCH HYPOTHESIS:** replacing post-result requester Acceptance with explicit upfront consent to an immutable deterministic payment predicate removes that veto for timely valid claims, while retaining authorization caps, identity binding, replay protection and deterministic refunds. It does not guarantee payment for all honest effort or strong exchange fairness.

Recommend M1 because it isolates the veto variable with the smallest additional mechanism and no challenger, adjudicator, encryption or proof system. Keep the same public addition task for a controlled comparison, openly acknowledging that it is too trivial to justify outsourcing. A failure even here is valuable evidence against expanding the design. See the [proposed experiment](../../docs/experiments/EXPERIMENT_002.md), [architecture](../../docs/architecture/EXPERIMENT_002_ARCHITECTURE.md), [threat model](../../docs/experiments/EXPERIMENT_002_THREAT_MODEL.md), [test plan](../../docs/experiments/EXPERIMENT_002_TEST_PLAN.md) and [proposed ADR 0002](../../docs/adr/0002-experiment-002-fair-exchange.md).

## Primary sources and inspected open-source evidence

These immutable snapshots are research references, **not adopted dependencies**. Selected-file inspection does not establish audit status, security, licensing suitability or compatibility for reuse.

| Reference | Evidence inspected and research relevance |
| --- | --- |
| [FairSwap paper metadata/abstract, 2018/740](https://eprint.iacr.org/2018/740) | Authors, CCS 2018 publication, DOI 10.1145/3243734.3243857, digital-goods and smart-contract judge model verified. PDF retrieval failed; no full-paper proof review claimed. |
| [FairSwap README](https://github.com/lEthDev/FairSwap/blob/07f5664de64e232a0e1a8c0a84eefc223b45ae8b/README.md) and [FairFileSale.sol](https://github.com/lEthDev/FairSwap/blob/07f5664de64e232a0e1a8c0a84eefc223b45ae8b/FairFileSale.sol) | README and selected contract paths inspected; Solidity ^0.4.23, template placeholders, timed complaints and unaudited warning. Historical example; do not copy into current tooling. |
| [ASW asynchronous fair-exchange paper record](https://research.ibm.com/publications/asynchronous-protocols-for-optimistic-fair-exchange) | IBM publication abstract, authors and S&P 1998 venue verified. Related [author-hosted signature-exchange paper](https://www.shoup.net/papers/fex.pdf) was located, but text extraction was unreadable; no full construction review claimed. |
| [Teutsch and Reitwießner, A scalable verification solution for blockchains](https://arxiv.org/abs/1908.04756) | Abstract-level prior art for an incentive layer over verification games; arXiv record is 2019, author-hosted draft dated 2017. Not a completed analysis of Truebit's incentives or any current deployed product. |
| [OP fault dispute specification](https://specs.optimism.io/fault-proof/stage-one/fault-dispute-game.html), [honest challenger](https://specs.optimism.io/fault-proof/stage-one/honest-challenger-fdg.html), [implementation](https://github.com/ethereum-optimism/optimism/blob/9c14635375e22608458da1d3ec4830af491009dd/packages/contracts-bedrock/src/dispute/FaultDisputeGame.sol) | Specification and selected implementation declarations inspected: claims, clocks, step verification and bond/accounting machinery. No source audit or service-market adaptation tested. |
| [Lightning BOLT 2](https://github.com/lightning/bolts/blob/1aadb719b4007c4cea0ba6e36b08c4fb53788dee/02-peer-protocol.md), [BOLT 3](https://github.com/lightning/bolts/blob/1aadb719b4007c4cea0ba6e36b08c4fb53788dee/03-transactions.md), [Core Lightning README](https://github.com/ElementsProject/lightning/blob/5959fd15a7b125c43645a86b90ff85fbc91b4a80/README.md) | Protocol condition/timeout references and implementation README inspected. Core Lightning is an open-source implementation reference; not installed, run or audited here. |
| [RISC Zero receipt documentation](https://dev.risczero.com/api/zkvm/receipts), [source README](https://github.com/risc0/risc0/blob/3bbcd44d6459b9ef6ac0df3846dc9215514934e8/README.md) | Journal, seal, expected image ID, RISC-V execution and development-branch warning inspected. No prover/verifier benchmarks or independent proof-system assessment performed. Documentation version displayed 3.0; snapshot is a research reference, not a release choice. |
| [EIP-712](https://eips.ethereum.org/EIPS/eip-712) | Established typed-data/domain standard; replay protection must be supplied by the application. Existing Genesis signatures use this standard; no new primitive proposed. |

## Unresolved research questions

- What useful task has cheap objective verification but material external computation cost?
- How can output confidentiality, availability and payment be bound without leaking usable work before inclusion?
- What inclusion/finality assumptions are acceptable for robots, intermittently connected devices and satellite links? A longer timeout is not a solution to arbitrary delay.
- When does a challenger/proof system reduce total costs enough to justify new failure modes?
- How should subjective or physical outcomes be adjudicated without disguising oracle trust?
- Can a future independent network meet these requirements more effectively than existing or non-chain systems? This experiment cannot answer that.

Before implementation, review the proposed consent change and bounded claim, exact schemas, test budget, dependency maintenance and ledger assumptions. A separate authorization is required; this task selects no production or irreversible architecture.
