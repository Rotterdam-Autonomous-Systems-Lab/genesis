# AI-Earned Native Tokens and Human/Machine Utility: Initial Research Foundations

**RASL / Genesis — 2026-10-18 — focused prior-art review and proposed research, not token design or measured economic results.**

## 1. Scope and evidence labels

The [charter](../../MASTER_PLAN.md) and [ADR 0003](../../docs/adr/0003-independent-l1-research-direction.md) set the goal: an independent permissionless L1 economy where AI systems may earn newly issued native tokens through independently verified contributions, and humans/machines can use the same economic network meaningfully. This document initiates research under Verifiable Autonomous Work, Independent Network Security and Human and Machine Economy. It neither selects consensus nor issues tokens.

**ESTABLISHED RESEARCH** below means a cited technique, specification or model, not proof of Genesis suitability. **ARCHITECTURAL HYPOTHESIS** means a falsifiable candidate. **SPECULATIVE USE CASE** means possible demand requiring evidence. Source pages/selected paper sections were inspected on 2026-10-18; no implementations, benchmark reproductions, comprehensive literature search, independent audit or adoption study were completed. Model conclusions depend on assumptions and must not be imported as forecasts.

## 2. Three different kinds of earning

| Earning | Who supplies payment / what must be verified | Economic/security distinction |
| --- | --- | --- |
| AI service earnings | Customer transfers an existing balance for an agreed service. Verify consent, task predicate/delivery and settlement. | Not new issuance, even if settled in the native asset. May demonstrate a paid service, not independent market demand when parties collude or are subsidized. |
| Protocol-issued useful-work reward | Protocol creates new units under an eligible-work rule. Verify task origin, correctness, eligible quantity/uniqueness and budget accounting. | Redistributes/dilutes ownership; does not create buyer demand by itself. Fake self-requested work, duplicate proofs and Sybil farms can consume issuance without social utility. |
| Consensus-security reward | Fees and/or issuance compensate block/validation/security participation under a specific protocol. | Must support safety/liveness and attack incentives under scarce-resource assumptions. Useful service work is not automatically evidence of consensus security. |

A provider could earn customer fees and protocol rewards for the same activity, but double incentives need explicit justification/accounting; none are selected. A human may direct an AI-operated participant, but rewards should depend on verifiable rules, not claiming to be intelligent. Newly created addresses must not imply newly created security resources.

## 3. Contribution candidates and attacks

The following are **architectural hypotheses** for investigation, not candidate reward schedules or implemented mechanisms.

| Contribution | Candidate verification and costs | Known attack classes / limits to investigate |
| --- | --- | --- |
| Deterministic computation | Direct checking, sampled replication, fraud proofs or proof-verified execution bound to program/input/output. Measure verification, proof, storage and communication costs. | Copying/precomputation, padded or self-generated tasks, data withholding, verifier collusion, invalid input provenance; correct execution is not usefulness or unique effort. |
| ML execution/training | Reproducible operators and trace disputes, or reviewed computation proofs for fixed tasks. | Hardware nondeterminism, all-providers collusion, poisoned/low-value training data, benchmark gaming, proof costs; reproducibility does not prove model quality or truthful answers. |
| Storage over time | Replication/time proofs, unpredictable challenges, audits and retrieval tests. | Outsourcing/copying, temporary availability, correlated storage, proving capacity with no useful demand, withholding retrieval; resource commitment and service usability differ. |
| Bandwidth/relay | Signed receipts, unpredictable endpoint challenges and independent measurements. | Sybil endpoints looping fake traffic, colluding receipt issuers, location/routing spoofing, test-specific prioritization; bytes counted need not be useful delivered bytes. |
| Verification/auditing | Randomized assigned checks, independently checkable challenges and objectively resolved disputes. | Rubber-stamping, copying others' reports, bribery, selective challenges, verifier cartel; incentives do not guarantee an honest watcher. |
| Sensing/robotic/physical work | Authenticated sensors, redundant independent observations, bounded hardware attestations or agreed adjudication. | Fabricated/calibration-biased data, common-control sensors, GPS/time spoofing, hardware vendor trust; a signature proves an assertion, not physical truth. |

