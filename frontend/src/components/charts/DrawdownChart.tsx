import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { EquityPoint } from '../../api/types';
import { calculateDrawdownSeries } from '../../hooks/useBacktest';

interface DrawdownChartProps {
  data: EquityPoint[];
  height?: number;
}

export function DrawdownChart({ data, height = 200 }: DrawdownChartProps) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 bg-gray-800 rounded-lg">
        <p className="text-gray-400">No drawdown data available</p>
      </div>
    );
  }

  const drawdownData = calculateDrawdownSeries(data);

  const maxDrawdown = Math.min(...drawdownData.map((d) => d.drawdown || 0));

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) => {
    if (active && payload && payload.length > 0) {
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-400 text-sm mb-1">{label}</p>
          <p className="text-red-400 font-medium">
            Drawdown: {payload[0].value.toFixed(2)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-white">Drawdown</h3>
        <div className="text-sm">
          <span className="text-gray-400">Max Drawdown: </span>
          <span className="text-red-400 font-medium">{maxDrawdown.toFixed(2)}%</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={drawdownData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <defs>
            <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            tickFormatter={(value) => {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getFullYear().toString().slice(2)}`;
            }}
          />
          <YAxis
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            tickFormatter={(value) => `${value.toFixed(0)}%`}
            domain={[Math.floor(maxDrawdown * 1.1), 0]}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="#6b7280" />
          <ReferenceLine
            y={maxDrawdown}
            stroke="#ef4444"
            strokeDasharray="3 3"
            label={{
              value: `Max: ${maxDrawdown.toFixed(1)}%`,
              fill: '#ef4444',
              fontSize: 12,
              position: 'right',
            }}
          />
          <Area
            type="monotone"
            dataKey="drawdown"
            stroke="#ef4444"
            fill="url(#drawdownGradient)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default DrawdownChart;
