import {
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  Shield,
  Percent,
  Award,
  Clock,
} from 'lucide-react';
import { BacktestMetrics } from '../../api/types';

interface MetricsPanelProps {
  metrics: BacktestMetrics;
  initialCapital: number;
  finalValue: number;
}

export function MetricsPanel({ metrics, initialCapital, finalValue }: MetricsPanelProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const formatRatio = (value: number) => {
    return value.toFixed(2);
  };

  const MetricCard = ({
    icon: Icon,
    label,
    value,
    subLabel,
    valueColor = 'text-white',
    iconColor = 'text-gray-400',
  }: {
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    value: string;
    subLabel?: string;
    valueColor?: string;
    iconColor?: string;
  }) => (
    <div className="bg-gray-700/30 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${iconColor}`} />
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <div className={`text-xl font-bold ${valueColor}`}>{value}</div>
      {subLabel && <div className="text-xs text-gray-500 mt-1">{subLabel}</div>}
    </div>
  );

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="text-lg font-medium text-white">Performance Metrics</h3>
      </div>

      <div className="p-4">
        {/* Primary metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <MetricCard
            icon={metrics.totalReturn >= 0 ? TrendingUp : TrendingDown}
            label="Total Return"
            value={formatPercent(metrics.totalReturn)}
            subLabel={`${formatCurrency(initialCapital)} → ${formatCurrency(finalValue)}`}
            valueColor={metrics.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}
            iconColor={metrics.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}
          />

          <MetricCard
            icon={Activity}
            label="Annualized Return"
            value={formatPercent(metrics.annualizedReturn)}
            valueColor={metrics.annualizedReturn >= 0 ? 'text-green-400' : 'text-red-400'}
          />

          <MetricCard
            icon={Target}
            label="Sharpe Ratio"
            value={formatRatio(metrics.sharpeRatio)}
            subLabel="Risk-adjusted return"
            valueColor={
              metrics.sharpeRatio >= 2
                ? 'text-green-400'
                : metrics.sharpeRatio >= 1
                ? 'text-yellow-400'
                : 'text-red-400'
            }
          />

          <MetricCard
            icon={Shield}
            label="Max Drawdown"
            value={formatPercent(metrics.maxDrawdown)}
            valueColor="text-red-400"
            iconColor="text-red-400"
          />
        </div>

        {/* Secondary metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <MetricCard
            icon={Percent}
            label="Win Rate"
            value={`${metrics.winRate.toFixed(1)}%`}
            subLabel={`${metrics.winningTrades}W / ${metrics.losingTrades}L`}
            valueColor={metrics.winRate >= 50 ? 'text-green-400' : 'text-red-400'}
          />

          <MetricCard
            icon={Award}
            label="Profit Factor"
            value={formatRatio(metrics.profitFactor)}
            valueColor={metrics.profitFactor >= 1.5 ? 'text-green-400' : 'text-yellow-400'}
          />

          <MetricCard
            icon={Activity}
            label="Sortino Ratio"
            value={formatRatio(metrics.sortinoRatio)}
            subLabel="Downside risk-adjusted"
          />

          <MetricCard
            icon={Clock}
            label="Avg Holding Period"
            value={`${metrics.avgHoldingPeriod.toFixed(1)}d`}
            subLabel="Average trade duration"
          />
        </div>

        {/* Trade statistics */}
        <div className="bg-gray-700/20 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Trade Statistics</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">Total Trades</div>
              <div className="text-lg font-medium text-white">{metrics.totalTrades}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">Winning Trades</div>
              <div className="text-lg font-medium text-green-400">{metrics.winningTrades}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">Average Win</div>
              <div className="text-lg font-medium text-green-400">
                {formatPercent(metrics.avgWin)}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">Average Loss</div>
              <div className="text-lg font-medium text-red-400">
                {formatPercent(metrics.avgLoss)}
              </div>
            </div>
          </div>

          {/* Risk/Reward visualization */}
          <div className="mt-4">
            <div className="text-xs text-gray-500 mb-2">Risk/Reward Profile</div>
            <div className="flex items-center gap-2">
              <div className="flex-1">
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden flex">
                  <div
                    className="h-full bg-green-500"
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, (Math.abs(metrics.avgWin) / (Math.abs(metrics.avgWin) + Math.abs(metrics.avgLoss))) * 100)
                      )}%`,
                    }}
                  />
                  <div
                    className="h-full bg-red-500"
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, (Math.abs(metrics.avgLoss) / (Math.abs(metrics.avgWin) + Math.abs(metrics.avgLoss))) * 100)
                      )}%`,
                    }}
                  />
                </div>
              </div>
              <span className="text-sm text-gray-400">
                {(Math.abs(metrics.avgWin) / Math.abs(metrics.avgLoss)).toFixed(2)}:1
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MetricsPanel;
