import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface AllocationData {
  name: string;
  value: number;
  percentage: number;
}

interface AllocationPieProps {
  data: AllocationData[];
  height?: number;
}

const COLORS = [
  '#3b82f6', // blue
  '#10b981', // emerald
  '#f59e0b', // amber
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#f97316', // orange
  '#84cc16', // lime
];

export function AllocationPie({ data, height = 200 }: AllocationPieProps) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48">
        <p className="text-gray-500 text-sm">No allocation data</p>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: AllocationData }> }) => {
    if (active && payload && payload.length > 0) {
      const item = payload[0].payload;
      return (
        <div className="bg-gray-900 border border-gray-700 rounded px-3 py-2 shadow-xl">
          <p className="text-white font-medium text-sm">{item.name}</p>
          <p className="text-gray-400 text-xs mt-1">
            {formatCurrency(item.value)} ({item.percentage.toFixed(1)}%)
          </p>
        </div>
      );
    }
    return null;
  };

  // Sort data by percentage descending for the legend
  const sortedData = [...data].sort((a, b) => b.percentage - a.percentage);

  return (
    <div className="flex items-center gap-6">
      {/* Pie Chart */}
      <div className="flex-shrink-0" style={{ width: height, height }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius="90%"
              innerRadius="60%"
              dataKey="value"
              animationDuration={400}
              stroke="#1f2937"
              strokeWidth={2}
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="space-y-2">
        {sortedData.map((item, index) => {
          const originalIndex = data.findIndex(d => d.name === item.name);
          return (
            <div key={item.name} className="flex items-center gap-2">
              <div
                className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                style={{ backgroundColor: COLORS[originalIndex % COLORS.length] }}
              />
              <span className="text-sm text-gray-300">{item.name}</span>
              <span className="text-sm text-gray-500 tabular-nums">{item.percentage.toFixed(1)}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AllocationPie;
