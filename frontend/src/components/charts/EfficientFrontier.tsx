import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface PortfolioPoint {
  name: string;
  risk: number; // Standard deviation / volatility
  return: number; // Expected return
  sharpe?: number;
  isOptimal?: boolean;
  isCurrent?: boolean;
}

interface EfficientFrontierProps {
  portfolios: PortfolioPoint[];
  efficientFrontier?: { risk: number; return: number }[];
  riskFreeRate?: number;
  height?: number;
}

export function EfficientFrontier({
  portfolios,
  efficientFrontier = [],
  riskFreeRate = 0.04,
  height = 400,
}: EfficientFrontierProps) {
  if (portfolios.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-800 rounded-lg">
        <p className="text-gray-400">No portfolio data available</p>
      </div>
    );
  }

  const allPoints = [
    ...portfolios.map((p) => ({ ...p, type: 'portfolio' })),
    ...efficientFrontier.map((p, i) => ({
      ...p,
      name: `Frontier ${i}`,
      type: 'frontier',
    })),
  ];

  const minRisk = Math.min(...allPoints.map((p) => p.risk)) * 0.9;
  const maxRisk = Math.max(...allPoints.map((p) => p.risk)) * 1.1;
  const minReturn = Math.min(...allPoints.map((p) => p.return), riskFreeRate) * 0.9;
  const maxReturn = Math.max(...allPoints.map((p) => p.return)) * 1.1;

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: PortfolioPoint & { type: string } }> }) => {
    if (active && payload && payload.length > 0) {
      const point = payload[0].payload;
      if (point.type === 'frontier') return null;

      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-white font-medium mb-2">{point.name}</p>
          <div className="space-y-1 text-sm">
            <p className="text-gray-400">
              Expected Return: <span className="text-green-400">{(point.return * 100).toFixed(2)}%</span>
            </p>
            <p className="text-gray-400">
              Risk (σ): <span className="text-yellow-400">{(point.risk * 100).toFixed(2)}%</span>
            </p>
            {point.sharpe !== undefined && (
              <p className="text-gray-400">
                Sharpe Ratio: <span className="text-primary-400">{point.sharpe.toFixed(2)}</span>
              </p>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  const renderShape = (props: { cx: number; cy: number; payload: PortfolioPoint & { type: string } }) => {
    const { cx, cy, payload } = props;

    if (payload.type === 'frontier') {
      return <circle cx={cx} cy={cy} r={3} fill="#6b7280" />;
    }

    if (payload.isOptimal) {
      return (
        <g>
          <circle cx={cx} cy={cy} r={8} fill="#f59e0b" stroke="#fff" strokeWidth={2} />
          <text
            x={cx}
            y={cy - 15}
            textAnchor="middle"
            fill="#f59e0b"
            fontSize={10}
            fontWeight={600}
          >
            OPTIMAL
          </text>
        </g>
      );
    }

    if (payload.isCurrent) {
      return (
        <g>
          <circle cx={cx} cy={cy} r={8} fill="#0ea5e9" stroke="#fff" strokeWidth={2} />
          <text
            x={cx}
            y={cy - 15}
            textAnchor="middle"
            fill="#0ea5e9"
            fontSize={10}
            fontWeight={600}
          >
            CURRENT
          </text>
        </g>
      );
    }

    return <circle cx={cx} cy={cy} r={5} fill="#6b7280" opacity={0.6} />;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-white">Efficient Frontier</h3>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary-500" />
            <span className="text-gray-400">Current</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-warning" />
            <span className="text-gray-400">Optimal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-500" />
            <span className="text-gray-400">Frontier</span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            type="number"
            dataKey="risk"
            name="Risk"
            domain={[minRisk, maxRisk]}
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            label={{
              value: 'Risk (Volatility)',
              position: 'bottom',
              fill: '#9ca3af',
              fontSize: 12,
            }}
          />
          <YAxis
            type="number"
            dataKey="return"
            name="Return"
            domain={[minReturn, maxReturn]}
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            label={{
              value: 'Expected Return',
              angle: -90,
              position: 'insideLeft',
              fill: '#9ca3af',
              fontSize: 12,
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={riskFreeRate}
            stroke="#6b7280"
            strokeDasharray="3 3"
            label={{
              value: `Rf: ${(riskFreeRate * 100).toFixed(1)}%`,
              fill: '#6b7280',
              fontSize: 10,
              position: 'right',
            }}
          />
          <Scatter
            data={allPoints}
            shape={renderShape}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export default EfficientFrontier;
