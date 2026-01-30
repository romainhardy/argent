import { ArrowUpRight, ArrowDownRight, Clock, CheckCircle2 } from 'lucide-react';
import { Trade } from '../../api/types';

interface TradeLogProps {
  trades: Trade[];
  maxHeight?: number;
}

export function TradeLog({ trades, maxHeight = 400 }: TradeLogProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatPercent = (value: number | undefined) => {
    if (value === undefined) return '-';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  if (trades.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
        <p className="text-gray-400">No trades recorded</p>
      </div>
    );
  }

  const closedTrades = trades.filter((t) => t.status === 'closed');
  const openTrades = trades.filter((t) => t.status === 'open');
  const winners = closedTrades.filter((t) => (t.pnl || 0) > 0);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <h3 className="text-lg font-medium text-white">Trade Log</h3>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-gray-400">
            Total: <span className="text-white">{trades.length}</span>
          </span>
          <span className="text-gray-400">
            Win Rate:{' '}
            <span className="text-green-400">
              {closedTrades.length > 0
                ? ((winners.length / closedTrades.length) * 100).toFixed(1)
                : 0}
              %
            </span>
          </span>
          {openTrades.length > 0 && (
            <span className="text-yellow-400">
              {openTrades.length} open
            </span>
          )}
        </div>
      </div>

      <div className="overflow-x-auto" style={{ maxHeight }}>
        <table className="w-full">
          <thead className="sticky top-0 bg-gray-800 z-10">
            <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Symbol</th>
              <th className="px-4 py-3 font-medium">Side</th>
              <th className="px-4 py-3 font-medium">Entry</th>
              <th className="px-4 py-3 font-medium text-right">Entry Price</th>
              <th className="px-4 py-3 font-medium">Exit</th>
              <th className="px-4 py-3 font-medium text-right">Exit Price</th>
              <th className="px-4 py-3 font-medium text-right">Qty</th>
              <th className="px-4 py-3 font-medium text-right">P&L</th>
              <th className="px-4 py-3 font-medium text-right">% Return</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
              <tr
                key={trade.id}
                className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors"
              >
                <td className="px-4 py-3">
                  {trade.status === 'closed' ? (
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                  ) : (
                    <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className="font-medium text-white">{trade.symbol}</span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    {trade.side === 'long' ? (
                      <>
                        <ArrowUpRight className="w-4 h-4 text-green-400" />
                        <span className="text-green-400 text-sm font-medium">LONG</span>
                      </>
                    ) : (
                      <>
                        <ArrowDownRight className="w-4 h-4 text-red-400" />
                        <span className="text-red-400 text-sm font-medium">SHORT</span>
                      </>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-300">
                  {formatDate(trade.entryDate)}
                </td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {formatCurrency(trade.entryPrice)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-300">
                  {trade.exitDate ? formatDate(trade.exitDate) : '-'}
                </td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {trade.exitPrice ? formatCurrency(trade.exitPrice) : '-'}
                </td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {trade.quantity.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right">
                  {trade.pnl !== undefined ? (
                    <span
                      className={`font-medium ${
                        trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {formatCurrency(trade.pnl)}
                    </span>
                  ) : (
                    <span className="text-gray-500">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  {trade.pnlPercent !== undefined ? (
                    <span
                      className={`font-medium ${
                        trade.pnlPercent >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {formatPercent(trade.pnlPercent)}
                    </span>
                  ) : (
                    <span className="text-gray-500">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary footer */}
      <div className="px-4 py-3 bg-gray-700/30 border-t border-gray-700">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400">
            {closedTrades.length} closed, {openTrades.length} open
          </span>
          {closedTrades.length > 0 && (
            <div className="flex gap-4">
              <span className="text-gray-400">
                Total P&L:{' '}
                <span
                  className={`font-medium ${
                    closedTrades.reduce((sum, t) => sum + (t.pnl || 0), 0) >= 0
                      ? 'text-green-400'
                      : 'text-red-400'
                  }`}
                >
                  {formatCurrency(closedTrades.reduce((sum, t) => sum + (t.pnl || 0), 0))}
                </span>
              </span>
              <span className="text-gray-400">
                Avg Win:{' '}
                <span className="text-green-400">
                  {formatCurrency(
                    winners.length > 0
                      ? winners.reduce((sum, t) => sum + (t.pnl || 0), 0) / winners.length
                      : 0
                  )}
                </span>
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TradeLog;
