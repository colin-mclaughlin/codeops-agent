import { useState } from "react";
import { getContext, queryContext, getContextStats } from "../api";

export default function ContextPanel() {
  const [sha, setSha] = useState("");
  const [context, setContext] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  const handleFetch = async () => {
    if (!sha.trim()) {
      setError("Please enter a commit SHA");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await getContext(sha.trim());
      setContext(response.data.context_snippets || []);
    } catch (err) {
      setError("Failed to fetch context");
      console.error("Context fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!sha.trim()) {
      setError("Please enter a query");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await queryContext(sha.trim(), 5);
      setContext(response.data.results?.map(r => r.text) || []);
    } catch (err) {
      setError("Failed to query context");
      console.error("Context query error:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await getContextStats();
      setStats(response.data.store_stats);
    } catch (err) {
      console.error("Stats fetch error:", err);
    }
  };

  return (
    <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">Context Lookup</h2>
        <button
          onClick={loadStats}
          className="text-xs text-gray-400 hover:text-white transition-colors"
        >
          Show Stats
        </button>
      </div>

      {stats && (
        <div className="mb-4 p-3 bg-gray-700 rounded-lg">
          <h3 className="text-sm font-medium text-white mb-2">Store Statistics</h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-400">Total Texts:</span>
              <span className="text-white ml-1">{stats.total_texts}</span>
            </div>
            <div>
              <span className="text-gray-400">Index Size:</span>
              <span className="text-white ml-1">{stats.index_size}</span>
            </div>
            <div>
              <span className="text-gray-400">Model:</span>
              <span className="text-white ml-1 text-xs">{stats.model_name}</span>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        <div className="flex gap-2">
          <input
            value={sha}
            onChange={(e) => setSha(e.target.value)}
            placeholder="Commit SHA or query text..."
            className="p-2 bg-gray-700 rounded-md text-sm flex-1 text-white placeholder-gray-400 border border-gray-600 focus:border-blue-500 focus:outline-none"
            onKeyPress={(e) => e.key === 'Enter' && handleFetch()}
          />
          <button
            onClick={handleFetch}
            disabled={loading}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-md text-sm text-white transition-colors"
          >
            {loading ? "..." : "Fetch"}
          </button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleQuery}
            disabled={loading}
            className="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-md text-sm text-white transition-colors"
          >
            Query Similar
          </button>
          <button
            onClick={() => {
              setContext([]);
              setError(null);
            }}
            className="px-3 py-2 bg-gray-600 hover:bg-gray-700 rounded-md text-sm text-white transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-3 p-2 bg-red-900/20 border border-red-500/30 rounded-md">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {context.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-white mb-2">
            Context Snippets ({context.length})
          </h3>
          <div className="max-h-64 overflow-y-auto space-y-2">
            {context.map((snippet, i) => (
              <div
                key={i}
                className="p-3 bg-gray-700 rounded-md text-sm text-gray-300 border-l-2 border-blue-500"
              >
                <span className="text-xs text-gray-500 mr-2">#{i + 1}</span>
                {snippet}
              </div>
            ))}
          </div>
        </div>
      )}

      {context.length === 0 && !loading && !error && (
        <div className="mt-4 text-center py-4 text-gray-400">
          <p className="text-sm">No context snippets to display</p>
          <p className="text-xs mt-1">Enter a commit SHA or query to fetch context</p>
        </div>
      )}
    </div>
  );
}
