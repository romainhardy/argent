import { ArrowUpRight, ArrowDownRight, Filter } from 'lucide-react';
import { useState } from 'react';
import { Transaction } from '../../api/types';

interface TransactionHistoryProps {
  transactions: Transaction[];
  onFilter?: (filter: { type?: 'buy' | 'sell'; symbol?: string }) => void;
}

export function TransactionHistory({ transactions, onFilter }: TransactionHistoryProps) {
  const [filterType, setFilterType] = useState<'all' | 'buy' | 'sell'>('all');
  const [filterSymbol, setFilterSymbol] = useState<string>('');

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
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const uniqueSymbols = [...new Set(transactions.map((t) => t.symbol))];

  const filteredTransactions = transactions.filter((t) => {
    if (filterType !== 'all' && t.type !== filterType) return false;
    if (filterSymbol && t.symbol !== filterSymbol) return false;
    return true;
  });

  if (transactions.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
        <p className="text-gray-400">No transactions yet</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <h3 className="text-lg font-medium text-white">Transaction History</h3>

        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-gray-400" />

          <select
            value={filterType}
            onChange={(e) => {
              setFilterType(e.target.value as 'all' | 'buy' | 'sell');
              onFilter?.({
                type: e.target.value === 'all' ? undefined : (e.target.value as 'buy' | 'sell'),
                symbol: filterSymbol || undefined,
              });
            }}
            className="bg-gray-700 text-gray-300 text-sm rounded px-2 py-1 border border-gray-600 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="all">All Types</option>
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>

          <select
            value={filterSymbol}
            onChange={(e) => {
              setFilterSymbol(e.target.value);
              onFilter?.({
                type: filterType === 'all' ? undefined : filterType,
                symbol: e.target.value || undefined,
              });
            }}
            className="bg-gray-700 text-gray-300 text-sm rounded px-2 py-1 border border-gray-600 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="">All Symbols</option>
            {uniqueSymbols.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="overflow-x-auto max-h-96 overflow-y-auto">
        <table className="w-full">
          <thead className="sticky top-0 bg-gray-800">
            <tr className="text-left text-sm text-gray-400 border-b border-gray-700">
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium">Type</th>
              <th className="px-4 py-3 font-medium">Symbol</th>
              <th className="px-4 py-3 font-medium text-right">Quantity</th>
              <th className="px-4 py-3 font-medium text-right">Price</th>
              <th className="px-4 py-3 font-medium text-right">Fees</th>
              <th className="px-4 py-3 font-medium text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {filteredTransactions.map((transaction) => (
              <tr
                key={transaction.id}
                className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors"
              >
                <td className="px-4 py-3 text-gray-300 text-sm">
                  {formatDate(transaction.date)}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    {transaction.type === 'buy' ? (
                      <>
                        <ArrowDownRight className="w-4 h-4 text-green-400" />
                        <span className="text-green-400 font-medium text-sm">BUY</span>
                      </>
                    ) : (
                      <>
                        <ArrowUpRight className="w-4 h-4 text-red-400" />
                        <span className="text-red-400 font-medium text-sm">SELL</span>
                      </>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="font-medium text-white">{transaction.symbol}</span>
                </td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {transaction.quantity.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {formatCurrency(transaction.price)}
                </td>
                <td className="px-4 py-3 text-right text-gray-400 text-sm">
                  {transaction.fees ? formatCurrency(transaction.fees) : '-'}
                </td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={`font-medium ${
                      transaction.type === 'buy' ? 'text-red-400' : 'text-green-400'
                    }`}
                  >
                    {transaction.type === 'buy' ? '-' : '+'}
                    {formatCurrency(transaction.total)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredTransactions.length === 0 && (
        <div className="p-8 text-center">
          <p className="text-gray-400">No transactions match the current filter</p>
        </div>
      )}

      <div className="px-4 py-3 bg-gray-700/30 border-t border-gray-700 text-sm text-gray-400">
        Showing {filteredTransactions.length} of {transactions.length} transactions
      </div>
    </div>
  );
}

export default TransactionHistory;
