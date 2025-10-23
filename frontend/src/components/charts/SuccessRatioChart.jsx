import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export default function SuccessRatioChart({ runs = [] }) {
  if (!runs || runs.length === 0) {
    return (
      <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
        <h3 className="text-lg font-semibold mb-4 text-white">Success Ratio</h3>
        <div className="flex items-center justify-center h-64 text-gray-400">
          No runs available
        </div>
      </div>
    );
  }

  // Calculate success vs failure counts
  const successCount = runs.filter(run => run.verdict === 'success').length;
  const failureCount = runs.filter(run => run.verdict === 'failure').length;

  const data = [
    { name: 'Success', value: successCount, color: '#10B981' },
    { name: 'Failure', value: failureCount, color: '#EF4444' }
  ];

  const formatTooltip = (value, name) => {
    const percentage = runs.length > 0 ? ((value / runs.length) * 100).toFixed(1) : 0;
    return [`${value} runs (${percentage}%)`, name];
  };

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    if (percent === 0) return null;
    
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div className="p-4 bg-gray-800 rounded-2xl shadow-md border border-gray-700">
      <h3 className="text-lg font-semibold mb-4 text-white">Success Ratio</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#F9FAFB'
              }}
              formatter={formatTooltip}
            />
            <Legend 
              wrapperStyle={{ color: '#F9FAFB' }}
              formatter={(value) => (
                <span style={{ color: '#F9FAFB' }}>{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 text-sm text-gray-300">
        <div className="flex justify-between">
          <span>Total Runs: {runs.length}</span>
          <span>Success Rate: {runs.length > 0 ? ((successCount / runs.length) * 100).toFixed(1) : 0}%</span>
        </div>
      </div>
    </div>
  );
}
