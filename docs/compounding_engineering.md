# Compounding Engineering (PR learnings → reusable acceleration)

The goal is to **make the next PR easier than the last** by turning recurring review feedback into reusable rules and automated checks.

## The loop
1. Build using spec + tests
2. Review the PR
3. Identify recurring review comments (friction)
4. Convert them into:
   - a PR checklist item
   - an agent rule (AGENTS.md)
   - an automated gate (test/lint/CI)
5. Repeat

## What to capture from PR review
- Missing tests for edge cases
- Silent contract changes (schema, API shape)
- Incorrect metric definitions or evaluation inconsistencies
- Missing monitoring, drift checks, or rollback strategy
- Observability gaps (model version, config, request id)
- Non-deterministic transforms without seeds

## A simple process (10 minutes per week)
- Maintain a short “top 10 recurring comments” list
- Each week, pick 1–2 items and codify them:
  - Add a checklist item to `.github/PULL_REQUEST_TEMPLATE.md`
  - Add a one-line rule to `AGENTS.md`
  - Add/adjust a test or CI step

## Rule writing guidelines
- One rule = one behavior
- Concrete and enforceable (“Add a contract test for schema changes”)
- Avoid vague rules (“Write cleaner code”)

## Optional: track rule history
Create `docs/rules_changelog.md` and add short entries when you change rules.
