import { useState, useMemo, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Settings2, RefreshCw } from 'lucide-react';
import {
  PageContainer,
  DashboardGrid,
  Card,
  LoadingState,
  ErrorState,
} from '../components/layout/DashboardGrid';
import { CandlestickChart } from '../components/charts/CandlestickChart';
import { IndicatorPanel } from '../components/charts/IndicatorPanel';
import { usePriceHistory, useCurrentPrice, calculateIndicators } from '../hooks/usePriceHistory';

const INTERVALS = [
  { value: '1d', label: '1D' },
  { value: '1h', label: '1H' },
  { value: '4h', label: '4H' },
  { value: '1w', label: '1W' },
];

const PERIODS = [
  { value: '1mo', label: '1M' },
  { value: '3mo', label: '3M' },
  { value: '6mo', label: '6M' },
  { value: '1y', label: '1Y' },
  { value: '2y', label: '2Y' },
];

export function Charts() {
  const [searchParams, setSearchParams] = useSearchParams();
  const symbolParam = searchParams.get('symbol');

  const [symbol, setSymbol] = useState(symbolParam || 'AAPL');
  const [searchInput, setSearchInput] = useState(symbolParam || 'AAPL');

  // Sync state with URL params when they change (e.g., from Header search)
  useEffect(() => {
    if (symbolParam && symbolParam !== symbol) {
      setSymbol(symbolParam);
      setSearchInput(symbolParam);
    }
  }, [symbolParam, symbol]);
  const [interval, setInterval] = useState('1d');
  const [period, setPeriod] = useState('1y');
  const [showBollingerBands, setShowBollingerBands] = useState(false);
  const [showSMA, setShowSMA] = useState(true);
  const [showRSI, setShowRSI] = useState(true);
  const [showMACD, setShowMACD] = useState(true);

  const priceHistoryQuery = usePriceHistory(symbol, interval, period);
  const currentPriceQuery = useCurrentPrice(symbol);

  const indicators = useMemo(() => {
    if (priceHistoryQuery.data?.bars) {
      return calculateIndicators(priceHistoryQuery.data.bars);
    }
    return {};
  }, [priceHistoryQuery.data]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      const newSymbol = searchInput.trim().toUpperCase();
      setSymbol(newSymbol);
      setSearchParams({ symbol: newSymbol });
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(price);
  };

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  return (
    <PageContainer title="Charts" subtitle="Technical analysis and price charts">
      {/* Search and controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
              placeholder="Enter symbol"
              className="input pl-10 w-40"
            />
          </div>
          <button type="submit" className="btn btn-primary">Load</button>
        </form>

        <div className="flex items-center gap-4">
          <div className="flex bg-gray-800 rounded-lg p-1">
            {INTERVALS.map((i) => (
              <button
                key={i.value}
                onClick={() => setInterval(i.value)}
                className={`px-3 py-1 text-sm rounded ${interval === i.value ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                {i.label}
              </button>
            ))}
          </div>

          <div className="flex bg-gray-800 rounded-lg p-1">
            {PERIODS.map((p) => (
              <button
                key={p.value}
                onClick={() => setPeriod(p.value)}
                className={`px-3 py-1 text-sm rounded ${period === p.value ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'}`}
              >
                {p.label}
              </button>
            ))}
          </div>

          <button onClick={() => priceHistoryQuery.refetch()} className="p-2 hover:bg-gray-800 rounded-lg" title="Refresh">
            <RefreshCw className={`w-5 h-5 text-gray-400 ${priceHistoryQuery.isFetching ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Symbol header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">{symbol}</h2>
          {currentPriceQuery.data && (
            <div className="flex items-center gap-4 mt-1">
              <span className="text-3xl font-bold text-white">{formatPrice(currentPriceQuery.data.price)}</span>
              <span className={`text-lg font-medium ${currentPriceQuery.data.changePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatPercent(currentPriceQuery.data.changePercent)}
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Settings2 className="w-4 h-4 text-gray-400" />
          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input type="checkbox" checked={showSMA} onChange={(e) => setShowSMA(e.target.checked)} className="rounded" />SMA
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input type="checkbox" checked={showBollingerBands} onChange={(e) => setShowBollingerBands(e.target.checked)} className="rounded" />BB
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input type="checkbox" checked={showRSI} onChange={(e) => setShowRSI(e.target.checked)} className="rounded" />RSI
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input type="checkbox" checked={showMACD} onChange={(e) => setShowMACD(e.target.checked)} className="rounded" />MACD
          </label>
        </div>
      </div>

      {/* Charts */}
      {priceHistoryQuery.isLoading ? (
        <Card><LoadingState message="Loading price data..." /></Card>
      ) : priceHistoryQuery.isError ? (
        <Card><ErrorState message={priceHistoryQuery.error.message} onRetry={() => priceHistoryQuery.refetch()} /></Card>
      ) : priceHistoryQuery.data ? (
        <div className="space-y-4">
          <Card padding={false}>
            <CandlestickChart data={priceHistoryQuery.data.bars} height={500} showSMA={showSMA} showBollingerBands={showBollingerBands} />
          </Card>

          <DashboardGrid columns={2}>
            {showRSI && <IndicatorPanel data={priceHistoryQuery.data.bars} type="rsi" height={150} />}
            {showMACD && <IndicatorPanel data={priceHistoryQuery.data.bars} type="macd" height={150} />}
          </DashboardGrid>

          <Card title="Technical Indicators">
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {indicators.sma20 !== undefined && (
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">SMA (20)</div>
                  <div className="text-white font-medium">{formatPrice(indicators.sma20)}</div>
                </div>
              )}
              {indicators.sma50 !== undefined && (
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">SMA (50)</div>
                  <div className="text-white font-medium">{formatPrice(indicators.sma50)}</div>
                </div>
              )}
              {indicators.rsi !== undefined && (
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">RSI (14)</div>
                  <div className={`font-medium ${indicators.rsi > 70 ? 'text-red-400' : indicators.rsi < 30 ? 'text-green-400' : 'text-white'}`}>
                    {indicators.rsi.toFixed(2)}
                  </div>
                </div>
              )}
              {indicators.macd && (
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">MACD</div>
                  <div className={`font-medium ${indicators.macd.macd >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {indicators.macd.macd.toFixed(2)}
                  </div>
                </div>
              )}
              {indicators.atr !== undefined && (
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <div className="text-xs text-gray-400 mb-1">ATR (14)</div>
                  <div className="text-white font-medium">{indicators.atr.toFixed(2)}</div>
                </div>
              )}
            </div>
          </Card>
        </div>
      ) : null}
    </PageContainer>
  );
}

export default Charts;
