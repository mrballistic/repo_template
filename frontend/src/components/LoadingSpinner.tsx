// AC-FE-2: Loading spinner while API call in flight
export function LoadingSpinner() {
  return (
    <div className="bg-gray-800/50 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-700/50 p-16 text-center">
      <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-gray-600 border-t-blue-500 mb-6"></div>
      <p className="text-gray-300 font-medium text-lg">Searching for flights...</p>
      <p className="text-gray-500 text-sm mt-2">Analyzing routes and probabilities</p>
    </div>
  );
}
