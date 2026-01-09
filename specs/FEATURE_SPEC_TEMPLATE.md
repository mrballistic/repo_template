# Feature Spec: <Feature Name>

- **Status:** Draft | In Review | Approved | Implemented
- **Owner(s):** <name / team>
- **Reviewer(s):** <name / team>
- **Last updated:** <YYYY-MM-DD>
- **Links:** Issue/Jira: <link> · Design doc: <link> · PR: <link>

---

## 1) Problem and context (why)
**Problem statement:**  
<What problem are we solving? Who is impacted? What decision/action changes as a result?>

**Context / constraints:**  
- <Regulatory/security constraints>
- <Latency/cost constraints>
- <Dependencies>

---

## 2) Goals and non-goals (what success looks like)
### Goals
- <Goal 1>
- <Goal 2>

### Non-goals
- <Explicitly out of scope>

### Success metrics (must be measurable)
**Product metric(s):**
- <e.g., reduce manual review time by X%>

**ML metric(s):**
- <e.g., precision@k, AUROC, calibration error>

**Operational metric(s):**
- <e.g., p95 latency < 200ms, error rate < 0.1%>

---

## 3) Users and workflow (who/when/how)
**Primary user(s):** <Ops agent / internal service / customer-facing system>  
**User journey / system flow:**  
1. <Step>
2. <Step>
3. <Step>

---

## 4) Inputs / outputs (contract)
### Inputs
- **Source:** <API / batch table / stream>
- **Schema (fields):**  
  - `field_a`: <type> — <description> (required/optional)
  - `field_b`: <type> — <description> (required/optional)
- **Validation rules:**  
  - <ranges, null policy, enums, max lengths>

### Outputs
- **Destination:** <API response / table / topic>
- **Schema (fields):**  
  - `prediction`: <type> — <description>
  - `confidence`: <type> — <description>
  - `reason_codes`: <type> — <description>
- **Error behavior:**  
  - <What happens on invalid inputs? timeouts? downstream unavailable?>

---

## 5) Acceptance criteria (testable statements)
Write these so a test can clearly pass/fail. Label each one.

- **AC-1:** Given <condition>, when <action>, then <expected outcome>.
- **AC-2:** …
- **AC-3:** …
- **AC-4 (failure mode):** Given <bad/edge input>, system returns <safe behavior> and logs <required fields>.
- **AC-5 (performance):** Under <load>, p95 latency is <target>.

> Tip: If you can’t write a failing test for it, it’s not an acceptance criterion yet.

---

## 6) ML approach and evaluation (how we know it works)
### Baseline
- <What is the current approach? what baseline will we beat?>

### Training / modeling (if applicable)
- <Model family or approach>
- <Feature transforms / embedding approach>
- <Versioning strategy for artifacts>

### Offline evaluation plan
- **Datasets:** <train/val/test split strategy; time windows>
- **Leakage checks:** <what you will validate>
- **Metrics:** <exact definitions>
- **Slice analysis:** <key segments>
- **Thresholding:** <how thresholds chosen; per-segment? global?>

### Online monitoring plan
- **Data quality monitors:** <null rate, schema drift, freshness>
- **Model performance monitors:** <proxy metrics, delayed labels, calibration drift>
- **Alerting:** <who gets paged, thresholds>

---

## 7) Rollout, fallback, and safety
- **Rollout plan:** Shadow | Canary | A/B | Full
- **Fallback behavior:** <what happens if model unavailable / low confidence?>
- **Kill switch / config flag:** <how to disable quickly>
- **Audit/logging requirements:** <what gets logged; retention; privacy>

---

## 8) Risks and mitigations
- **Risk:** <e.g., drift causes false positives>  
  **Mitigation:** <monitor, retrain trigger, guardrails>

- **Risk:** <e.g., data source instability>  
  **Mitigation:** <contract tests, schema versioning>

---

## 9) Open questions
- <Question 1>
- <Question 2>

---

## Appendix (optional)
- **Glossary:** <terms>
- **References:** <links>
