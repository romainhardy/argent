import { Trophy, TrendingUp, TrendingDown, Target } from 'lucide-react';
import { BacktestResult } from '../../api/types';
import { compareBacktestMetrics } from '../../hooks/useBacktest';

interface StrategyComparisonProps {
  results: BacktestResult[];
}

export function StrategyComparison({ results }: StrategyComparisonProps) {
  if (results.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
        <p className="text-gray-400">No backtest results to compare</p>
      </div>
    );
  }

  const comparisonData = compareBacktestMetrics(results);

  const formatValue = (metric: string, value: number) => {
    if (metric.includes('%') || metric.includes('Return') || metric.includes('Drawdown') || metric.includes('Win Rate')) {
      return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
    }
    return value.toFixed(2);
  };

  const getValueColor = (metric: string, value: number, isBest: boolean) => {
    if (isBest) {
      return 'text-green-400 font-bold';
    }
    if (metric.includes('Drawdown')) {
      return value <= -20 ? 'text-red-400' : value <= -10 ? 'text-yellow-400' : 'text-gray-300';
    }
    return 'text-gray-300';
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-medium text-white">Strategy Comparison</h3>
        </div>
        <span className="text-sm text-gray-400">{results.length} strategies</span>
      </div>

      {/* Strategy headers */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-400 min-w-[150px]">
                Metric
              </th>
              {results.map((result) => (
                <th
                  key={result.id}
                  className="px-4 py-3 text-center text-sm font-medium min-w-[120px]"
                >
                  <div className="text-white">{result.strategyName}</div>
                  <div className="text-gray-500 text-xs font-normal">{result.symbol}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparisonData.map((row, rowIndex) => (
              <tr
                key={row.metric}
                className={`border-b border-gray-700/50 ${
                  rowIndex % 2 === 0 ? 'bg-gray-800' : 'bg-gray-750'
                }`}
              >
                <td className="px-4 py-3 text-sm text-gray-400">{row.metric}</td>
                {row.values.map((val) => (
                  <td key={val.name} className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-1">
                      {val.best && <Trophy className="w-3 h-3 text-yellow-400" />}
                      <span className={`text-sm ${getValueColor(row.metric, val.value, val.best)}`}>
                        {formatValue(row.metric, val.value)}
                      </span>
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary cards */}
      <div className="p-4 border-t border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {results.map((result) => {
            const isTopPerformer =
              result.metrics.totalReturn ===
              Math.max(...results.map((r) => r.metrics.totalReturn));

            return (
              <div
                key={result.id}
                className={`rounded-lg p-4 ${
                  isTopPerformer
                    ? 'bg-green-900/20 border border-green-800'
                    : 'bg-gray-700/30'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white">{result.strategyName}</span>
                  {isTopPerformer && (
                    <span className="px-2 py-0.5 bg-green-800 text-green-300 text-xs rounded-full">
                      Top Performer
                    </span>
                  )}
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Final Value:</span>
                    <span className="text-white">
                      ${result.finalValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Trades:</span>
                    <span className="text-white">{result.metrics.totalTrades}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Return:</span>
                    <span
                      className={`flex items-center gap-1 ${
                        result.metrics.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {result.metrics.totalReturn >= 0 ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      {result.metrics.totalReturn >= 0 ? '+' : ''}
                      {result.metrics.totalReturn.toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default StrategyComparison;
