# Instructions for Codex and other automated agents

- Read `MASTER_PLAN.md` before making any changes.
- Never silently change Genesis's mission, scope, or guiding principles. Propose a reviewable change and record approved major decisions in an ADR.
- Never invent consensus, governance, or tokenomics decisions. The project has not invented or validated a new consensus protocol.
- Keep implementation tasks small, isolated, and tied to a research question.
- Write meaningful tests for future security-critical code; do not add protocol or smart-contract implementations without an explicit task.
- Record major architectural decisions in `docs/adr/`.
- Never read into logs, print, stage, or commit credentials, private keys, seed phrases, wallet files, `.env` files, or other secrets. Keep `.env.example` limited to placeholders.
- Never use real funds or production deployments.
- Never access external compute or services without authorization.
- Clearly distinguish assumptions, established techniques, hypotheses, and verified findings; cite sources for factual claims.
- Ask for approval before irreversible architectural decisions or actions.
- Inspect `git status` and staged filenames before committing. Do not force-push or overwrite existing work.
