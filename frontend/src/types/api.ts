/**
 * TypeScript types matching DATA_SCHEMA.md
 * Generated for Fly Bot API v1
 */

// ========== Request Types ==========

export type AgeBucket = 'infant' | 'child' | 'adult';

export interface Traveler {
  age_bucket: AgeBucket;
}

export interface ReturnWindow {
  earliest: string; // ISO8601 datetime
  latest: string; // ISO8601 datetime
  return_flex_minutes: number;
}

export interface Constraints {
  nonstop_only?: boolean;
  max_connections?: number;
  cabin_preference?: string;
}

export interface RecommendationRequest {
  request_id: string;
  origin: string; // IATA code
  destination: string; // IATA code
  lookahead_minutes?: number;
  return_window: ReturnWindow;
  travelers: Traveler[];
  constraints?: Constraints;
}

// ========== Response Types ==========

export interface ScoreBreakdown {
  return_success_probability: number;
  outbound_margin_bonus: number;
  trip_score: number;
}

export interface OutboundFlight {
  flight_id: string;
  flight_number: string;
  departure_time: string; // ISO8601
  arrival_time: string; // ISO8601
  open_seats_now: number;
  seat_margin: number;
  snapshot_ts: string; // ISO8601
}

export interface ReturnOption {
  flight_id: string;
  flight_number: string;
  departure_time: string; // ISO8601
  arrival_time: string; // ISO8601
  open_seats_now?: number;
  probability: number;
  meets_buffered_deadline: boolean;
}

export interface TripRecommendation {
  trip_score: number;
  score_breakdown: ScoreBreakdown;
  outbound: OutboundFlight;
  return_options: ReturnOption[];
  explanations: string[];
  reason_codes: string[];
}

export interface TimingInfo {
  total_ms: number;
  empties_ms?: number;
  schedule_ms?: number;
  scoring_ms?: number;
}

export interface RecommendationResponse {
  request_id: string;
  model_version: string;
  generated_at: string; // ISO8601
  seats_required: number;
  required_return_buffer_minutes: number;
  recommendations: TripRecommendation[];
  fallback_used: boolean;
  timing_ms: TimingInfo;
}

// ========== Error Response ==========

export interface ErrorResponse {
  detail: string;
  request_id?: string;
}
