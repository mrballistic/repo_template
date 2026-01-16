import { useState } from 'react';
import type { TripRecommendation } from '../types/api';

interface ResultCardProps {
  recommendation: TripRecommendation;
  rank: number;
}

// AC-FE-2: Results display recommendations with key details
// AC-FE-3: Detail view shows explainability fields
export function ResultCard({ recommendation, rank }: ResultCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const { outbound, score_breakdown, return_options, explanations, reason_codes } = recommendation;
  
  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const probabilityPercent = Math.round(score_breakdown.return_success_probability * 100);

  return (
    <div className="bg-gray-800/50 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-700/50 p-5 hover:shadow-blue-900/20 hover:border-blue-500/50 transition-all hover:scale-[1.01]">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="bg-gradient-to-r from-blue-600 to-blue-500 text-white text-sm font-bold px-3 py-1 rounded-full shadow-lg">
            #{rank}
          </span>
          <span className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-blue-300 bg-clip-text text-transparent">
            {Math.round(recommendation.trip_score * 100)}%
          </span>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-400">Return Probability</div>
          <div className="text-2xl font-bold text-green-400">{probabilityPercent}%</div>
        </div>
      </div>

      {/* Outbound Flight */}
      <div className="border-l-4 border-blue-500 bg-blue-900/20 rounded-r-lg pl-4 pr-3 py-2 mb-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wide">Outbound</div>
            <div className="font-bold text-white text-lg">{outbound.flight_number}</div>
            <div className="text-sm text-gray-300">
              {formatDate(outbound.departure_time)} • {formatTime(outbound.departure_time)} - {formatTime(outbound.arrival_time)}
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400 uppercase">Open Seats</div>
            <div className="text-2xl font-bold text-white">{outbound.open_seats_now}</div>
            <div className={`text-sm font-semibold ${
              outbound.seat_margin >= 0 ? 'text-green-400' : 'text-orange-400'
            }`}>
              {outbound.seat_margin >= 0 ? '+' : ''}{outbound.seat_margin} margin
            </div>
          </div>
        </div>
      </div>

      {/* Return Options Count */}
      <div className="text-sm text-gray-300 mb-3 flex items-center gap-2">
        <span className="text-blue-400">✓</span>
        {return_options.length} return option{return_options.length !== 1 ? 's' : ''} available
      </div>

      {/* Explanations */}
      {explanations.length > 0 && (
        <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-3 mb-3">
          {explanations.map((exp, i) => (
            <div key={i} className="text-sm text-gray-300 flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>{exp}</span>
            </div>
          ))}
        </div>
      )}

      {/* Expand Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-blue-400 hover:text-blue-300 font-medium text-sm py-2 transition-colors border-t border-gray-700 mt-2"
      >
        {isExpanded ? '▲ Hide Details' : '▼ Show Details'}
      </button>

      {/* Expanded Details - AC-FE-3 */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-700 space-y-4">
          {/* Score Breakdown */}
          <div>
            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <span className="text-blue-400">📊</span>
              Score Breakdown
            </h4>
            <dl className="grid grid-cols-2 gap-3 text-sm bg-gray-900/50 rounded-lg p-3 border border-gray-700">
              <dt className="text-gray-400">Return Success Probability:</dt>
              <dd className="font-mono text-right text-green-400">{score_breakdown.return_success_probability.toFixed(4)}</dd>
              
              <dt className="text-gray-400">Outbound Margin Bonus:</dt>
              <dd className="font-mono text-right text-blue-400">{score_breakdown.outbound_margin_bonus.toFixed(4)}</dd>
              
              <dt className="text-gray-300 font-semibold">Trip Score:</dt>
              <dd className="font-mono font-bold text-right text-white">{score_breakdown.trip_score.toFixed(4)}</dd>
            </dl>
          </div>

          {/* Reason Codes */}
          <div>
            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <span className="text-blue-400">🏷️</span>
              Reason Codes
            </h4>
            <div className="flex flex-wrap gap-2">
              {reason_codes.map((code, i) => (
                <span
                  key={i}
                  className="bg-gray-700/50 text-blue-300 text-xs font-mono px-3 py-1.5 rounded-lg border border-gray-600"
                >
                  {code}
                </span>
              ))}
            </div>
          </div>

          {/* Return Flight Options */}
          <div>
            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <span className="text-blue-400">✈️</span>
              Return Flight Options
            </h4>
            <div className="space-y-2">
              {return_options.map((ret, i) => (
                <div key={i} className="bg-gray-900/50 border border-gray-700 rounded-lg p-3 text-sm hover:border-blue-500/50 transition-colors">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-white">{ret.flight_number}</div>
                      <div className="text-gray-400">
                        {formatDate(ret.departure_time)} • {formatTime(ret.departure_time)} - {formatTime(ret.arrival_time)}
                      </div>
                      {ret.open_seats_now !== undefined && (
                        <div className="text-gray-500 text-xs mt-1">{ret.open_seats_now} open seats</div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-green-400 text-lg">
                        {Math.round(ret.probability * 100)}%
                      </div>
                      {ret.meets_buffered_deadline ? (
                        <div className="text-xs text-green-400 flex items-center gap-1">
                          <span>✓</span> On time
                        </div>
                      ) : (
                        <div className="text-xs text-orange-400 flex items-center gap-1">
                          <span>⚠</span> Tight
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
