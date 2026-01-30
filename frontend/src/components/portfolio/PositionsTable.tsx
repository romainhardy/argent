import { TrendingUp, TrendingDown, MoreVertical } from 'lucide-react';
import { Position } from '../../api/types';

interface PositionsTableProps {
  positions: Position[];
  onSelectPosition?: (position: Position) => void;
}

export function PositionsTable({ positions, onSelectPosition }: PositionsTableProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  if (positions.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
        <p className="text-gray-400">No positions in portfolio</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="text-lg font-medium text-white">Positions</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
              <th className="px-4 py-3 font-medium">Symbol</th>
              <th className="px-4 py-3 font-medium text-right">Qty</th>
              <th className="px-4 py-3 font-medium text-right">Avg Cost</th>
              <th className="px-4 py-3 font-medium text-right">Current</th>
              <th className="px-4 py-3 font-medium text-right">Market Value</th>
              <th className="px-4 py-3 font-medium text-right">P&L</th>
              <th className="px-4 py-3 font-medium text-right">% Return</th>
              <th className="px-4 py-3 font-medium text-right">Allocation</th>
              <th className="px-4 py-3 font-medium w-10"></th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position) => (
              <tr
                key={position.id}
                className="border-b border-gray-700/50 hover:bg-gray-700/30 cursor-pointer transition-colors"
                onClick={() => onSelectPosition?.(position)}
              >
                <td className="px-4 py-3">
                  <span className="font-medium text-white">{position.symbol}</span>
                </td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {position.quantity.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {formatCurrency(position.avgCost)}
                </td>
                <td className="px-4 py-3 text-right text-white font-medium">
                  {formatCurrency(position.currentPrice)}
                </td>
                <td className="px-4 py-3 text-right text-white">
                  {formatCurrency(position.marketValue)}
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-1">
                    {position.unrealizedPnL >= 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-400" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-400" />
                    )}
                    <span
                      className={`font-medium ${
                        position.unrealizedPnL >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {formatCurrency(position.unrealizedPnL)}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={`font-medium ${
                      position.unrealizedPnLPercent >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {formatPercent(position.unrealizedPnLPercent)}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500"
                        style={{ width: `${position.allocation}%` }}
                      />
                    </div>
                    <span className="text-gray-300 text-sm w-12 text-right">
                      {position.allocation.toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <button className="p-1 hover:bg-gray-700 rounded">
                    <MoreVertical className="w-4 h-4 text-gray-400" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary row */}
      <div className="px-4 py-3 bg-gray-700/30 border-t border-gray-700">
        <div className="flex justify-between items-center">
          <span className="text-gray-400">
            Total: {positions.length} position{positions.length !== 1 ? 's' : ''}
          </span>
          <div className="flex gap-6">
            <div>
              <span className="text-gray-400 text-sm">Total Value: </span>
              <span className="text-white font-medium">
                {formatCurrency(positions.reduce((sum, p) => sum + p.marketValue, 0))}
              </span>
            </div>
            <div>
              <span className="text-gray-400 text-sm">Total P&L: </span>
              <span
                className={`font-medium ${
                  positions.reduce((sum, p) => sum + p.unrealizedPnL, 0) >= 0
                    ? 'text-green-400'
                    : 'text-red-400'
                }`}
              >
                {formatCurrency(positions.reduce((sum, p) => sum + p.unrealizedPnL, 0))}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PositionsTable;
