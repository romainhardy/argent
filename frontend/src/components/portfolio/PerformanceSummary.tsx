import { TrendingUp, TrendingDown, DollarSign, PieChart, Calendar } from 'lucide-react';
import { Portfolio } from '../../api/types';

interface PerformanceSummaryProps {
  portfolio: Portfolio;
}

export function PerformanceSummary({ portfolio }: PerformanceSummaryProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatLargeCurrency = (value: number) => {
    if (Math.abs(value) >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`;
    }
    if (Math.abs(value) >= 1000) {
      return `$${(value / 1000).toFixed(2)}K`;
    }
    return formatCurrency(value);
  };

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const StatCard = ({
    icon: Icon,
    label,
    value,
    subValue,
    valueColor = 'text-white',
    iconColor = 'text-gray-400',
  }: {
    icon: React.ComponentType<{ className?: string }>;
    label: string;
    value: string;
    subValue?: string;
    valueColor?: string;
    iconColor?: string;
  }) => (
    <div className="bg-gray-700/30 rounded-lg p-3">
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className={`w-3.5 h-3.5 ${iconColor}`} />
        <span className="text-xs text-gray-400 whitespace-nowrap">{label}</span>
      </div>
      <div className={`text-xl font-bold ${valueColor}`}>{value}</div>
      {subValue && <div className="text-xs text-gray-500 mt-0.5 whitespace-nowrap">{subValue}</div>}
    </div>
  );

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-white">{portfolio.name}</h3>
          <span className="text-sm text-gray-400">Portfolio Overview</span>
        </div>
      </div>

      <div className="p-4">
        {/* Main stats */}
        <div className="grid grid-cols-4 gap-3 mb-4">
          <StatCard
            icon={DollarSign}
            label="Total Value"
            value={formatLargeCurrency(portfolio.totalValue)}
            iconColor="text-primary-400"
          />

          <StatCard
            icon={portfolio.dayChange >= 0 ? TrendingUp : TrendingDown}
            label="Day Change"
            value={formatCurrency(portfolio.dayChange)}
            subValue={formatPercent(portfolio.dayChangePercent)}
            valueColor={portfolio.dayChange >= 0 ? 'text-green-400' : 'text-red-400'}
            iconColor={portfolio.dayChange >= 0 ? 'text-green-400' : 'text-red-400'}
          />

          <StatCard
            icon={portfolio.totalReturn >= 0 ? TrendingUp : TrendingDown}
            label="Total Return"
            value={formatCurrency(portfolio.totalReturn)}
            subValue={formatPercent(portfolio.totalReturnPercent)}
            valueColor={portfolio.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}
            iconColor={portfolio.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}
          />

          <StatCard
            icon={PieChart}
            label="Cash"
            value={formatLargeCurrency(portfolio.cashBalance)}
            subValue={`${((portfolio.cashBalance / portfolio.totalValue) * 100).toFixed(1)}%`}
            iconColor="text-yellow-400"
          />
        </div>

        {/* Quick breakdown */}
        <div className="bg-gray-700/20 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400">Portfolio Breakdown</span>
          </div>

          <div className="space-y-3">
            {/* Invested vs Cash */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-400">Invested</span>
                <span className="text-white">
                  {formatLargeCurrency(portfolio.totalValue - portfolio.cashBalance)}
                </span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500"
                  style={{
                    width: `${
                      ((portfolio.totalValue - portfolio.cashBalance) / portfolio.totalValue) * 100
                    }%`,
                  }}
                />
              </div>
            </div>

            {/* Position count */}
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-400">Active Positions</span>
              <span className="text-white font-medium">{portfolio.positions.length}</span>
            </div>

            {/* Top holdings */}
            {portfolio.positions.length > 0 && (
              <div>
                <span className="text-sm text-gray-400 block mb-2">Top Holdings</span>
                <div className="space-y-1.5">
                  {portfolio.positions
                    .sort((a, b) => b.allocation - a.allocation)
                    .slice(0, 3)
                    .map((position) => (
                      <div
                        key={position.id}
                        className="flex items-center text-sm"
                      >
                        <span className="text-white font-medium w-14">{position.symbol}</span>
                        <span className="text-gray-500 w-12">{position.allocation.toFixed(1)}%</span>
                        <span
                          className={`ml-auto tabular-nums ${
                            position.unrealizedPnLPercent >= 0
                              ? 'text-green-400'
                              : 'text-red-400'
                          }`}
                        >
                          {formatPercent(position.unrealizedPnLPercent)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default PerformanceSummary;
