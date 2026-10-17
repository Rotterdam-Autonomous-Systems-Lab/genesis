# Threat model (initial)

This document is a starting inventory, not a complete assessment of a deployed system. Genesis has no production protocol or network. Every future experiment must define its own boundary and update this model before making security claims.

## Assets to consider

- Cryptographic keys and delegated authority.
- Funds, compute, bandwidth, storage, physical resources, and service access.
- Integrity and provenance of service agreements, messages, and contribution evidence.
- Availability of discovery and coordination functions.
- Privacy of participants, activity, and relationships.
- Upgrade and recovery mechanisms.

## Adversaries and failure conditions

Consider malicious participants, Sybil identities, colluding parties, compromised or lost keys, dishonest service providers or requesters, spam and denial-of-service actors, censoring intermediaries, malicious software updates, network partitions, delayed or reordered messages, and accidental operator error. Environmental constraints may include low power, intermittent connectivity, limited storage, and heterogeneous capabilities.

## Trust assumptions to state

For every proposal, state assumptions about cryptography, hardware, identity claims, time, connectivity, external data, dispute resolution, and participant resources. A mechanism does not remove trust merely by moving it to an oracle, registry, committee, or upgrade key.

## Initial security questions

- Can authority be constrained so a compromised key cannot exceed a stated budget or capability?
- Can service and contribution claims be forged, replayed, selectively withheld, or mutually fabricated by colluding parties?
- Can an attacker cheaply create identities or overwhelm discovery and verification?
- What happens during long partitions, equivocation, and delayed settlement?
- Can protocol evolution introduce hidden privilege or break historical verification?

## Research controls

Use synthetic keys and test data. Do not use real funds, production endpoints, or unauthorized external services. Document attack preconditions, impact, mitigations, residual risks, and evaluation limits. This document does not certify any design as secure.
