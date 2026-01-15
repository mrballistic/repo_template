# Fly Bot Data Schema

This doc defines:
1) Online API request/response schemas (operational contract)
2) Training dataset schema (return-flight probability model)
3) Inference logging schema (monitoring + delayed label join)

---

## 1) Online schemas

### FlybotRecommendRequest
| Field | Type | Required | Notes |
|---|---:|:---:|---|
| request_id | string | ✅ | tracing |
| origin | string | ✅ | IATA |
| destination | string | ✅ | IATA |
| lookahead_minutes | int | ❌ | default 60 |
| return_window.earliest | datetime | ✅ | ISO8601 |
| return_window.latest | datetime | ✅ | ISO8601 |
| return_window.return_flex_minutes | int | ✅ | 0 = hard |
| travelers[] | array | ✅ | age_bucket items |
| travelers[].age_bucket | enum | ✅ | infant/child/adult |
| constraints.nonstop_only | bool | ❌ | default false |
| constraints.max_connections | int | ❌ | default 1 |
| constraints.cabin_preference | string | ❌ | default any |

### FlybotRecommendResponse
| Field | Type | Required | Notes |
|---|---:|:---:|---|
| request_id | string | ✅ | echo |
| model_version | string | ✅ | baseline if fallback |
| generated_at | datetime | ✅ | |
| seats_required | int | ✅ | derived |
| required_return_buffer_minutes | int | ✅ | derived |
| recommendations[] | array | ✅ | sorted |
| recommendations[].trip_score | float | ✅ | [0,1] |
| recommendations[].score_breakdown | object | ✅ | explicit math |
| recommendations[].outbound | object | ✅ | empties + margin |
| recommendations[].return_options[] | array | ✅ | eligible returns + p |
| recommendations[].explanations[] | array[string] | ✅ | user-facing |
| recommendations[].reason_codes[] | array[string] | ✅ | stable codes |
| fallback_used | bool | ✅ | |
| timing_ms | object | ✅ | step timings |

---

## 2) Training dataset schema

### Table: return_clearance_training_examples
One row per (return-flight candidate, party) with label cleared standby.

| Column | Type | Required | Description |
|---|---:|:---:|---|
| example_id | string | ✅ | stable id |
| event_date | date | ✅ | return departure date (for time split) |
| origin | string | ✅ | return origin |
| destination | string | ✅ | return destination |
| region_bucket | string | ✅ | derived taxonomy |
| flight_number | string | ✅ | carrier+number |
| departure_ts | datetime | ✅ | scheduled |
| arrival_ts | datetime | ✅ | scheduled |
| dow | int | ✅ | 0–6 |
| dep_hour | int | ✅ | 0–23 |
| aircraft_type | string | ❌ | if available |
| capacity_total | int | ❌ | if available |
| open_seats_snapshot | int | ❌ | near decision time |
| booked_seats_snapshot | int | ❌ | if available |
| load_factor_snapshot | float | ❌ | if available |
| disruptions_flag | bool | ❌ | proxy |
| time_to_departure_min | int | ✅ | from decision_ts |
| seats_required | int | ✅ | derived |
| party_size | int | ✅ | count travelers |
| num_infants | int | ✅ | bucket count |
| num_children | int | ✅ | bucket count |
| num_adults | int | ✅ | bucket count |
| return_deadline_ts | datetime | ✅ | scenario constraint |
| return_flex_minutes | int | ✅ | |
| required_return_buffer_minutes | int | ✅ | computed |
| meets_buffered_deadline | bool | ✅ | arrival <= latest-buffer |
| label_cleared | int | ✅ | 1 boarded else 0 |
| label_source | string | ✅ | derivation note |
| snapshot_ts | datetime | ❌ | snapshot capture time |

**Decision timestamp note:** If query logs aren't available initially, use a proxy such as `decision_ts = departure_ts - X minutes` for historical backtesting and document in `label_source`.

---

## 3) Inference logging schema

### Table: flybot_predictions_log
| Column | Type | Required | Description |
|---|---:|:---:|---|
| request_id | string | ✅ | join key |
| logged_at | datetime | ✅ | |
| model_version | string | ✅ | |
| origin | string | ✅ | |
| destination | string | ✅ | |
| lookahead_minutes | int | ✅ | |
| seats_required | int | ✅ | |
| return_deadline_ts | datetime | ✅ | |
| return_flex_minutes | int | ✅ | |
| required_return_buffer_minutes | int | ✅ | |
| outbound_flight_id | string | ✅ | |
| outbound_open_seats_now | int | ❌ | |
| outbound_seat_margin | int | ❌ | |
| outbound_snapshot_ts | datetime | ❌ | |
| return_flight_ids | array[string] | ✅ | |
| return_probs | array[float] | ✅ | aligned |
| return_success_probability | float | ✅ | aggregated |
| outbound_margin_bonus | float | ✅ | |
| trip_score | float | ✅ | |
| fallback_used | bool | ✅ | |
| reason_codes | array[string] | ✅ | |
| timing_total_ms | int | ✅ | |

### Table: flybot_outcomes_joined
| Column | Type | Required | Description |
|---|---:|:---:|---|
| request_id | string | ✅ | |
| outcome_available_at | datetime | ✅ | |
| return_cleared_observed | bool | ✅ | |
| return_cleared_flight_id | string | ❌ | |
| label_quality | string | ✅ | high/medium/low |
