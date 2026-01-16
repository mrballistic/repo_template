import { ResultCard } from './ResultCard';
import type { TripRecommendation } from '../types/api';

interface ResultsListProps {
  recommendations: TripRecommendation[];
}

// AC-FE-2: Results display recommendations with key details
export function ResultsList({ recommendations }: ResultsListProps) {
  if (recommendations.length === 0) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-700/50 p-12 text-center">
        <div className="text-6xl mb-4">🛑</div>
        <h3 className="text-xl font-semibold text-white mb-2">No Recommendations Found</h3>
        <p className="text-gray-400">
          Try adjusting your search criteria or return time window.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white flex items-center gap-2">
        <span className="text-green-400">✓</span>
        {recommendations.length} Recommendation{recommendations.length !== 1 ? 's' : ''} Found
      </h3>
      {recommendations.map((rec, index) => (
        <ResultCard key={index} recommendation={rec} rank={index + 1} />
      ))}
    </div>
  );
}
