# ML Product Repo Template (Spec-Driven + TDD + Compounding Engineering)

This template is designed to help teams accelerate the product development lifecycle using **AI-enabled workflows** while keeping changes **reviewable, testable, and safe**.

## How this repo is meant to be used

1. **Write the spec first**  
   Create a new file in `specs/` using `specs/FEATURE_SPEC_TEMPLATE.md`.

2. **Turn acceptance criteria into tests**  
   Add tests in `tests/` that map directly to your acceptance criteria (AC-1, AC-2, ...).

3. **Implement a thin slice**  
   Implement the minimum code needed to pass tests (start in `src/project_name/`).

4. **Review → learn → codify**  
   Use PR reviews to identify recurring feedback. Convert that feedback into:
   - a PR checklist item (`.github/PULL_REQUEST_TEMPLATE.md`)
   - an agent rule (`AGENTS.md`)
   - an automated gate (lint/test/CI)

## Key files

- `specs/FEATURE_SPEC_TEMPLATE.md` — the spec template
- `AGENTS.md` — instructions for AI assistants (and humans)
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist aligned to spec + eval + rollout
- `docs/compounding_engineering.md` — how to turn PR learnings into reusable rules
- `docs/definition_of_done.md` — what “done” means for this repo

## Quickstart (local)

> Adjust tooling to match your org standards. This is intentionally minimal.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"

pytest -q
ruff check .
```

## Notes on AI usage

- Do **not** paste secrets, credentials, or sensitive customer/operational data into non-approved AI tools.
- Treat AI output as **untrusted** until validated by tests and code review.
- Prefer small diffs and explicit acceptance criteria.

See: `docs/ai_usage_and_data_handling.md` (customize to your internal policy).
