import { useState, FormEvent } from 'react';
import type { RecommendationRequest, AgeBucket } from '../types/api';

interface SearchFormProps {
  onSubmit: (request: RecommendationRequest) => void;
  isLoading: boolean;
}

// AC-FE-1: Search form captures all required inputs
export function SearchForm({ onSubmit, isLoading }: SearchFormProps) {
  const [origin, setOrigin] = useState('PDX');
  const [destination, setDestination] = useState('SFO');
  const [lookahead, setLookahead] = useState('90');
  const [returnEarliest, setReturnEarliest] = useState('2026-01-15T18:00');
  const [returnLatest, setReturnLatest] = useState('2026-01-15T23:00');
  const [returnFlex, setReturnFlex] = useState('60');
  const [travelerCount, setTravelerCount] = useState('1');
  const [errors, setErrors] = useState<string[]>([]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    const validationErrors: string[] = [];

    // Validate required fields
    if (!origin || origin.length !== 3) {
      validationErrors.push('Origin must be a 3-letter IATA code');
    }
    if (!destination || destination.length !== 3) {
      validationErrors.push('Destination must be a 3-letter IATA code');
    }
    if (!returnEarliest) {
      validationErrors.push('Return window earliest time is required');
    }
    if (!returnLatest) {
      validationErrors.push('Return window latest time is required');
    }

    // Validate datetime order
    if (returnEarliest && returnLatest && returnEarliest >= returnLatest) {
      validationErrors.push('Return earliest must be before latest');
    }

    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    setErrors([]);

    // Build travelers array (simplified: all adults for v1)
    const count = parseInt(travelerCount, 10) || 1;
    const travelers = Array.from({ length: count }, () => ({
      age_bucket: 'adult' as AgeBucket,
    }));

    const request: RecommendationRequest = {
      request_id: `web-${Date.now()}`,
      origin: origin.toUpperCase(),
      destination: destination.toUpperCase(),
      lookahead_minutes: parseInt(lookahead, 10) || 90,
      return_window: {
        earliest: returnEarliest,
        latest: returnLatest,
        return_flex_minutes: parseInt(returnFlex, 10) || 60,
      },
      travelers,
    };

    onSubmit(request);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-800/50 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-700/50 p-6 space-y-4">
      <h2 className="text-2xl font-bold text-white mb-4">Search Standby Flights</h2>

      {errors.length > 0 && (
        <div className="bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg backdrop-blur-sm">
          <ul className="list-disc list-inside">
            {errors.map((error, i) => (
              <li key={i}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="origin" className="block text-sm font-medium text-blue-200 mb-1">
            Origin (IATA)
          </label>
          <input
            id="origin"
            type="text"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            maxLength={3}
            className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase placeholder-gray-400"
            placeholder="PDX"
          />
        </div>

        <div>
          <label htmlFor="destination" className="block text-sm font-medium text-blue-200 mb-1">
            Destination (IATA)
          </label>
          <input
            id="destination"
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            maxLength={3}
            className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 uppercase placeholder-gray-400"
            placeholder="SFO"
          />
        </div>
      </div>

      <div>
        <label htmlFor="travelerCount" className="block text-sm font-medium text-blue-200 mb-1">
          Number of Travelers
        </label>
        <input
          id="travelerCount"
          type="number"
          min="1"
          max="9"
          value={travelerCount}
          onChange={(e) => setTravelerCount(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div>
        <label htmlFor="lookahead" className="block text-sm font-medium text-blue-200 mb-1">
          Lookahead Minutes (outbound departure window)
        </label>
        <input
          id="lookahead"
          type="number"
          min="30"
          max="240"
          value={lookahead}
          onChange={(e) => setLookahead(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="returnEarliest" className="block text-sm font-medium text-blue-200 mb-1">
            Return Earliest
          </label>
          <input
            id="returnEarliest"
            type="datetime-local"
            value={returnEarliest}
            onChange={(e) => setReturnEarliest(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="returnLatest" className="block text-sm font-medium text-blue-200 mb-1">
            Return Latest
          </label>
          <input
            id="returnLatest"
            type="datetime-local"
            value={returnLatest}
            onChange={(e) => setReturnLatest(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      <div>
        <label htmlFor="returnFlex" className="block text-sm font-medium text-blue-200 mb-1">
          Return Flexibility Minutes
        </label>
        <input
          id="returnFlex"
          type="number"
          min="0"
          max="180"
          value={returnFlex}
          onChange={(e) => setReturnFlex(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 disabled:from-gray-600 disabled:to-gray-600 text-white font-bold py-3 px-4 rounded-xl transition-all shadow-lg hover:shadow-xl hover:scale-[1.02] disabled:scale-100 min-h-[44px]"
      >
        {isLoading ? '🔍 Searching...' : '✈️ Search Flights'}
      </button>
    </form>
  );
}
