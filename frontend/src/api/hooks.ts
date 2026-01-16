import { useMutation } from '@tanstack/react-query';
import { fetchRecommendations } from './client';
import type { RecommendationRequest, RecommendationResponse } from '../types/api';

/**
 * TanStack Query hook for fetching recommendations
 * AC-FE-7: Wire up API client with TanStack Query
 */
export function useRecommendations() {
  return useMutation<RecommendationResponse, Error, RecommendationRequest>({
    mutationFn: fetchRecommendations,
    retry: 1, // Retry once on failure
  });
}
