import { AlertTriangle, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { RiskAnalysis } from '../../api/types';

interface RiskMetricsProps {
  risk: RiskAnalysis;
  symbol?: string;
}

export function RiskMetrics({ risk, symbol }: RiskMetricsProps) {
  const {
    volatility,
    beta,
    sharpeRatio,
    sortinoRatio,
    maxDrawdown,
    valueAtRisk,
    riskLevel,
  } = risk;

  const getRiskLevelConfig = () => {
    switch (riskLevel) {
      case 'low':
        return {
          label: 'Low Risk',
          color: 'text-green-400',
          bgColor: 'bg-green-900/20',
          borderColor: 'border-green-700',
        };
      case 'medium':
        return {
          label: 'Medium Risk',
          color: 'text-yellow-400',
          bgColor: 'bg-yellow-900/20',
          borderColor: 'border-yellow-700',
        };
      case 'high':
        return {
          label: 'High Risk',
          color: 'text-red-400',
          bgColor: 'bg-red-900/20',
          borderColor: 'border-red-700',
        };
      default:
        return {
          label: 'Unknown',
          color: 'text-gray-400',
          bgColor: 'bg-gray-800',
          borderColor: 'border-gray-700',
        };
    }
  };

  const config = getRiskLevelConfig();

  const formatPercent = (value: number, decimals: number = 2) => {
    return `${value >= 0 ? '' : ''}${value.toFixed(decimals)}%`;
  };

  const formatRatio = (value: number | undefined, decimals: number = 2) => {
    if (value === undefined) return 'N/A';
    return value.toFixed(decimals);
  };

  const MetricGauge = ({
    value,
    min,
    max,
    label,
    format,
    goodDirection = 'high',
  }: {
    value: number;
    min: number;
    max: number;
    label: string;
    format: (v: number) => string;
    goodDirection?: 'high' | 'low';
  }) => {
    const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
    const isGood =
      goodDirection === 'high'
        ? percentage > 60
        : percentage < 40;

    return (
      <div className="bg-gray-800/50 rounded-lg p-3">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-400">{label}</span>
          <span
            className={`text-sm font-medium ${
              isGood ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {format(value)}
          </span>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              isGood ? 'bg-green-500' : 'bg-red-500'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex justify-between mt-1 text-xs text-gray-500">
          <span>{format(min)}</span>
          <span>{format(max)}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className={`w-5 h-5 ${config.color}`} />
            <div>
              <h3 className="text-lg font-medium text-white">
                Risk Analysis {symbol && <span className="text-gray-400">- {symbol}</span>}
              </h3>
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${config.bgColor} ${config.borderColor} ${config.color} border`}
          >
            {config.label}
          </span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <MetricGauge
          value={volatility}
          min={0}
          max={100}
          label="Volatility (Annualized)"
          format={formatPercent}
          goodDirection="low"
        />

        {sharpeRatio !== undefined && (
          <MetricGauge
            value={sharpeRatio}
            min={-1}
            max={3}
            label="Sharpe Ratio"
            format={(v) => formatRatio(v)}
            goodDirection="high"
          />
        )}

        <MetricGauge
          value={maxDrawdown}
          min={0}
          max={50}
          label="Max Drawdown"
          format={formatPercent}
          goodDirection="low"
        />

        <MetricGauge
          value={valueAtRisk}
          min={0}
          max={20}
          label="Value at Risk (95%)"
          format={formatPercent}
          goodDirection="low"
        />
      </div>

      {/* Additional metrics */}
      <div className="px-4 pb-4 grid grid-cols-2 md:grid-cols-4 gap-3">
        {beta !== undefined && (
          <div className="bg-gray-700/30 rounded-lg p-3 text-center">
            <Activity className="w-4 h-4 text-gray-400 mx-auto mb-1" />
            <div className="text-xs text-gray-400">Beta</div>
            <div className="text-lg font-medium text-white">{formatRatio(beta)}</div>
          </div>
        )}

        {sortinoRatio !== undefined && (
          <div className="bg-gray-700/30 rounded-lg p-3 text-center">
            <TrendingUp className="w-4 h-4 text-gray-400 mx-auto mb-1" />
            <div className="text-xs text-gray-400">Sortino Ratio</div>
            <div className="text-lg font-medium text-white">{formatRatio(sortinoRatio)}</div>
          </div>
        )}

        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <TrendingDown className="w-4 h-4 text-gray-400 mx-auto mb-1" />
          <div className="text-xs text-gray-400">Max DD</div>
          <div className="text-lg font-medium text-red-400">{formatPercent(maxDrawdown)}</div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <AlertTriangle className="w-4 h-4 text-gray-400 mx-auto mb-1" />
          <div className="text-xs text-gray-400">VaR (95%)</div>
          <div className="text-lg font-medium text-yellow-400">{formatPercent(valueAtRisk)}</div>
        </div>
      </div>
    </div>
  );
}

export default RiskMetrics;
