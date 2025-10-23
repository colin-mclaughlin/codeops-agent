import { useEffect, useState } from "react";
import { getRuns } from "../api";

export default function RunsTable() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const response = await getRuns();
      setRuns(response.data);
      setError(null);
    } catch (err) {
      setError("Failed to load runs");
      console.error("Runs fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
    // Refresh runs every 30 seconds
    const interval = setInterval(fetchRuns, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatTimestamp = (timestamp) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case "success":
        return "text-green-400 bg-green-400/10";
      case "failure":
        return "text-red-400 bg-red-400/10";
      default:
        return "text-gray-400 bg-gray-400/10";
    }
  };

  if (loading) {
    return (
      <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
        <h2 className="text-lg font-semibold mb-2 text-white">Recent Runs</h2>
        <div className="text-gray-400 text-sm">Loading runs...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
        <h2 className="text-lg font-semibold mb-2 text-white">Recent Runs</h2>
        <div className="text-red-400 text-sm">{error}</div>
        <button
          onClick={fetchRuns}
          className="mt-2 text-xs text-blue-400 hover:text-blue-300"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">Recent Runs</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">
            {runs.length} run{runs.length !== 1 ? 's' : ''}
          </span>
          <button
            onClick={fetchRuns}
            className="text-xs text-gray-400 hover:text-white transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>
      
      {runs.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <p>No runs found</p>
          <p className="text-sm mt-1">Agent runs will appear here once they are executed</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-700">
                <th className="p-2 text-left">Run ID</th>
                <th className="p-2 text-left">Verdict</th>
                <th className="p-2 text-left">Latency</th>
                <th className="p-2 text-left">Tokens</th>
                <th className="p-2 text-left">Timestamp</th>
                <th className="p-2 text-left">Plan</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id} className="border-b border-gray-700 hover:bg-gray-700/30 transition-colors">
                  <td className="p-2 text-white font-mono text-xs">{run.id}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getVerdictColor(run.verdict)}`}>
                      {run.verdict}
                    </span>
                  </td>
                  <td className="p-2 text-gray-300">{run.latency_ms}ms</td>
                  <td className="p-2 text-gray-300">{run.tokens_used?.toLocaleString() || 'N/A'}</td>
                  <td className="p-2 text-gray-300 text-xs">
                    {formatTimestamp(run.timestamp)}
                  </td>
                  <td className="p-2">
                    <div className="max-w-xs truncate text-gray-300" title={run.plan}>
                      {run.plan}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
