# Spec: Fly Bot React Frontend

## Context
Fly Bot API is complete with demo data mode. Users need a web UI to search for standby recommendations without using curl/Postman.

## User Stories
**As a** standby traveler  
**I want** a simple web form to search for flight recommendations  
**So that** I can quickly find the best trips without technical knowledge

**As a** standby traveler  
**I want** to see probability breakdowns and explanations  
**So that** I understand why each trip is recommended

**As a** curious user  
**I want** to see the scoring logic (score breakdown, reason codes)  
**So that** I can validate/trust the recommendations

## Acceptance Criteria

### AC-FE-1: Search form captures all required inputs
- Route: origin (3-letter code), destination (3-letter code)
- Travelers: count and age buckets (adult, child, infant)
- Lookahead: minutes from now (default 90)
- Return window: earliest/latest ISO datetimes, flexibility minutes
- Form validates before submission (no empty origin/dest, valid datetimes)
- Submit button triggers POST to `/v1/flybot/recommend`

### AC-FE-2: Results display recommendations with key details
- Shows list of recommendations sorted by score (descending)
- Each result card shows:
  - Outbound flight (route, departure time, open seats)
  - Return probability percentage
  - Trip score
  - Expand button for details
- Empty state if no recommendations returned
- Loading spinner while API call in flight

### AC-FE-3: Detail view shows explainability fields
- Expanded result shows:
  - Score breakdown (return_success_probability, outbound_margin_bonus, trip_score)
  - Reason codes (machine-readable list)
  - User-facing explanations (strings)
  - Return flight options (eligible flights with individual probabilities)
- Details collapse when clicking expand button again

### AC-FE-4: Error handling for network and API failures
- Network error (fetch failed): shows "Unable to connect" message
- API error (4xx/5xx): shows error message from response body
- Timeout (>10s): shows "Request timed out" message
- All errors display with retry button
- Errors do not crash the app

### AC-FE-5: TypeScript types match API contracts
- RecommendationRequest type matches DATA_SCHEMA.md exactly
- RecommendationResponse type matches DATA_SCHEMA.md exactly
- No `any` types in API client or components
- Build fails if types mismatch

### AC-FE-6: Demo mode connection works out of box
- Default API URL is `http://127.0.0.1:8000` (local demo server)
- URL configurable via env var (VITE_API_BASE_URL)
- README includes "Start API, then npm run dev" instructions

### AC-FE-7: Responsive layout works on mobile and desktop
- Form fields stack vertically on mobile (<768px)
- Results cards adapt to screen width
- No horizontal scroll on mobile
- Touch-friendly tap targets (≥44px)

## Non-Goals (v1)
- Authentication/login
- User accounts or saved searches
- Historical trip tracking
- Multi-leg trips (covered by API but not UI yet)
- Admin panel for config/metrics

## Technical Requirements

### Stack
- **React 18** with functional components and hooks
- **TypeScript 5.0+** with strict mode
- **Vite** for build tooling (fast HMR)
- **TanStack Query (React Query)** for API state management
- **Tailwind CSS** for styling (utility-first)
- **Vitest + Testing Library** for component tests

### Type Generation
- Create `frontend/src/types/api.ts` matching:
  - `RecommendationRequest` from DATA_SCHEMA.md
  - `RecommendationResponse` from DATA_SCHEMA.md
  - `TripRecommendation`, `ScoreBreakdown`, `ReturnOption`, etc.

### Component Structure
```
frontend/src/
  components/
    SearchForm.tsx        # AC-FE-1
    ResultsList.tsx       # AC-FE-2
    ResultCard.tsx        # AC-FE-2, AC-FE-3
    ErrorBoundary.tsx     # AC-FE-4
  api/
    client.ts             # API call logic, TanStack Query hooks
  types/
    api.ts                # TypeScript types
  App.tsx                 # Main layout
  main.tsx                # Entry point
```

### Testing Requirements
- Unit tests for:
  - Form validation logic
  - Result card display logic
  - Error message formatting
  - API client request building
- Integration tests for:
  - Full search flow with mocked API responses
  - Error handling scenarios
- No E2E tests for v1 (can add later with Playwright)

### Performance Targets
- Initial load: <2s on 3G
- Time to interactive: <3s
- API request timeout: 10s
- No unnecessary re-renders (use React.memo where needed)

## Security/Privacy
- No PII sent to API (age_bucket instead of age)
- No credentials stored in localStorage
- API URL configurable (no hardcoded production URLs)

## Rollout Plan
1. Deploy frontend to static hosting (Vercel/Netlify/S3+CloudFront)
2. Point to demo API initially (read-only, no real data)
3. Add analytics (page views, search rate, error rate)
4. Iterate based on user feedback

## Open Questions
- Do we want to persist search history in localStorage? (No for v1)
- Should we add a "Share this recommendation" link? (No for v1)
- Do we need dark mode? (Nice to have, not blocking)

## References
- Backend spec: [PRD_SPEC.md](./PRD_SPEC.md)
- API contracts: [DATA_SCHEMA.md](./DATA_SCHEMA.md)
- TASK_LIST: Phase 8 (not yet defined, this spec initiates it)
