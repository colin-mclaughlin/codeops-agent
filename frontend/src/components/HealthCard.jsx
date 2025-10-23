import { useEffect, useState } from "react";
import { getHealth } from "../api";

export default function HealthCard() {
  const [status, setStatus] = useState("loading");
  const [lastChecked, setLastChecked] = useState(null);

  const checkHealth = async () => {
    try {
      const response = await getHealth();
      setStatus("ok");
      setLastChecked(new Date().toLocaleTimeString());
    } catch (error) {
      setStatus("error");
      setLastChecked(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case "ok":
        return "text-green-400";
      case "error":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case "ok":
        return "🟢";
      case "error":
        return "🔴";
      default:
        return "🟡";
    }
  };

  return (
    <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold text-white">System Health</h2>
        <button
          onClick={checkHealth}
          className="text-xs text-gray-400 hover:text-white transition-colors"
        >
          Refresh
        </button>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-2xl">{getStatusIcon()}</span>
        <div>
          <p className={`text-sm font-medium ${getStatusColor()}`}>
            {status.toUpperCase()}
          </p>
          {lastChecked && (
            <p className="text-xs text-gray-500">
              Last checked: {lastChecked}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
