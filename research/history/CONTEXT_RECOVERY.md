# Context Recovery Guide

Use this repository as the durable project record across contributors and future AI sessions.

## Reading order

1. `docs/PROJECT_CONTEXT.md` for a compact onboarding view.
2. `MASTER_PLAN.md` for the canonical mission, scope, and research gates.
3. `docs/DECISION_REGISTER.md` for confirmed decisions and unresolved choices.
4. Relevant topic documents, especially the research specification, hypotheses, threat model, roadmap, and future network architecture territory.
5. `research/history/ORIGINAL_BRAINSTORM.md` and `NAMING_AND_IDENTITY.md` for recovered historical material and naming context.
6. `docs/adr/` and Git history for decisions as they evolve.

## Distinguishing history from approved architecture

Historical brainstorm documents preserve ideas, ambitions, tensions, and rejected or deferred approaches. They are not specifications. A confirmed decision must appear in the decision register or a current approved ADR. A hypothesis is unvalidated even when it has a name such as APoC. An implementation is not evidence of security or project approval beyond its documented scope.

Use evidence labels: established technique, project assumption, research hypothesis, and finding. Cite the source and method for claims. If a historical detail cannot be supported by the repository or supplied project brief, mark it **not recovered** rather than filling the gap with plausible-sounding material.

## Reconstructing change over time

Review the initial charter and subsequent commits, ADRs, decision register, and dated research artifacts. Preserve superseded decisions and the reason for change; do not silently rewrite history. Check commit messages and dates as evidence of repository history only, not proof of technical claims. Where two records conflict, prefer the current master plan and decision register for present direction, and report the conflict so it can be resolved explicitly.

## Future-session instructions

Read `MASTER_PLAN.md` and `docs/PROJECT_CONTEXT.md`, consult `docs/DECISION_REGISTER.md`, and inspect current repository state before acting. Preserve the long-term independent-network ambition while keeping present hypotheses distinct from facts. Do not treat the original brainstorm as an architecture mandate or reduce Genesis to the first experiment.
