import { useNavigate } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  PieChart,
  BarChart3,
  ArrowRight,
} from 'lucide-react';
import {
  PageContainer,
  DashboardGrid,
  GridItem,
  Card,
  StatCard,
  LoadingState,
  EmptyState,
} from '../components/layout/DashboardGrid';
import { useAnalysisList } from '../hooks/useAnalysis';
import { AllocationPie } from '../components/charts/AllocationPie';

export function Dashboard() {
  const navigate = useNavigate();
  const analysesQuery = useAnalysisList(5);

  // Mock portfolio data for demo
  const mockPortfolio = {
    totalValue: 125430.50,
    dayChange: 1234.56,
    dayChangePercent: 0.99,
    positions: [
      { name: 'AAPL', value: 35000, percentage: 27.9 },
      { name: 'MSFT', value: 28000, percentage: 22.3 },
      { name: 'GOOGL', value: 22000, percentage: 17.5 },
      { name: 'AMZN', value: 18000, percentage: 14.4 },
      { name: 'Cash', value: 22430.50, percentage: 17.9 },
    ],
  };

  const activeAnalyses = analysesQuery.data?.filter(
    (a) => a.status === 'running' || a.status === 'pending'
  ).length || 0;

  const completedAnalyses = analysesQuery.data?.filter(
    (a) => a.status === 'completed'
  ).length || 0;

  return (
    <PageContainer
      title="Dashboard"
      subtitle="Overview of your financial analysis and portfolio"
    >
      {/* Quick Stats */}
      <DashboardGrid columns={4}>
        <StatCard
          label="Portfolio Value"
          value={`$${(mockPortfolio.totalValue / 1000).toFixed(1)}K`}
          change={mockPortfolio.dayChangePercent}
          changeLabel="today"
          trend={mockPortfolio.dayChangePercent >= 0 ? 'up' : 'down'}
          icon={<PieChart className="w-5 h-5" />}
        />
        <StatCard
          label="Day Change"
          value={`$${mockPortfolio.dayChange.toLocaleString()}`}
          trend={mockPortfolio.dayChange >= 0 ? 'up' : 'down'}
          icon={mockPortfolio.dayChange >= 0 ? <TrendingUp className="w-5 h-5 text-green-400" /> : <TrendingDown className="w-5 h-5 text-red-400" />}
        />
        <StatCard
          label="Active Analyses"
          value={activeAnalyses}
          icon={<Activity className="w-5 h-5" />}
        />
        <StatCard
          label="Completed Analyses"
          value={completedAnalyses}
          icon={<BarChart3 className="w-5 h-5" />}
        />
      </DashboardGrid>

      <DashboardGrid columns={2} gap="lg">
        {/* Portfolio Overview */}
        <GridItem>
          <Card
            title="Portfolio Allocation"
            actions={
              <button
                onClick={() => navigate('/portfolio')}
                className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
              >
                View Details <ArrowRight className="w-4 h-4" />
              </button>
            }
          >
            <AllocationPie data={mockPortfolio.positions} height={250} />
          </Card>
        </GridItem>

        {/* Recent Analyses */}
        <GridItem>
          <Card
            title="Recent Analyses"
            actions={
              <button
                onClick={() => navigate('/analysis')}
                className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
              >
                View All <ArrowRight className="w-4 h-4" />
              </button>
            }
            padding={false}
          >
            {analysesQuery.isLoading ? (
              <div className="p-4">
                <LoadingState message="Loading analyses..." />
              </div>
            ) : analysesQuery.data && analysesQuery.data.length > 0 ? (
              <div className="divide-y divide-gray-700">
                {analysesQuery.data.slice(0, 5).map((analysis) => (
                  <button
                    key={analysis.id}
                    onClick={() => navigate(`/analysis?id=${analysis.id}`)}
                    className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-700/30 transition-colors text-left"
                  >
                    <div>
                      <div className="font-medium text-white">
                        {analysis.symbols.join(', ')}
                      </div>
                      <div className="text-sm text-gray-400">
                        {new Date(analysis.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          analysis.status === 'completed'
                            ? 'bg-green-900/50 text-green-400'
                            : analysis.status === 'running'
                            ? 'bg-blue-900/50 text-blue-400'
                            : analysis.status === 'failed'
                            ? 'bg-red-900/50 text-red-400'
                            : 'bg-yellow-900/50 text-yellow-400'
                        }`}
                      >
                        {analysis.status}
                      </span>
                      <ArrowRight className="w-4 h-4 text-gray-500" />
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-4">
                <EmptyState
                  title="No Analyses"
                  message="Start your first analysis to see results here"
                  icon={<TrendingUp className="w-6 h-6" />}
                  action={{
                    label: 'New Analysis',
                    onClick: () => navigate('/analysis'),
                  }}
                />
              </div>
            )}
          </Card>
        </GridItem>

        {/* Quick Actions */}
        <GridItem colSpan="full">
          <Card title="Quick Actions">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <button
                onClick={() => navigate('/analysis')}
                className="flex items-center gap-3 p-4 bg-primary-900/20 border border-primary-800 rounded-lg hover:bg-primary-900/30 transition-colors"
              >
                <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <div className="font-medium text-white">New Analysis</div>
                  <div className="text-sm text-gray-400">Analyze stocks or crypto</div>
                </div>
              </button>

              <button
                onClick={() => navigate('/charts')}
                className="flex items-center gap-3 p-4 bg-gray-700/30 border border-gray-700 rounded-lg hover:bg-gray-700/50 transition-colors"
              >
                <div className="w-10 h-10 bg-gray-600 rounded-lg flex items-center justify-center">
                  <Activity className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <div className="font-medium text-white">View Charts</div>
                  <div className="text-sm text-gray-400">Technical analysis</div>
                </div>
              </button>

              <button
                onClick={() => navigate('/backtest')}
                className="flex items-center gap-3 p-4 bg-gray-700/30 border border-gray-700 rounded-lg hover:bg-gray-700/50 transition-colors"
              >
                <div className="w-10 h-10 bg-gray-600 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <div className="font-medium text-white">Run Backtest</div>
                  <div className="text-sm text-gray-400">Test trading strategies</div>
                </div>
              </button>
            </div>
          </Card>
        </GridItem>

        {/* Market Summary */}
        <GridItem colSpan="full">
          <Card title="Market Summary">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { name: 'S&P 500', value: '5,234.18', change: 0.45 },
                { name: 'NASDAQ', value: '16,428.82', change: -0.23 },
                { name: 'DOW', value: '39,512.84', change: 0.12 },
                { name: 'BTC/USD', value: '67,234.50', change: 2.34 },
              ].map((index) => (
                <div key={index.name} className="bg-gray-700/30 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">{index.name}</div>
                  <div className="text-lg font-medium text-white">{index.value}</div>
                  <div className={`text-sm flex items-center gap-1 ${index.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {index.change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {index.change >= 0 ? '+' : ''}{index.change}%
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </GridItem>
      </DashboardGrid>
    </PageContainer>
  );
}

export default Dashboard;
