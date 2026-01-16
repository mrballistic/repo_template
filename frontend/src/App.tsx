import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SearchForm } from './components/SearchForm';
import { ResultsList } from './components/ResultsList';
import { ErrorDisplay } from './components/ErrorDisplay';
import { LoadingSpinner } from './components/LoadingSpinner';
import { useRecommendations } from './api/hooks';
import type { RecommendationRequest } from './types/api';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function FlybotApp() {
  const { mutate, data, error, isPending, reset } = useRecommendations();

  const handleSearch = (request: RecommendationRequest) => {
    reset(); // Clear previous results/errors
    mutate(request);
  };

  const handleRetry = () => {
    reset();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2 drop-shadow-lg">✈️ Fly Bot</h1>
          <p className="text-blue-200 text-lg">Standby Travel Recommender</p>
        </div>

        {/* Search Form */}
        <div className="mb-8">
          <SearchForm onSubmit={handleSearch} isLoading={isPending} />
        </div>

        {/* Results/Error/Loading */}
        <div>
          {error && <ErrorDisplay error={error} onRetry={handleRetry} />}
          {isPending && <LoadingSpinner />}
          {data && !isPending && !error && (
            <div className="space-y-4">
              <div className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/30 rounded-xl p-4 shadow-lg">
                <div className="flex items-center justify-between text-sm">
                  <div>
                    <span className="font-semibold text-blue-200">Model:</span>{' '}
                    <span className="text-blue-300 font-mono">{data.model_version}</span>
                    {data.fallback_used && (
                      <span className="ml-2 bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded text-xs border border-yellow-500/30">
                        FALLBACK
                      </span>
                    )}
                  </div>
                  <div className="text-blue-300">
                    Seats: {data.seats_required} • Buffer: {data.required_return_buffer_minutes}min
                  </div>
                </div>
              </div>
              <ResultsList recommendations={data.recommendations} />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-400">
          <p>Fly Bot v1 • Data from demo mode</p>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <FlybotApp />
    </QueryClientProvider>
  );
}
