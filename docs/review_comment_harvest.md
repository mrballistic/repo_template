# Review Comment Harvest (Starter)

Use this list to simulate PR review feedback and convert it into:
- PR checklist items
- agent rules in `AGENTS.md`
- automated gates (tests/lint/CI)

## Starter comments
- “This function has no unit tests for missing inputs.”
- “Schema changed but no migration note or versioning.”
- “Metric calculation differs from the spec.”
- “Logging doesn’t include request id / model version.”
- “No fallback behavior described for low confidence.”
- “Feature transformation isn’t deterministic.”
- “We need monitoring for drift / input null rate.”
- “Threshold logic is hardcoded; should be config-driven.”
- “This code path isn’t typed and broke in prod last time.”
- “No evidence of evaluation results or baseline comparison.”
