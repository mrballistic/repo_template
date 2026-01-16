## Spec
- [x] Link to spec: `specs/PRD_SPEC.md` (baseline evaluation requirements)
- [x] Link to task list: `specs/TASK_LIST.md` (Phase 3, Tasks 23-26)

## What changed
- Implemented baseline heuristic model (`src/flybot/baseline.py`) with simple probability calculation based on party size, capacity, time-to-departure
- Created evaluation metrics module (`eval/metrics.py`) with Brier score, accuracy, precision/recall/F1, calibration curves
- Built synthetic dataset generator (`eval/dataset.py`) that creates easy/medium/hard scenarios with known ground truth
- Added evaluation script (`eval/evaluate_baseline.py`) that reports overall and per-scenario performance
- Wired baseline fallback into service layer with `fallback_used` flag
- Added 26 tests (14 baseline unit tests, 12 metrics unit tests) following TDD

## Acceptance criteria coverage
List the AC-* items satisfied by this PR and how they are verified.

- [x] **AC-BASELINE-1:** Baseline model produces probabilities in [0, 1] - Verified by `test_baseline_probability_range`
- [x] **AC-BASELINE-2:** Baseline decreases probability as seats_required increases - Verified by `test_baseline_party_size_penalty`
- [x] **AC-BASELINE-3:** Baseline model is deterministic - Verified by `test_baseline_determinism`
- [x] **AC-BASELINE-4:** Baseline wired into service with fallback_used flag - Verified by integration tests in `test_api.py`
- [x] **AC-EVAL-1:** Evaluation metrics include Brier score - Verified by `test_brier_score_*` tests
- [x] **AC-EVAL-2:** Evaluation includes calibration curve - Verified by `test_calibration_curve`
- [x] **AC-EVAL-3:** Evaluation script runs and produces report - Verified by manual run showing Brier 0.2023, 72% accuracy

## Verification
- [x] Tests added/updated (mapped to AC-*)
  - `tests/unit/test_baseline.py` (14 tests) - AC-BASELINE-1,2,3
  - `tests/unit/test_metrics.py` (12 tests) - AC-EVAL-1,2
  - Baseline already wired in service from Phase 2 - AC-BASELINE-4
- [x] `pytest` passes (110 total tests, all passing)
- [x] Lint passes (`ruff check`)

## ML evaluation (if applicable)
- [x] Offline evaluation results: `eval/results/baseline_eval_results.json`
  - **Overall:** Brier score 0.2023, Accuracy 72%, Precision 72.6%, Recall 70.67%, F1 71.62%
  - **By scenario:** Easy 80% acc, Medium 56% acc, Hard 80% acc (conservative, predicts all negative)
  - **Calibration:** Reasonable alignment across 5 bins (predicted vs actual within ~10-15% except one bin)
- [x] Metric definitions match the spec
  - Brier score = MSE of probabilities (per PRD_SPEC.md success metrics)
  - Calibration curve bins predicted vs actual (per PRD_SPEC.md)
- [x] Thresholding strategy documented
  - No explicit threshold; baseline returns raw probabilities aggregated via 1-∏(1-p_i)
  - ML model must beat baseline by ≥10% relative improvement per PRD_SPEC.md

## Monitoring / observability
- [x] Data quality monitors: Not applicable (synthetic dataset for baseline eval only)
- [x] Model version logged: `model_version="baseline-v1"` in response schema
- [x] Baseline provides safe fallback target for ML model performance comparison

## Rollout / fallback
- [x] Rollout plan: Baseline is the *fallback* itself, always available when ML unavailable
- [x] Fallback behavior: Service returns baseline predictions with `fallback_used=true` flag when `use_ml=False` or ML model unavailable
- [x] Baseline establishes minimum acceptable performance (72% accuracy, Brier 0.2023) that ML must exceed

## Risks
What could go wrong? How will we know quickly?

- **Risk:** Baseline too conservative (predicts low probabilities) → users don't trust recommendations
  - **Mitigation:** Evaluation shows 72% accuracy is reasonable starting point; ML model will improve this
  - **Detection:** Monitor fallback_count metric + user engagement with low-score recommendations
- **Risk:** Synthetic dataset doesn't match real distribution → baseline performance misleading
  - **Mitigation:** Synthetic scenarios based on domain knowledge from PRD; will validate with real data when available
  - **Detection:** Compare baseline performance on real data (when we get labeled examples) vs synthetic eval
- **Risk:** Calibration issues (predicted probabilities don't match observed frequencies)
  - **Mitigation:** Calibration curve shows reasonable alignment; ML model will include explicit calibration step
  - **Detection:** Monitor calibration metrics on production data

## AI usage (optional but recommended)
- [x] AI assistance used: **yes**
- [x] Parts assisted: spec review, test-first implementation (Red→Green→Refactor), evaluation script structure
- [x] Assumptions validated:
  - Baseline formula (base 0.5, party penalty -0.05/seat, capacity bonus, time bonus) → verified by tests
  - Synthetic dataset scenario definitions (easy/medium/hard) → verified that eligible returns align with buffer logic
  - Brier score implementation → validated against known values in tests
  - Calibration curve binning → tested with perfect predictions and known distributions

## Notes
- This completes **Phase 3** of TASK_LIST.md
- Baseline evaluation framework provides foundation for ML model comparison (Phase 5)
- All 110 tests passing (26 new baseline+metrics tests)
- Evaluation artifacts saved to `eval/results/` for reproducibility
