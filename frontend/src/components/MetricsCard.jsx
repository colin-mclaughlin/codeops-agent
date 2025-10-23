import { useEffect, useState } from "react";
import { getMetrics } from "../api";

export default function MetricsCard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await getMetrics();
      setMetrics(response.data);
      setError(null);
    } catch (err) {
      setError("Failed to load metrics");
      console.error("Metrics fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    // Refresh metrics every 10 seconds for live updates
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
        <h2 className="text-lg font-semibold mb-2 text-white">Metrics</h2>
        <div className="text-gray-400 text-sm">Loading metrics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
        <h2 className="text-lg font-semibold mb-2 text-white">Metrics</h2>
        <div className="text-red-400 text-sm">{error}</div>
        <button
          onClick={fetchMetrics}
          className="mt-2 text-xs text-blue-400 hover:text-blue-300"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold text-white">Metrics</h2>
        <button
          onClick={fetchMetrics}
          className="text-xs text-gray-400 hover:text-white transition-colors"
        >
          Refresh
        </button>
      </div>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-300">Total Runs:</span>
          <span className="text-white font-medium">{metrics?.total_runs || 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-300">Success Rate:</span>
          <span className="text-white font-medium">
            {metrics?.success_rate || 0}%
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-300">Avg Latency:</span>
          <span className="text-white font-medium">
            {metrics?.avg_latency || 0} ms
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-300">Avg Tokens:</span>
          <span className="text-white font-medium">
            {metrics?.avg_tokens || 0}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-300">Avg Cost:</span>
          <span className="text-white font-medium">
            ${metrics?.avg_cost_usd || 0}
          </span>
        </div>
        {metrics?.total_tokens > 0 && (
          <div className="flex justify-between">
            <span className="text-gray-300">Total Tokens:</span>
            <span className="text-white font-medium">
              {metrics.total_tokens.toLocaleString()}
            </span>
          </div>
        )}
        {metrics?.total_cost_usd > 0 && (
          <div className="flex justify-between">
            <span className="text-gray-300">Total Cost:</span>
            <span className="text-white font-medium">
              ${metrics.total_cost_usd.toFixed(5)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
