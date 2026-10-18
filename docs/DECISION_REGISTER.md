# Decision Register

This register records project decisions and the boundaries around unresolved matters. “Confirmed” means established by the project owner’s instructions and current charter; it does not mean technically proven. Material changes require explicit review and a corresponding ADR. For technical context and historical ideas, see `research/history/`.

## Confirmed decisions

| ID | Decision | Consequence / boundary |
| --- | --- | --- |
| D-001 | Rotterdam Autonomous Systems Lab (RASL) is the research organization. | Genesis research is attributed to RASL; this does not establish legal structure beyond the stated organization. |
| D-002 | Genesis is the temporary project codename. | A permanent protocol or network name has not been selected. |
| D-003 | Development is open-source and research-first. | Prior art, assumptions, methods, failures, and uncertainty should be documented before implementation claims. |
| D-004 | Security and verifiability are primary principles. | Do not rely on participant intelligence or good intentions where actions can be independently bounded and verified. |
| D-005 | The original cross-cutting technical tracks are: Autonomous Economic Authority, Verifiable Coordination, and Autonomous Network Security. | Retained as technical methods; Task 006 organizes planning around the connected pillars in D-015. Do not collapse the whole mission into one track or app. |
| D-006 | A small two-agent experiment is the first implementation milestone. | It is an early step toward a larger network; its exact design, platform, scope, and acceptance details still require a research task and review. |
| D-007 | No premature token issuance. | No ticker, tokenomics parameters, presale, launch date, or issuance schedule is approved. |
| D-008 | No premature consensus claims. | Genesis has not invented or validated a new consensus protocol; APoC remains a hypothesis. |
| D-009 | No uncontrolled autonomous replication or unauthorized infrastructure use. | Experiments must remain bounded and authorized; do not self-propagate or consume third-party resources without authorization. |
| D-010 | Ethereum is not a permanent commitment as final architecture. | Existing chains may be experimental platforms or comparison points; Task 006 makes an independent permissionless L1 the research goal; no final implementation/consensus is selected. |
| D-011 | No final network brand, ticker, or consensus algorithm is selected. | Names and mechanisms remain open pending research and review. |
| D-012 | Historical brainstorms must remain distinguishable from decisions. | Preserve ideas as historical material without presenting them as approved design. |
| D-013 | Public repository materials must not contain credentials or secrets. | Local-only sensitive or unpolished notes belong under ignored `internal/`; public history documents must be suitable for release. |
| D-014 | Task 006 explicitly sets an independent permissionless L1/native human-and-machine economy as the long-term research goal. | Investigate AI mining/earning through independently verified contributions and genuine utility for the same asset across human-to-human, human-to-machine and machine-to-machine activity. Research direction only; no validated design, asset issuance, parameters or sustainable outcome approved. See ADR 0003. |
| D-015 | Task 006 organizes planning around Verifiable Autonomous Work, Independent Network Security, and Human and Machine Economy. | Preserve D-005's technical tracks as cross-cutting methods; test useful work, AI Sybil resistance and sustainable native-asset utility separately. Seek adaptability without guaranteed future-proofing. |
| D-016 | Task 008 preserves the AI-first autonomous bootstrapping research direction. | Agents may eventually discover/onboard under bounded authority, contribute verifiable work and earn/spend; genuine observable activity may enable organic human discovery without marketing as the primary adoption mechanism. Aspiration only; see ADR 0004. |
| D-017 | Do not manufacture wallet activity, artificial trading or misleading economic signals. | Label synthetic tests; public volume/address count is not proof of independent customers, native value, useful work or adoption. |

## Long-term aspirations (not decisions)

- Explore a foundational permissionless economic network for diverse autonomous participants.
- Investigate the independent permissionless L1/native-economy goal under D-014; use alternatives as controls and explicitly review direction if evidence challenges it.
- Support heterogeneous owners, hardware, models, jurisdictions, objectives, and connectivity conditions where feasible.
- Investigate offline, satellite, and future space-based coordination constraints.
- Consider whether useful contribution can contribute to services, incentives, or security.

## Open and deferred choices

D-014 confirms a research target, not a final protocol. Concrete chain architecture, consensus, native-asset design/necessity, economics, token issuance, execution model, governance, permanent name, launch and production timeline remain unselected/unvalidated. See `MASTER_PLAN.md`, `docs/FUTURE_NETWORK_ARCHITECTURE.md`, and `docs/ROADMAP.md`.

