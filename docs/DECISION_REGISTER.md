# Decision Register

This register records project decisions and the boundaries around unresolved matters. “Confirmed” means established by the project owner’s instructions and current charter; it does not mean technically proven. Material changes require explicit review and a corresponding ADR. For technical context and historical ideas, see `research/history/`.

## Confirmed decisions

| ID | Decision | Consequence / boundary |
| --- | --- | --- |
| D-001 | Rotterdam Autonomous Systems Lab (RASL) is the research organization. | Genesis research is attributed to RASL; this does not establish legal structure beyond the stated organization. |
| D-002 | Genesis is the temporary project codename. | A permanent protocol or network name has not been selected. |
| D-003 | Development is open-source and research-first. | Prior art, assumptions, methods, failures, and uncertainty should be documented before implementation claims. |
| D-004 | Security and verifiability are primary principles. | Do not rely on participant intelligence or good intentions where actions can be independently bounded and verified. |
| D-005 | The core research program has three tracks: Autonomous Economic Authority, Verifiable Coordination, and Autonomous Network Security. | Do not collapse the whole mission into one track or app. |
| D-006 | A small two-agent experiment is the first implementation milestone. | It is an early step toward a larger network; its exact design, platform, scope, and acceptance details still require a research task and review. |
| D-007 | No premature token issuance. | No ticker, tokenomics parameters, presale, launch date, or issuance schedule is approved. |
| D-008 | No premature consensus claims. | Genesis has not invented or validated a new consensus protocol; APoC remains a hypothesis. |
| D-009 | No uncontrolled autonomous replication or unauthorized infrastructure use. | Experiments must remain bounded and authorized; do not self-propagate or consume third-party resources without authorization. |
| D-010 | Ethereum is not a permanent commitment as final architecture. | Existing chains may be experimental platforms or comparison points; an independent network remains an open possibility. |
| D-011 | No final network brand, ticker, or consensus algorithm is selected. | Names and mechanisms remain open pending research and review. |
| D-012 | Historical brainstorms must remain distinguishable from decisions. | Preserve ideas as historical material without presenting them as approved design. |
| D-013 | Public repository materials must not contain credentials or secrets. | Local-only sensitive or unpolished notes belong under ignored `internal/`; public history documents must be suitable for release. |

## Long-term aspirations (not decisions)

- Explore a foundational permissionless economic network for diverse autonomous participants.
- Explore an independent permissionless L1 or another decentralized architecture if evidence justifies it.
- Support heterogeneous owners, hardware, models, jurisdictions, objectives, and connectivity conditions where feasible.
- Investigate offline, satellite, and future space-based coordination constraints.
- Consider whether useful contribution can contribute to services, incentives, or security.

## Open and deferred choices

No final decision exists on chain architecture, consensus, native asset, economics, token issuance, execution model, governance, permanent name, launch, or production timeline. See `MASTER_PLAN.md`, `docs/FUTURE_NETWORK_ARCHITECTURE.md`, and `docs/ROADMAP.md`.

## Experiment-specific proposals

Task 002B originally recorded [ADR 0001](adr/0001-experiment-001-architecture.md) as **Proposed** at that time, with a local Anvil/Ethereum-compatible experiment, typed authorization, requester Acceptance plus on-chain arithmetic, and deterministic escrow/refund rules. This does not change D-006 or D-010 and is not an accepted production architecture. The original [specification](experiments/EXPERIMENT_001.md) authorized documentation only; Task 003A subsequently authorizes the component described below.

Task 003A separately authorizes the local Solidity escrow implementation and explicitly preserves requester veto. ADR 0001 is now accepted for that component only; [escrow coverage](experiments/EXPERIMENT_001_ESCROW_COVERAGE.md) and [dependency pins](../DEPENDENCIES.md) record the boundary. No Python-agent, full network, token, consensus, or production decision follows.

Task 003B subsequently authorizes the independent Python-agent integration and temporary loopback Anvil deployment for Experiment 001. ADR 0001's scope is extended to this local fixture without changing its escrow semantics or requester-veto limitation. This does not authorize production, native assets, consensus implementation, or any final network architecture.

## Task 005 — Experiment 002 proposal, pending design review

[ADR 0002](adr/0002-experiment-002-fair-exchange.md) is **Proposed, not accepted**. The [research comparison](../research/experiments/EXPERIMENT_002_FAIR_EXCHANGE_COMPARISON.md) recommends testing a fixed directly verifiable service with upfront contingent payment consent in a separate Experiment 002. This would remove Experiment 001's second requester Acceptance requirement only in the new experiment. It is an explicit proposed semantic change, not a correction to the published control or an amended interpretation of its 18 invariants.

No new confirmed architectural/economic decision is recorded. The Task 005 instruction authorizes research/documentation and normal Git publication only. Design approval and implementation require a separate task. Conditional provider collectability assumes a timely canonical claim; public disclosure followed by censorship/expiry can still leave work unpaid. Ledger selection, confidential delivery, useful workloads, subjective/physical verification and broader fair exchange remain open. D-003, D-004, D-010 and all long-term decision boundaries remain unchanged.
