import { useState } from 'react';
import { Plus } from 'lucide-react';
import { PageContainer, DashboardGrid, GridItem } from '../components/layout/DashboardGrid';
import { AllocationPie } from '../components/charts/AllocationPie';
import { PositionsTable } from '../components/portfolio/PositionsTable';
import { PerformanceSummary } from '../components/portfolio/PerformanceSummary';
import { EquityCurve } from '../components/charts/EquityCurve';
import { Portfolio as PortfolioType } from '../api/types';

const MOCK_PORTFOLIO: PortfolioType = {
  id: 'demo-1',
  name: 'Main Portfolio',
  totalValue: 125430.50,
  cashBalance: 15230.25,
  dayChange: 1234.56,
  dayChangePercent: 0.99,
  totalReturn: 25430.50,
  totalReturnPercent: 25.43,
  positions: [
    { id: '1', symbol: 'AAPL', quantity: 100, avgCost: 150, currentPrice: 185.5, marketValue: 18550, unrealizedPnL: 3550, unrealizedPnLPercent: 23.67, allocation: 16.8 },
    { id: '2', symbol: 'GOOGL', quantity: 50, avgCost: 120, currentPrice: 145.2, marketValue: 7260, unrealizedPnL: 1260, unrealizedPnLPercent: 21, allocation: 6.6 },
    { id: '3', symbol: 'MSFT', quantity: 75, avgCost: 280, currentPrice: 415.3, marketValue: 31147.5, unrealizedPnL: 10147.5, unrealizedPnLPercent: 48.32, allocation: 28.2 },
    { id: '4', symbol: 'NVDA', quantity: 40, avgCost: 450, currentPrice: 875.6, marketValue: 35024, unrealizedPnL: 17024, unrealizedPnLPercent: 94.58, allocation: 31.7 },
    { id: '5', symbol: 'TSLA', quantity: 30, avgCost: 250, currentPrice: 187.3, marketValue: 5619, unrealizedPnL: -1881, unrealizedPnLPercent: -25.08, allocation: 5.1 },
  ],
};

const MOCK_PERFORMANCE = Array.from({ length: 365 }, (_, i) => {
  const date = new Date(); date.setDate(date.getDate() - (365 - i));
  return { date: date.toISOString().split('T')[0], equity: 100000 * (1 + (i / 365) * 0.25), benchmark: 100000 * (1 + (i / 365) * 0.15) };
});

export function Portfolio() {
  const [activeTab, setActiveTab] = useState<'overview' | 'positions'>('overview');
  const portfolio = MOCK_PORTFOLIO;

  return (
    <PageContainer title="Portfolio" subtitle="Track your investments" actions={<button className="btn btn-primary flex items-center gap-2"><Plus className="w-4 h-4" />Add Position</button>}>
      <div className="flex gap-1 bg-gray-800 p-1 rounded-lg w-fit">
        {(['overview', 'positions'] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 rounded-lg capitalize ${activeTab === tab ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'}`}>{tab}</button>
        ))}
      </div>
      {activeTab === 'overview' ? (
        <DashboardGrid columns={2} gap="lg">
          <GridItem><PerformanceSummary portfolio={portfolio} /></GridItem>
          <GridItem><AllocationPie data={portfolio.positions.map(p => ({ name: p.symbol, value: p.marketValue, percentage: p.allocation }))} height={300} /></GridItem>
          <GridItem colSpan="full"><EquityCurve data={MOCK_PERFORMANCE} showBenchmark height={350} /></GridItem>
        </DashboardGrid>
      ) : (
        <PositionsTable positions={portfolio.positions} onSelectPosition={(p) => window.open(`/charts?symbol=${p.symbol}`, '_blank')} />
      )}
    </PageContainer>
  );
}

export default Portfolio;
