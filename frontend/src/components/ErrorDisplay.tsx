import { ApiError } from '../api/client';

interface ErrorDisplayProps {
  error: Error | null;
  onRetry?: () => void;
}

// AC-FE-4: Error handling for network and API failures
export function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  if (!error) return null;

  const isApiError = error instanceof ApiError;
  const isTimeout = error.message.includes('timed out');
  const isNetworkError = error.message.includes('Unable to connect');

  let title = 'Error';
  let message = error.message;
  let icon = '⚠️';

  if (isTimeout) {
    title = 'Request Timed Out';
    message = 'The request took too long to complete. Please try again.';
    icon = '⏱️';
  } else if (isNetworkError) {
    title = 'Connection Error';
    message = 'Unable to connect to the server. Please check your connection and try again.';
    icon = '🔌';
  } else if (isApiError) {
    title = 'API Error';
    icon = '❌';
  }

  return (
    <div className="bg-red-900/30 backdrop-blur-md border border-red-500/50 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-start gap-4">
        <div className="text-4xl">{icon}</div>
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-red-200 mb-2">{title}</h3>
          <p className="text-red-300 mb-4">{message}</p>
          
          {isApiError && (error as ApiError).requestId && (
            <p className="text-sm text-red-400 mb-4">
              Request ID: <span className="font-mono text-red-300">{(error as ApiError).requestId}</span>
            </p>
          )}

          {onRetry && (
            <button
              onClick={onRetry}
              className="bg-red-600 hover:bg-red-500 text-white font-semibold py-2 px-6 rounded-lg transition-all shadow-lg hover:shadow-xl"
            >
              🔄 Retry
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