## Experiment-specific proposals

Task 002B originally recorded [ADR 0001](adr/0001-experiment-001-architecture.md) as **Proposed** at that time, with a local Anvil/Ethereum-compatible experiment, typed authorization, requester Acceptance plus on-chain arithmetic, and deterministic escrow/refund rules. This does not change D-006 or D-010 and is not an accepted production architecture. The original [specification](experiments/EXPERIMENT_001.md) authorized documentation only; Task 003A subsequently authorizes the component described below.

Task 003A separately authorizes the local Solidity escrow implementation and explicitly preserves requester veto. ADR 0001 is now accepted for that component only; [escrow coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) and [dependency pins](../DEPENDENCIES.md) record the boundary. No Python-agent, full network, token, consensus, or production decision follows.

Task 003B subsequently authorizes the independent Python-agent integration and temporary loopback Anvil deployment for Experiment 001. ADR 0001's scope is extended to this local fixture without changing its escrow semantics or requester-veto limitation. This does not authorize production, native assets, consensus implementation, or any final network architecture.

## Task 005 — Experiment 002 proposal, pending design review

[ADR 0002](adr/0002-experiment-002-fair-exchange.md) is **Proposed, not accepted**. The [research comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md) recommends testing a fixed directly verifiable service with upfront contingent payment consent in a separate Experiment 002. This would remove Experiment 001's second requester Acceptance requirement only in the new experiment. It is an explicit proposed semantic change, not a correction to the published control or an amended interpretation of its 18 invariants.

No new confirmed architectural/economic decision is recorded. The Task 005 instruction authorizes research/documentation and normal Git publication only. Design approval and implementation require a separate task. Conditional provider collectability assumes a timely canonical claim; public disclosure followed by censorship/expiry can still leave work unpaid. Ledger selection, confidential delivery, useful workloads, subjective/physical verification and broader fair exchange remain open. D-003, D-004, D-010 and all long-term decision boundaries remain unchanged.

## Task 006 — Vision clarification and Experiment 002 review

[ADR 0003](adr/0003-independent-l1-research-direction.md) records the founder-authorized research direction and three-pillar organization. It supersedes earlier canonical “one possibility” framing for the current goal; historical brainstorm and publication wording remain historical evidence, not retroactively edited decisions. Research may still find proposed mechanisms or the target unjustified and must preserve that evidence.

[ADR 0002](adr/0002-experiment-002-fair-exchange.md) is **amended and remains Proposed**, per the [design review](experiments/EXPERIMENT_002_DESIGN_REVIEW.md). Conditional valid-claim collection is distinct from provider progress, automatic refunds and strong fairness. No implementation approval follows. Scope/consent acceptance, schema/vector/timing freeze and reviewed dependencies/evidence mapping remain R1–R3. No additional token, consensus, mining or economic mechanism is decided.

## Task 007 — Final proposal and separate economic research

The [Experiment 002 final specification](experiments/EXPERIMENT_002_FINAL_SPEC.md), [signature/state fixtures](experiments/EXPERIMENT_002_SIGNING_VECTORS.md) and [dependency review](experiments/EXPERIMENT_002_DEPENDENCY_REVIEW.md) supply exact proposed behavior and R2 detail. ADR 0002 remains **Proposed / BLOCKED**, with B-DEP and B-FEE as explicit remaining decisions; service principal and gas-fee limits are separate. No new confirmed chain/economic/dependency choice or implementation approval is recorded.

The [AI-earned native-token/economic foundations](../research/economics/AI_EARNED_NATIVE_TOKENS_AND_UTILITY.md) initiates scoped prior-art and falsifiable E-01–E-05 research under D-014/D-015. Customer payments, useful-work issuance and consensus compensation are distinct. Native-only versus stable-value-settlement possibilities are hypotheses, not asset/adoption decisions. No ticker, supply, issuance rule, consensus selection, valuation, launch or return is proposed. Experiment 001 evidence and limitations remain unchanged.

## Task 008 — Blockers resolved and autonomous bootstrapping preserved

