import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchRecommendations, ApiError } from './client';
import type { RecommendationRequest } from '../types/api';

// AC-FE-5: TypeScript types match API contracts (compile-time check)
// AC-FE-4: Error handling for network and API failures

describe('API Client', () => {
  const mockRequest: RecommendationRequest = {
    request_id: 'test-123',
    origin: 'PDX',
    destination: 'SFO',
    lookahead_minutes: 90,
    return_window: {
      earliest: '2026-01-15T18:00:00',
      latest: '2026-01-15T23:00:00',
      return_flex_minutes: 60,
    },
    travelers: [{ age_bucket: 'adult' }],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it('should make POST request with correct headers and body', async () => {
    const mockResponse = {
      request_id: 'test-123',
      model_version: 'baseline-v1',
      generated_at: '2026-01-15T12:00:00Z',
      seats_required: 1,
      required_return_buffer_minutes: 30,
      recommendations: [],
      fallback_used: false,
      timing_ms: { total_ms: 100 },
    };

    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await fetchRecommendations(mockRequest);

    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/v1/flybot/recommend',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockRequest),
      })
    );
    expect(result).toEqual(mockResponse);
  });

  it('should throw ApiError with status for 4xx errors', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => ({ detail: 'Invalid origin code', request_id: 'test-123' }),
    });

    try {
      await fetchRecommendations(mockRequest);
      expect.fail('Should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).message).toContain('Invalid origin code');
    }
  });

  it('should throw ApiError with status for 5xx errors', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => ({ detail: 'Database connection failed' }),
    });

    try {
      await fetchRecommendations(mockRequest);
      expect.fail('Should have thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).message).toContain('Database connection failed');
    }
  });

  it('should throw ApiError for network errors', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Failed to fetch'));

    await expect(fetchRecommendations(mockRequest)).rejects.toThrow(ApiError);
    await expect(fetchRecommendations(mockRequest)).rejects.toThrow('Unable to connect');
  });

  it('should throw ApiError for timeout', async () => {
    // Mock a slow fetch that will be aborted
    const abortError = new DOMException('The user aborted a request', 'AbortError');
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockRejectedValueOnce(abortError);

    try {
      await fetchRecommendations(mockRequest);
      expect.fail('Should have thrown timeout error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).message).toContain('timed out');
    }
  });

  it('should include request_id in error', async () => {
    (global.fetch as unknown as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Network error'));

    try {
      await fetchRecommendations(mockRequest);
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).requestId).toBe('test-123');
    }
  });
});
