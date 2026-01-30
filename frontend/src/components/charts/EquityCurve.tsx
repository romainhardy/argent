import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { EquityPoint } from '../../api/types';

interface EquityCurveProps {
  data: EquityPoint[];
  showBenchmark?: boolean;
  initialValue?: number;
  height?: number;
}

export function EquityCurve({
  data,
  showBenchmark = true,
  initialValue = 100000,
  height = 300,
}: EquityCurveProps) {
  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-800 rounded-lg">
        <p className="text-gray-400">No equity data available</p>
      </div>
    );
  }

  // Calculate percentage returns for display
  const chartData = data.map((point) => ({
    date: point.date,
    equity: point.equity,
    benchmark: point.benchmark,
    equityReturn: ((point.equity - initialValue) / initialValue) * 100,
    benchmarkReturn: point.benchmark
      ? ((point.benchmark - initialValue) / initialValue) * 100
      : undefined,
  }));

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; dataKey: string }>; label?: string }) => {
    if (active && payload && payload.length > 0) {
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-400 text-sm mb-2">{label}</p>
          {payload.map((entry) => (
            <div key={entry.dataKey} className="flex justify-between gap-4 text-sm">
              <span className={entry.dataKey === 'equity' ? 'text-primary-400' : 'text-gray-400'}>
                {entry.dataKey === 'equity' ? 'Strategy' : 'Benchmark'}:
              </span>
              <span className="text-white font-medium">
                {formatCurrency(entry.value)}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  const minValue = Math.min(...chartData.map((d) => Math.min(d.equity, d.benchmark || Infinity)));
  const maxValue = Math.max(...chartData.map((d) => Math.max(d.equity, d.benchmark || 0)));
  const padding = (maxValue - minValue) * 0.1;

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-white">Equity Curve</h3>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-primary-500 rounded-full" />
            <span className="text-gray-400">Strategy</span>
            <span className={`font-medium ${chartData[chartData.length - 1].equityReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatPercent(chartData[chartData.length - 1].equityReturn)}
            </span>
          </div>
          {showBenchmark && chartData[0].benchmark !== undefined && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gray-500 rounded-full" />
              <span className="text-gray-400">Benchmark</span>
              <span className={`font-medium ${(chartData[chartData.length - 1].benchmarkReturn || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatPercent(chartData[chartData.length - 1].benchmarkReturn || 0)}
              </span>
            </div>
          )}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
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
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            domain={[minValue - padding, maxValue + padding]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <ReferenceLine y={initialValue} stroke="#6b7280" strokeDasharray="3 3" />
          <Line
            type="monotone"
            dataKey="equity"
            name="Strategy"
            stroke="#0ea5e9"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#0ea5e9' }}
          />
          {showBenchmark && (
            <Line
              type="monotone"
              dataKey="benchmark"
              name="Benchmark"
              stroke="#6b7280"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
              activeDot={{ r: 4, fill: '#6b7280' }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default EquityCurve;
