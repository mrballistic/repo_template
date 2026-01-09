# AGENTS.md — How to work in this repo (for humans and AI assistants)

This file defines **operating rules** for AI assistants and contributors in this repository.

## Prime directive
**Do not implement or change behavior unless it is traceable to the spec and acceptance criteria.**

## Required workflow
1. Start from a spec in `specs/` (create or update one).
2. Ensure acceptance criteria (AC-*) exist and are **testable**.
3. Write/modify tests in `tests/` first (or alongside) to enforce the ACs.
4. Implement the minimum code needed to pass tests.
5. Keep diffs small; prefer multiple small PRs over one large PR.
6. Update docs and monitoring/eval hooks as required by the spec.

## Hard constraints (non-negotiable)
- **No secrets** in code, logs, or prompts.
- **No sensitive data** in non-approved tools.
- **No silent interface changes**: if you change an input/output contract, update:
  - the spec
  - contract tests
  - versioning/migration notes (if applicable)
- **No “works on my machine”**: changes must be verifiable via tests and/or reproducible commands.

## When using an AI assistant
The assistant must:
- Ask clarifying questions when requirements, metrics, schemas, or rollout are ambiguous.
- Reference repository context (existing files, patterns) when suggesting changes.
- Prefer generating **tests and acceptance criteria** before implementation code.
- Provide a short plan before making multi-file edits.
- Explain assumptions and highlight risks.

### Output style requirements for AI-generated changes
- Include the **AC label** in test comments (e.g., `# AC-3`).
- Include clear error messages for validation failures.
- Prefer deterministic behavior by default (seeded randomness if used).

## Compounding engineering: how rules evolve
If you see recurring PR feedback, convert it into:
1. A new checklist item in `.github/PULL_REQUEST_TEMPLATE.md`
2. A new rule here (keep it one line if possible)
3. An automated gate (test, lint rule, CI check) when feasible

Track rule changes in `docs/compounding_engineering.md`.

## Common repo expectations (edit to your org)
- Log enough context to debug: request id, model version, config version (where applicable)
- Include a safe fallback behavior for low confidence / model unavailability
- Maintain a clear eval story (offline + monitoring)