[Blocker resolution](experiments/EXPERIMENT_002_BLOCKER_RESOLUTION.md) selects constrained reuse of the tested baseline with source restrictions and residual-risk acceptance for disposable local-only use. [Bounded costs](experiments/EXPERIMENT_002_BOUNDED_COST_MODEL.md) specify separate service principal and signer gas/run budgets; the baseline already had fixed fee fields overlooked in Task 007. **B-DEP and B-FEE are RESOLVED for this scope; ADR 0002 is Accepted for bounded local design, READY for separate implementation authorization.** No Experiment 002 implementation/experimental success, public deployment, asset, consensus or economic outcome follows. Source/feature/budget changes reopen review.

[ADR 0004](adr/0004-autonomous-bootstrapping-research-direction.md) records D-016/D-017 based on explicit founder instructions. Five [future research scopes](../research/AUTONOMOUS_BOOTSTRAPPING_RESEARCH.md) remain unimplemented. Market funding, native issuance, useful/duplicate work, fixed-resource Sybils and human discovery must remain distinguishable. No autonomous discovery, monetary value or organic adoption is demonstrated.

## Task 009 — authorized partial implementation and reopened evidence gate

Task 009 authorizes the separate local Experiment 002 implementation under accepted ADR 0002. The [blocking review](experiments/EXPERIMENT_002_IMPLEMENTATION_REVIEW.md) publishes the validated isolated contract/tests and records **FAIL / implementation BLOCKED**, superseding Task 008 READY. **B-ANVIL-FEE-EVIDENCE** reopens dependency compatibility and fee-reconciliation readiness: the pinned node's receipt effectiveGasPrice contradicts its actual capped debit under the controlled boundary schedule.

ADR 0002 remains Accepted for bounded local design. No new dependency, fee cap, evidence policy or architectural/economic decision is accepted. B-FEE's finite cost model remains specified; complete enforcement acceptance is blocked. No complete agent workflow is released. Review and resolve the contradiction explicitly before resuming; do not silently substitute calculated fees or upgrade tooling. Experiment 001 and long-term D-014–D-017 boundaries remain unchanged.

## Task 010 — fee-reporting diagnosis; no new dependency adoption

The [fee investigation](experiments/EXPERIMENT_002_FEE_INVESTIGATION.md) attributes B-ANVIL-FEE-EVIDENCE to missing fee-cap clamping in pinned Anvil's derived RPC receipt/mined-transaction prices. Raw RPC, execution opcode and wallet accounting distinguish reporting from charging; no actual excess debit was observed. The approved fee equation and strict rejection remain correct. Add a requirement to distinguish derived RPC metadata and isolated fee-only wallet deltas from principal/concurrent flows; no contradictory receipt may be repaired or silently trusted.

**Conclusion STILL BLOCKED.** Upstream corrected-source references are a proposal, not permission to use a new toolchain. The candidate download was incomplete/unverified and never executed; no pin, compiler, library, fee cap, signed schema or escrow semantics changed. ADR 0002 remains Accepted for local design only. The incomplete agent implementation stays paused. Before resuming, explicitly review/record a verified corrected-node tuple after the original reproducer, full boundary/fee evidence and unchanged regressions pass. Characterization CI detects/rejects the old defect; it does not clear readiness.

## Task 011 — explicit corrected-Anvil profile

[ADR 0005](adr/0005-experiment-002-corrected-anvil-baseline.md) accepts the reversible, isolated Anvil v1.6.0-rc1 / b272ce3366987406406e9eb1b82596653a3ad628 **Cancun** profile for bounded infrastructure, subject to the publication commit's Ubuntu CI passing. [Validation](experiments/EXPERIMENT_002_ANVIL_VALIDATION.md) verifies source/archive/binary pins, original negative control and identical corrected positive fee cases, unchanged control regressions, signatures and strict rejection of forged evidence. Then B-ANVIL-FEE-EVIDENCE/node compatibility are resolved for this profile only.

Only the selected Experiment 002 node changes; original Experiment 001 defaults/code/evidence, Forge/Cast/compiler/libraries/Python, principal/fee/wallet/run limits, signed schemas and reconciliation rules remain. No crypto attestation/reproducible-build or production-security claim; dependency/host/rc1 risks remain. No agents were resumed in Task 011. A subsequent implementation task may use the validated profile but must still satisfy all outstanding experimental gates. Integrity/compatibility/scope failures reopen BLOCKED; no future Genesis architecture/economic choice follows.
