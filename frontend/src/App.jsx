import { useEffect, useState } from "react";
import HealthCard from "./components/HealthCard";
import MetricsCard from "./components/MetricsCard";
import RunsTable from "./components/RunsTable";
import ContextPanel from "./components/ContextPanel";
import LatencyLineChart from "./components/charts/LatencyLineChart";
import SuccessRatioChart from "./components/charts/SuccessRatioChart";
import ConfidenceTrendChart from "./components/charts/ConfidenceTrendChart";
import { getRuns } from "./api";

export default function App() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchRuns = async () => {
    try {
      const response = await getRuns(50);
      setRuns(response.data);
    } catch (err) {
      console.error("Error fetching runs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
    // Refresh runs every 15 seconds for charts
    const interval = setInterval(fetchRuns, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">CodeOps Agent Dashboard</h1>
              <p className="text-sm text-gray-400 mt-1">
                Autonomous DevOps Assistant - Monitor, Analyze, and Fix CI/CD Issues
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm text-gray-400">
                <span className="text-green-400">●</span> Backend Connected
              </div>
              <div className="text-xs text-gray-500">
                v0.1.0
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        <div className="space-y-6">
          {/* Top Row - Health and Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <HealthCard />
            <MetricsCard />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <LatencyLineChart runs={runs} />
            <SuccessRatioChart runs={runs} />
            <ConfidenceTrendChart runs={runs} />
          </div>

          {/* Runs Table */}
          <RunsTable />

          {/* Context Panel */}
          <ContextPanel />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <div>
              CodeOps Agent - Phase 4b Frontend Implementation
            </div>
            <div className="flex items-center gap-4">
              <span>React + TailwindCSS + FastAPI</span>
              <span>•</span>
              <span>FAISS Retrieval System</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