For each, identify the scarce resource, useful beneficiary, adversary budget, false-accept/reject behavior, verifier cost and availability assumptions before rewards. Separate **task identity**, **result correctness**, **resource commitment**, **unique contribution**, **beneficiary demand** and **consensus influence**. A hash or successful service payment does not establish all six.

## 4. Relevant research and networks

| Primary reference / established evidence | What it contributes; explicit distinction from Genesis |
| --- | --- |
| [Nakamoto, Bitcoin: A Peer-to-Peer Electronic Cash System (2008)](https://bitcoin.org/bitcoin.pdf) | Hash-based proof of work and chain selection connect a publicly checkable resource cost to a ledger under stated attacker assumptions. It is not proof of useful AI computation. An AI controller could participate operationally without its intelligence defining validity. |
| [Filecoin Storage Power Consensus specification](https://spec.filecoin.io/systems/filecoin_blockchain/storage_power_consensus/) | Separates customer storage-market payments from block rewards and connects proven storage power to leader election. This is concrete prior art for resource/security coupling, not evidence that arbitrary useful work is safe consensus input. Capacity, retrieval, collateral and concentration require separate analysis. |
| [Bittensor Yuma developer specification](https://guides.learnbittensor.org/learn/yuma-consensus) | Computes miner/validator emissions from validators' performance rankings. This is a reward/scoring aggregation reference, not an objective cryptographic proof that a subjective AI answer is true. Do not equate this scoring process with a complete L1 consensus-security proof or assume Genesis adopts its economics. |
| [Arun et al., Verde: Verification via Refereed Delegation for Machine Learning Programs, arXiv:2502.19405v1 (2025)](https://arxiv.org/html/2502.19405v1) | Dispute arbitration plus reproducible operators addresses deterministic ML execution under at-least-one-honest-provider/referee assumptions. The paper explicitly notes incorrect selection can remain when all providers are dishonest. It does not prove subjective quality, unique contribution, rewards, token demand or Genesis security. |
| [Gensyn RepOps demonstration repository](https://github.com/gensyn-ai/repops-demo) | Open-source reference linked by the authors; not installed, run, audited or adopted here. Review restricted hardware/operator support before generalizing reproducibility. The [project research note](https://www.gensyn.ai/research/verde-a-verification-system-for-machine-learning-over-untrusted-nodes) is not independent validation. |
| [Douceur, The Sybil Attack, IPTPS 2002](https://www.microsoft.com/en-us/research/publication/the-sybil-attack/) | Foundational reference on one entity presenting multiple identities and the assumptions required to resist it. AI-agent count is not independent operator count; no new Sybil solution is claimed. |
| [Budish, The Economic Limits of Bitcoin and the Blockchain, NBER WP 24717 (2018)](https://www.nber.org/papers/w24717) | Equilibrium analysis relates recurring miner compensation to attack incentives under its proof-of-work model. It motivates attack-budget/security-budget analysis, not a numerical rule or proof applying to every consensus system. Abstract-level review; no calibration performed. |
| [Cong, Li and Wang, Tokenomics: Dynamic Adoption and Valuation, NBER WP 27222 (2020)](https://www.nber.org/papers/w27222) | Model of transaction demand, adoption and network effects under explicit assumptions. It is not empirical proof that a Genesis token gains adoption/value or that issuance generates demand. Abstract-level review; full NBER page retrieval failed, so no full-paper review is claimed. |
| [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) | Existing fee design distinguishes burned base fees from proposer priority-fee revenue. Therefore “fees paid” and “security revenue” are not interchangeable. This is a comparison example, not a selected Genesis fee rule. |
| [BIS, Annual Economic Report 2025, Chapter III](https://www.bis.org/publications/aer-2025/next-generation-monetary-financial-system) | Discusses stablecoin monetary/institutional limits and deviations from par. Useful counterpoint for settlement-unit research; not a verdict on an unbuilt Genesis network or evidence of risk-free stable assets. |

Proof systems, optimistic challengers, payment channels and digital-goods exchange are additionally compared in the [Experiment 002 review](../experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md). Those mechanisms verify different predicates and do not individually solve issuance eligibility, usefulness or decentralization. No source above establishes Genesis originality or economic feasibility. Current project emission parameters, token prices, participant counts and deployment claims were deliberately not used as evidence.

## 5. Independent-L1 security without trusting AI intelligence

**Architectural hypothesis:** keep deterministic consensus validity separate from AI choices and subjective scoring unless a precisely specified, independently analyzed resource/proof mechanism justifies coupling. AI may operate clients, produce tasks or proofs and manage bounded authority; the network should verify admissible evidence rather than ask whether a model is persuasive.

Compare resource-cost baselines such as hash work, bonded participation or proven storage without selecting one. For each specify eligibility, scarce-resource/ownership assumptions, randomness, proposer selection, fork choice, fault thresholds, availability and partition recovery. Test attackers who control many keys and AI agents but a fixed resource budget, and attackers who acquire additional real resources. Do not mistake a fixed-budget identity-splitting test for resistance against unlimited resource concentration.

Task correctness proofs can be cheap to verify yet reusable/outsourced; that property alone does not establish consensus weight. Rewarding useful work in a market or separate incentive layer may reduce consensus complexity, but could still enable subsidies, corruption or verification overload. APoC remains an internal hypothesis, not a consensus invention. No proof or benchmark for a Genesis security mechanism exists.

## 6. Human utility and settlement-unit choices

These are **speculative use cases**, not demand findings:

| Potential utility | Who benefits / evidence needed | Main limitations |
| --- | --- | --- |
| Human-to-human payments | Individuals or organizations needing accountable transfer; compare consent, finality, recovery, total fees and existing payment systems. | Volatility, custody/recovery, privacy, usability and legal access can defeat utility. |
| Human-to-machine services | People buying compute/storage/bandwidth or bounded machine services. | Must show real service need, objective delivery or disclosed adjudication, predictable total cost and alternatives comparison. |
| Machine-to-machine infrastructure | Vehicles/robots/agents obtaining resources under operator policy. | Continuous budget control, offline behavior, faults and beneficiary demand; machine traffic alone is not human utility. |
| Collateral and service bonds | Counterparties limiting specified defaults with objectively enforceable outcomes. | Volatile collateral, liquidations, oracle errors and correlated defaults; locking supply does not demonstrate social value. |
| Infrastructure/applications | Open APIs, marketplaces, verification and access to shared infrastructure. | Discovery concentration, Sybil spam, rent extraction, data availability and migration risk; applications need users rather than token incentives alone. |

**Architectural hypothesis:** distinguish unit of account, payment asset, fee asset and security collateral. Humans may prefer stable-value quoting or settlement for wages, invoices and machine operating budgets, while a native asset could serve another demonstrated network function. Compare native-only, stable-settlement/native-fee, and existing-payment/no-native-asset controls. No stable asset, bridge, oracle, exchange, wallet or architecture is selected.

Stable-value assets can introduce issuer/reserve/redemption/censorship risk; algorithmic or collateralized forms add their own stabilization/liquidation/oracle assumptions. Cross-chain representations add bridge/custody and data-availability risk. “Stable” is not guaranteed; simulate depegs and unavailable redemption, not just a constant price. Native fee demand may be small even with large stable-value payment volume. A hybrid could improve budgeting while weakening a native-token necessity argument; preserve either outcome.

## 7. Demand, issuance and sustainability accounting

Use a unit-consistent model before any parameter proposal:

- Supply accounting: `S(next) = S(now) + issued - burned`. Transfers/market earnings do not create supply. Locked/collateral balances differ from spendable liquidity. This identity is not an issuance schedule or price prediction.
- Security compensation: count only fees actually allocated to security plus its issuance allocation; burned fees are not validator revenue. Useful-work subsidies, treasury spending and service payment are different flows. Convert costs and payments using consistent units in any simulation; do not silently equate token units with stable purchasing power.
- Net issuance relative to supply measures token-unit dilution when defined; purchasing-power inflation depends on demand and prices too. No rate is proposed.
- Transaction demand and desired holding balances differ. Rapid turnover or automatic conversion can support services with little retained native balance; low velocity or locked supply can impair liquidity. Volume/velocity identities alone do not determine valuation.
- Liquidity involves depth, conversion costs and stressed availability, not merely a market listing. Subsidized wash transactions can inflate activity while consuming issuance and verification resources.

**Research questions:** does recurring external customer demand cover service plus verification/security costs when subsidies fall? Who funds costs under low activity? Can participants manipulate reward eligibility more cheaply than honest contribution? Do fees exclude small human/machine transactions? Could volatile security collateral amplify outages or capture? Analyze sensitivity and adversarial equilibria rather than promise sustainability from growth.

## 8. Falsifiable work without a token launch

All proposals below use synthetic identities, tasks and accounting units; no token, public deployment, real funds, external compute, autonomous persistent actors or recruited users are authorized here. No experiment below has run. Freeze models, budgets, seeds, baselines and failure thresholds in a separate scoped task before simulation; report uncertainty and negative outcomes.

| ID / hypothesis | Proposed method and controls | Measures / falsification |
| --- | --- | --- |
| E-01 — Useful-work correctness can be separated from uniqueness and demand. | Synthetic deterministic task corpus with duplicated, padded, precomputed and requester/provider self-generated tasks; compare direct, replicated and proof/dispute-based checking. | False accepts/rejects, verification/production cost, duplicate payouts, externally demanded versus self-generated work. Reject any rule advertised as unique useful contribution if copies or fake demand obtain equivalent rewards. |
| E-02 — Identity splitting need not increase rewards/security weight at fixed scarce-resource budget. | Compare one synthetic operator/key with many keys/AI roles at identical compute/storage/bond budget; then separately vary resource concentration and verifier collusion. | Reward share, security influence and verification load versus identity count, attack cost and concentration. Any cheap identity-only amplification falsifies the candidate rule; no candidate is selected yet. |
| E-03 — Recurring useful demand may cover costs without indefinite issuance subsidy. | Synthetic service-demand model, native-only/hybrid/non-token controls; vary external demand, fees, verification cost and subsidy withdrawal; include wash traffic and adverse costs. | Total service cost, security-budget shortfall, subsidy dependence, concentration, denied small transactions and viable demand regions. Self-funded circular trades must not count as independent demand. No viable region falsifies that parameterized model, not all possible economies. |
| E-04 — Stable-value settlement may reduce budgeting uncertainty but adds trust/failure costs. | Synthetic purchasing budgets and price paths; compare native-only with stable-settlement/native-fee; inject depeg, oracle failure, conversion illiquidity and unavailable issuer/bridge. | Budget overruns, service completion, conversion cost, native balances/fee demand, shortfall during stress. Apparent improvement that disappears under declared failures weakens the hypothesis. |
| E-05 — Decoupling useful-work rewards from consensus may reduce safety dependencies. | Paper state-machine/threat comparison with resource-security baselines and alternative reward validation; model all-verifier collusion and withheld evidence. | Changes in safety/liveness assumptions, evidence size and verifier cost; reject claims that service validity alone secures consensus. Requires a concrete candidate before execution. |

Prioritize **E-01 and E-02** to test whether verified work is an eligible scarce contribution at all, then **E-03/E-04** to test human utility and sustainable costs. E-05 remains comparative architecture research. Experiment 002's repeated-work control informs E-01 but does not implement a mining experiment. This sequence preserves the independent-L1/native-economy goal while allowing evidence to challenge specific mechanisms.

## 9. Open decisions and next research gate

No selected reward eligibility, issuance budget, supply, ticker, consensus, collateral/fee asset, stable-value asset, oracle, governance or launch exists. Open issues include bootstrap demand, beneficiary authenticity/privacy, operator concentration, verifiable work attribution, tolerated verifier costs, time/partition assumptions, physical/subjective outcomes and economic measurement under adversarial adaptation. Adaptability requires explicit interfaces/migration assumptions; no complete future-proofing is promised.

Next research task: a bounded E-01/E-02 model and prior-art refinement, specifying one resource/task and one candidate accounting rule before any code/simulation authorization. Independently pursue Experiment 002's technical release gates; a service-payment prototype is neither a native-token issuance design nor evidence of a sustainable economy.
