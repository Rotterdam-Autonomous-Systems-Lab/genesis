# Instructions for Codex and other automated agents

1. Read `MASTER_PLAN.md` and `docs/PROJECT_CONTEXT.md` before making changes.
2. Consult `docs/DECISION_REGISTER.md` for established architectural and project decisions.
3. Preserve Genesis's long-term ambition to research foundational infrastructure and a possible independent permissionless network.
4. Never redefine Genesis as only an AI-agent payment application; the first two-agent experiment is an early research step.
5. Separate established facts and techniques from project assumptions, hypotheses, aspirations, and verified findings. Cite sources and do not claim novelty without prior-art evidence.
6. Record major architectural decisions in `docs/adr/` and update the decision register and affected documentation when approved decisions change.
7. Preserve research failures, negative results, uncertainty, and rejected or deferred ideas. Do not silently erase project history.
8. Use small, testable implementation tasks tied to a research question. Do not implement protocols, contracts, agents, consensus, or token systems unless a task explicitly authorizes it.
9. Never expose, read into output, stage, or commit secrets, private keys, wallet material, credentials, or `.env` files. Keep `.env.example` placeholder-only. Keep `internal/` ignored and uncommitted.
10. Never use real funds, production deployments, uncontrolled autonomous replication, or unauthorized infrastructure, compute, or external services.
11. Inspect repository state, Git identity, and staged filenames before committing. Never force-push, rewrite history, delete branches or tags, or change credentials or organization permissions without explicit approval.
12. Clearly identify assumptions, uncertainty, and evidence limits in reports and documentation.
13. Ask for approval before irreversible architectural or economic decisions.
