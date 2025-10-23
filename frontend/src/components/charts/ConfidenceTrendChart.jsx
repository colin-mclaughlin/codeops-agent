import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function ConfidenceTrendChart({ runs = [] }) {
  // Filter runs that have critic_confidence data
  const runsWithConfidence = runs.filter(run => run.critic_confidence !== null && run.critic_confidence !== undefined);
  
  if (runsWithConfidence.length === 0) {
    return (
      <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
        <h3 className="text-lg font-semibold mb-4 text-white">Confidence Trend</h3>
        <div className="flex items-center justify-center h-64 text-gray-400">
          No confidence data available
        </div>
      </div>
    );
  }

  // Prepare data for the chart - show last 20 runs with confidence
  const chartData = runsWithConfidence.slice(0, 20).map((run, index) => ({
    index: runsWithConfidence.length - index,
    confidence: (run.critic_confidence * 100).toFixed(1), // Convert to percentage
    timestamp: new Date(run.timestamp).toLocaleTimeString()
  })).reverse();

  const formatTooltip = (value, name) => {
    if (name === 'confidence') {
      return [`${value}%`, 'Confidence'];
    }
    return [value, name];
  };

  return (
    <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
      <h3 className="text-lg font-semibold mb-4 text-white">Confidence Trend</h3>
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
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
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
              dataKey="confidence" 
              stroke="#F59E0B" 
              strokeWidth={2}
              dot={{ fill: '#F59E0B', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#F59E0B', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 text-sm text-gray-300">
        <div className="flex justify-between">
          <span>Runs with Confidence: {runsWithConfidence.length}</span>
          <span>Avg Confidence: {runsWithConfidence.length > 0 ? (runsWithConfidence.reduce((sum, run) => sum + run.critic_confidence, 0) / runsWithConfidence.length * 100).toFixed(1) : 0}%</span>
        </div>
      </div>
    </div>
  );
}
