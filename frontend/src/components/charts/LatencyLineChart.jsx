import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function LatencyLineChart({ runs = [] }) {
  if (!runs || runs.length === 0) {
    return (
      <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
        <h3 className="text-lg font-semibold mb-4 text-white">Latency Trend</h3>
        <div className="flex items-center justify-center h-64 text-gray-400">
          No runs available
        </div>
      </div>
    );
  }

  // Prepare data for the chart - show last 20 runs
  const chartData = runs.slice(0, 20).map((run, index) => ({
    index: runs.length - index,
    latency: run.latency_ms,
    timestamp: new Date(run.timestamp).toLocaleTimeString()
  })).reverse();

  const formatTooltip = (value, name) => {
    if (name === 'latency') {
      return [`${value} ms`, 'Latency'];
    }
    return [value, name];
  };

  return (
    <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
      <h3 className="text-lg font-semibold mb-4 text-white">Latency Trend</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="index" 
              stroke="#9CA3AF"
              fontSize={12}
              tickFormatter={(value) => `#${value}`}
            />
            <YAxis 
              stroke="#9CA3AF"
              fontSize={12}
              tickFormatter={(value) => `${value}ms`}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#F9FAFB'
              }}
              formatter={formatTooltip}
              labelFormatter={(label, payload) => {
                if (payload && payload[0]) {
                  return `Run #${payload[0].payload.index} - ${payload[0].payload.timestamp}`;
                }
                return `Run #${label}`;
              }}
            />
            <Line 
              type="monotone" 
              dataKey="latency" 
              stroke="#3B82F6" 
              strokeWidth={2}
              dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#3B82F6', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
