# Research specification

## Purpose

Turn the Genesis mission into a set of tractable questions, explicit assumptions, and falsifiable hypotheses. Research outputs should help determine whether useful permissionless coordination is possible under clearly stated conditions.

## Tracks and questions

### Autonomous Economic Authority

- How are entities and their cryptographic identities represented while minimizing unnecessary disclosure?
- How can delegated authority be bounded by amount, time, purpose, counterparty, or resource?
- How can authorities be revoked, recovered, and audited when an entity is offline or a key is compromised?
- What evidence makes a service agreement and its fulfillment verifiable?

### Verifiable Coordination

- How can participants discover services without a central directory becoming a gatekeeper?
- Which contribution claims can be independently checked, by whom, and at what cost?
- How can parties coordinate when communication is offline, delayed, reordered, or partitioned?
- How should disagreements be represented when no single party is universally trusted?

### Autonomous Network Security

- What Sybil-resistance assumptions fit different environments and resource constraints?
- How can collusion, censorship, denial of service, replay, and resource exhaustion be detected or contained?
- How should protocols evolve while preserving interoperability and limiting the authority of upgrade mechanisms?
- Which security guarantees survive compromised keys or partially compromised participants?

## Method

For each research question, record prior art, actors, system boundaries, trust assumptions, threat cases, competing explanations, measurable outcomes, and a method that could falsify the leading hypothesis. Prefer formal analysis or reproducible simulations when appropriate. Report negative and inconclusive results.

## Evidence discipline

Label established techniques with citations. Label project assumptions and explain their effect. Mark untested claims as hypotheses. Reserve “finding” for a result backed by a documented method and evidence. Novelty claims require a documented search of relevant prior art.
