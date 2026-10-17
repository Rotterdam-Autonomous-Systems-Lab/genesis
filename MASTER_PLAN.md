# Genesis Master Plan

This document is the canonical project specification. Changes to the mission or scope require explicit review and a recorded decision. Genesis is a research project; statements below distinguish known techniques from questions and hypotheses.

## Mission and guiding principles

Research whether and how autonomous entities can hold cryptographic authority, coordinate, exchange resources, and transact over open networks without a centralized operator granting routine permission.

Guiding principles:

1. Research before implementation; evidence before claims.
2. Minimize authority and bound the damage any key or component can cause.
3. Prefer verifiable, interoperable mechanisms and explicit trust assumptions.
4. Treat privacy, accessibility, resilience, and abuse resistance as first-class requirements.
5. Publish uncertainty, negative results, and relevant prior art.
6. Do not presume a token, chain, consensus design, or governance structure.

## Research tracks

### 1. Autonomous Economic Authority

Study cryptographic identities and delegated authority, key rotation and recovery, capability-limited permissions, bounded autonomous spending, escrow and settlement interfaces, and verifiable service agreements. Questions include how an entity proves a particular authority without revealing unnecessary identity data, and how users revoke or constrain actions across disconnected systems.

### 2. Verifiable Coordination

Study permissionless discovery, negotiation and service descriptions, independently verifiable contributions, coordination under partial trust, and offline or delayed communication. Investigate what evidence can establish that a service was provided and how disputes can be handled without assuming one universally trusted judge.

### 3. Autonomous Network Security

Study Sybil resistance and collusion, incentives for honest participation, denial-of-service and resource-exhaustion risks, compromise containment, and future-proof protocol evolution. Compare trust assumptions and failure modes before proposing mechanisms.

## Scope

The current scope is literature review, threat analysis, formalization of requirements, small reproducible simulations, and evaluation of protocol hypotheses. Any software experiment must be explicitly scoped, non-production, and accompanied by stated assumptions and limitations.

## Explicit non-goals

- Implementing or claiming a novel consensus protocol at this stage.
- Building a production blockchain, node network, wallet, or autonomous agent.
- Launching a token, conducting a token sale, or specifying token economics.
- Handling real funds, production credentials, or live user assets.
- Claiming novelty without documented prior-art research.
- Promising that decentralization removes all governance, trust, or legal questions.

## Research milestones

1. **Problem framing:** define actors, capabilities, operating conditions, and measurable goals for each track.
2. **Prior-art map:** review relevant identity, capability security, distributed systems, cryptography, coordination, and Sybil-resistance work.
3. **Threat model:** document adversaries, assets, trust assumptions, and failure cases; review it with contributors.
4. **Requirements and hypotheses:** derive testable requirements and record competing hypotheses without selecting a winner prematurely.
5. **Evaluation design:** define metrics, baselines, reproducible methods, and criteria that could falsify each hypothesis.
6. **Research prototypes:** only after review, build isolated simulations or toy implementations that cannot be mistaken for production systems.
7. **Decision review:** publish findings, limitations, and unresolved risks; record major architectural decisions in ADRs.

Milestones are research gates, not delivery promises. A negative result or a decision not to implement is a valid outcome.

## Security requirements

- Never commit secrets, private keys, seed phrases, wallet material, or real credentials.
- Use synthetic identities and test data in experiments; never use real funds or production deployments.
- Minimize privileges and isolate experiments from external services.
- State adversary and trust assumptions in every security-relevant proposal.
- Include abuse cases such as Sybil attacks, collusion, replay, key compromise, censorship, denial of service, and network partitions where relevant.
- Security-critical future code must include meaningful tests and independent review before use.
- Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## Open questions

- What should count as an autonomous entity and a verifiable claim of authority?
- How can delegated authority be bounded, monitored, revoked, and recovered across systems?
- Which service and contribution claims can be verified independently, and at what cost?
- What guarantees are possible with intermittent connectivity and delayed messages?
- Which Sybil-resistance assumptions are acceptable for different use cases?
- How can collusion be measured or mitigated without a central arbiter?
- Which properties must remain stable across protocol upgrades, and who can authorize changes?
- Under what conditions, if any, would a token or consensus protocol be necessary?

## Development rules

- Read this document before making changes and preserve the mission unless an approved decision changes it.
- Keep work small, reviewable, and tied to a documented question or milestone.
- Separate established techniques, project assumptions, and speculative hypotheses.
- Cite sources for factual and prior-art claims; do not claim originality without evidence.
- Record major architectural decisions in `docs/adr/`.
- Never commit credentials or use real funds, production deployments, or external compute and services without authorization.
- Keep experiments reproducible and document methods, parameters, limitations, and negative results.
- See [AGENTS.md](AGENTS.md) for instructions to automated coding agents.

## Evidence labels

- **Established technique:** a method supported by prior work or broad practice; cite the relevant source and do not imply Genesis invented it.
- **Project assumption:** a condition currently adopted to make a question tractable; state how results depend on it.
- **Hypothesis:** an unvalidated proposition that has a test or argument capable of challenging it.
- **Finding:** a result supported by a documented method and evidence, with scope and limitations stated.
