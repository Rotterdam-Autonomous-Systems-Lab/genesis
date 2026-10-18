# Instructions for Codex and other automated agents

1. Read `MASTER_PLAN.md` and `docs/PROJECT_CONTEXT.md` before making changes.
2. Consult `docs/DECISION_REGISTER.md` for established architectural and project decisions.
3. Preserve the founder-defined research goal: an independent permissionless Layer 1 blockchain economy with a native asset, AI mining or rewards through independently verifiable contributions, and genuine human and machine utility. Treat feasibility, consensus, issuance and sustainability as unresolved research, not achieved capabilities. Organize planning around Verifiable Autonomous Work, Independent Network Security, and Human and Machine Economy; retain the original technical tracks as cross-cutting methods.
4. Never redefine Genesis as only an AI-agent payment application; the first two-agent experiment is an early research step.
5. Separate established facts and techniques from project assumptions, hypotheses, aspirations, and verified findings. Cite sources and do not claim novelty without prior-art evidence.
6. Record major architectural decisions in `docs/adr/` and update the decision register and affected documentation when approved decisions change.
7. Preserve research failures, negative results, uncertainty, and rejected or deferred ideas. Do not silently erase project history.
8. Use small, testable implementation tasks tied to a research question. Do not implement protocols, contracts, agents, consensus, or token systems unless a task explicitly authorizes it.
9. Never expose, read into output, stage, or commit secrets, private keys, wallet material, credentials, or `.env` files. Keep `.env.example` placeholder-only. Keep `internal/` ignored and uncommitted.
10. Never use real funds, production deployments, uncontrolled autonomous replication, or unauthorized infrastructure, compute, or external services.
11. For routine repository tasks, inspect repository state, Git identity, diffs, and staged filenames; stage only files relevant to the requested task, create a commit, and push the ordinary commit to `origin/main` by default without asking again. Follow an explicit user request for local-only work, another branch or PR flow, or no publishing. Never force-push, rewrite history, delete branches or tags, or change credentials or organization permissions without explicit approval.
12. Clearly identify assumptions, uncertainty, and evidence limits in reports and documentation.
13. Ask for approval before irreversible architectural or economic decisions.
14. After significant tasks, make a concise update to `docs/SESSION_HANDOFF.md` covering current status, completed work, open questions, next task, blockers, relevant commits, and links to canonical documents.
