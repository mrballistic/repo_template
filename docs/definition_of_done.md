# Definition of Done

A change is “done” when:

## Spec alignment
- The change is traceable to an approved spec in `specs/`
- Acceptance criteria (AC-*) are present and up to date

## Verification
- Tests exist for new/changed behavior and map to AC-*
- `pytest` passes locally and in CI (or equivalent)

## Safety and operations (ML-focused)
- Input/output schema changes are documented and tested
- Evaluation story is documented (offline) and monitoring plan exists (online)
- Fallback behavior is defined for low confidence / model failure
- Logging/telemetry requirements are met (no sensitive data in logs)

## Reviewability
- Diff is reasonably small and explained
- PR description includes: what changed, why, how verified, risks, rollout plan
