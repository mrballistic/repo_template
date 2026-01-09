# Contributing

This repo follows a **spec-driven** and **test-first** workflow.

## The expected sequence
1. Create/update a spec in `specs/`
2. Add/modify tests in `tests/` mapped to AC-*
3. Implement in `src/project_name/`
4. Open a PR using the PR template

## Definition of Done
See `docs/definition_of_done.md`.

## Compounding engineering (PR learnings → reusable rules)
If a PR review comment repeats across multiple PRs:
1. Convert it into a concrete checklist item in `.github/PULL_REQUEST_TEMPLATE.md`
2. Add a corresponding rule in `AGENTS.md`
3. Add an automated check when possible (test, lint, CI)

See `docs/compounding_engineering.md` for a simple process.
