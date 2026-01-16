import type { RecommendationRequest, RecommendationResponse, ErrorResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const TIMEOUT_MS = 10000;

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public requestId?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * POST /v1/flybot/recommend
 * AC-FE-5: TypeScript types match API contracts
 */
export async function fetchRecommendations(
  request: RecommendationRequest
): Promise<RecommendationResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}/v1/flybot/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let requestId: string | undefined;

      try {
        const errorData: ErrorResponse = await response.json();
        errorMessage = errorData.detail || errorMessage;
        requestId = errorData.request_id;
      } catch {
        // Use default error message if JSON parsing fails
      }

      throw new ApiError(errorMessage, response.status, requestId);
    }

    const data: RecommendationResponse = await response.json();
    return data;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error || (error as unknown as { name?: string }).name === 'AbortError') {
      const err = error as Error & { name?: string };
      if (err.name === 'AbortError') {
        throw new ApiError('Request timed out', undefined, request.request_id);
      }
      throw new ApiError(
        `Unable to connect to server: ${err.message}`,
        undefined,
        request.request_id
      );
    }

    throw new ApiError('An unknown error occurred', undefined, request.request_id);
  }
}
