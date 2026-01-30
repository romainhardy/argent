import { useState } from 'react';
import { Play } from 'lucide-react';
import { PageContainer, DashboardGrid, GridItem, Card } from '../components/layout/DashboardGrid';
import { EquityCurve } from '../components/charts/EquityCurve';
import { DrawdownChart } from '../components/charts/DrawdownChart';
import { MetricsPanel } from '../components/backtest/MetricsPanel';
import { TradeLog } from '../components/backtest/TradeLog';
import { BacktestResult } from '../api/types';

const MOCK_BACKTEST: BacktestResult = {
  id: '1', strategyName: 'SMA Crossover', symbol: 'AAPL', startDate: '2023-01-01', endDate: '2024-01-01',
  initialCapital: 100000, finalValue: 125000, status: 'completed',
  metrics: { totalReturn: 25, annualizedReturn: 25, sharpeRatio: 1.8, sortinoRatio: 2.1, maxDrawdown: -12, winRate: 58, profitFactor: 1.6, totalTrades: 24, winningTrades: 14, losingTrades: 10, avgWin: 5.2, avgLoss: -3.1, avgHoldingPeriod: 12 },
  equityCurve: Array.from({ length: 252 }, (_, i) => ({ date: new Date(2023, 0, 1 + i).toISOString().split('T')[0], equity: 100000 * (1 + (i / 252) * 0.25 + Math.sin(i / 20) * 0.03), benchmark: 100000 * (1 + (i / 252) * 0.15) })),
  trades: [
    { id: '1', symbol: 'AAPL', entryDate: '2023-01-15', entryPrice: 150, exitDate: '2023-02-10', exitPrice: 162, quantity: 100, side: 'long', pnl: 1200, pnlPercent: 8, status: 'closed' },
    { id: '2', symbol: 'AAPL', entryDate: '2023-03-01', entryPrice: 158, exitDate: '2023-03-20', exitPrice: 152, quantity: 100, side: 'long', pnl: -600, pnlPercent: -3.8, status: 'closed' },
  ],
};

export function Backtest() {
  const [symbol, setSymbol] = useState('AAPL');
  const [strategy, setStrategy] = useState('sma_crossover');
  const [showResults, setShowResults] = useState(true);
  const result = MOCK_BACKTEST;

  return (
    <PageContainer title="Backtest" subtitle="Test trading strategies on historical data">
      <DashboardGrid columns={3} gap="lg">
        <GridItem>
          <Card title="Run Backtest">
            <div className="space-y-4">
              <div><label className="block text-sm text-gray-300 mb-2">Symbol</label><input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} className="input w-full" /></div>
              <div><label className="block text-sm text-gray-300 mb-2">Strategy</label>
                <select value={strategy} onChange={(e) => setStrategy(e.target.value)} className="input w-full">
                  <option value="sma_crossover">SMA Crossover</option>
                  <option value="rsi_mean_reversion">RSI Mean Reversion</option>
                  <option value="macd_momentum">MACD Momentum</option>
                </select>
              </div>
              <button onClick={() => setShowResults(true)} className="btn btn-primary w-full flex items-center justify-center gap-2"><Play className="w-4 h-4" />Run Backtest</button>
            </div>
          </Card>
        </GridItem>
        <GridItem colSpan={2}>
          {showResults && <MetricsPanel metrics={result.metrics} initialCapital={result.initialCapital} finalValue={result.finalValue} />}
        </GridItem>
      </DashboardGrid>
      {showResults && (
        <DashboardGrid columns={2} gap="lg">
          <GridItem colSpan="full"><EquityCurve data={result.equityCurve} showBenchmark height={300} /></GridItem>
          <GridItem><DrawdownChart data={result.equityCurve} height={200} /></GridItem>
          <GridItem><TradeLog trades={result.trades} maxHeight={250} /></GridItem>
        </DashboardGrid>
      )}
    </PageContainer>
  );
}

export default Backtest;
