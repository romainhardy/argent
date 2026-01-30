import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Play, History } from 'lucide-react';
import {
  PageContainer,
  DashboardGrid,
  GridItem,
  Card,
  LoadingState,
  ErrorState,
} from '../components/layout/DashboardGrid';
import {
  useAnalysisList,
  useAnalysisById,
  useStartAnalysis,
} from '../hooks/useAnalysis';
import { AnalysisProgress } from '../components/analysis/AnalysisProgress';
import { RecommendationCard } from '../components/analysis/RecommendationCard';
import { RiskMetrics } from '../components/analysis/RiskMetrics';

export function Analysis() {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedId = searchParams.get('id');

  const [showNewAnalysis, setShowNewAnalysis] = useState(!selectedId);
  const [symbols, setSymbols] = useState('');
  const [assetType, setAssetType] = useState<'stock' | 'crypto'>('stock');

  const analysesQuery = useAnalysisList(20);
  const startAnalysis = useStartAnalysis();

  const analysisQuery = useAnalysisById(selectedId);
  const analysis = analysisQuery.data;
  const analysisLoading = analysisQuery.isLoading;
  const analysisError = analysisQuery.error?.message;

  const handleStartAnalysis = async () => {
    const symbolList = symbols
      .split(/[,\s]+/)
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);

    if (symbolList.length === 0) return;

    try {
      const result = await startAnalysis.mutateAsync({
        symbols: symbolList,
        assetType,
      });
      setSearchParams({ id: result.id });
      setShowNewAnalysis(false);
      setSymbols('');
    } catch (error) {
      console.error('Failed to start analysis:', error);
    }
  };

  const handleSelectAnalysis = (id: string) => {
    setSearchParams({ id });
    setShowNewAnalysis(false);
  };

  return (
    <PageContainer
      title="Analysis"
      subtitle="Run comprehensive financial analysis on stocks and cryptocurrencies"
      actions={
        <button
          onClick={() => {
            setShowNewAnalysis(true);
            setSearchParams({});
          }}
          className="btn btn-primary flex items-center gap-2"
        >
          <Play className="w-4 h-4" />
          New Analysis
        </button>
      }
    >
      <DashboardGrid columns={3} gap="lg">
        {/* Left: History */}
        <GridItem>
          <Card title="Analysis History" padding={false}>
            <div className="max-h-[600px] overflow-y-auto">
              {analysesQuery.isLoading ? (
                <div className="p-4"><LoadingState message="Loading history..." /></div>
              ) : analysesQuery.data && analysesQuery.data.length > 0 ? (
                <div className="divide-y divide-gray-700">
                  {analysesQuery.data.map((a) => (
                    <button
                      key={a.id}
                      onClick={() => handleSelectAnalysis(a.id)}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-700/30 transition-colors ${
                        selectedId === a.id ? 'bg-primary-900/20 border-l-2 border-primary-500' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-white">{a.symbols.join(', ')}</span>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${
                          a.status === 'completed' ? 'bg-green-900/50 text-green-400' :
                          a.status === 'running' ? 'bg-blue-900/50 text-blue-400' :
                          a.status === 'failed' ? 'bg-red-900/50 text-red-400' :
                          'bg-yellow-900/50 text-yellow-400'
                        }`}>
                          {a.status}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400 mt-1">
                        {new Date(a.createdAt).toLocaleString()}
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="p-4 text-center text-gray-400">
                  <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No analysis history</p>
                </div>
              )}
            </div>
          </Card>
        </GridItem>

        {/* Right: Main content */}
        <GridItem colSpan={2}>
          {showNewAnalysis ? (
            <Card title="New Analysis">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Symbols (comma separated)
                  </label>
                  <input
                    type="text"
                    value={symbols}
                    onChange={(e) => setSymbols(e.target.value)}
                    placeholder="e.g., AAPL, GOOGL, MSFT"
                    className="input w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Asset Type</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="assetType" value="stock" checked={assetType === 'stock'} onChange={() => setAssetType('stock')} className="text-primary-500" />
                      <span className="text-gray-300">Stocks</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="assetType" value="crypto" checked={assetType === 'crypto'} onChange={() => setAssetType('crypto')} className="text-primary-500" />
                      <span className="text-gray-300">Crypto</span>
                    </label>
                  </div>
                </div>

                <button
                  onClick={handleStartAnalysis}
                  disabled={!symbols.trim() || startAnalysis.isPending}
                  className="btn btn-primary w-full flex items-center justify-center gap-2"
                >
                  {startAnalysis.isPending ? (
                    <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Starting...</>
                  ) : (
                    <><Play className="w-4 h-4" />Start Analysis</>
                  )}
                </button>

                {startAnalysis.isError && (
                  <div className="p-3 bg-red-900/20 border border-red-800 rounded-lg text-red-400 text-sm">
                    {startAnalysis.error.message}
                  </div>
                )}
              </div>
            </Card>
          ) : selectedId ? (
            <div className="space-y-6">
              {analysisLoading ? (
                <Card><LoadingState message="Loading analysis..." /></Card>
              ) : analysisError ? (
                <Card><ErrorState message={analysisError} onRetry={() => window.location.reload()} /></Card>
              ) : analysis ? (
                <>
                  {(analysis.status === 'running' || analysis.status === 'pending') && (
                    <AnalysisProgress status={analysis.status} progress={null} />
                  )}

                  {analysis.status === 'completed' && analysis.results && (
                    <>
                      {analysis.results.recommendations && analysis.results.recommendations.length > 0 && (
                        <div>
                          <h2 className="text-xl font-bold text-white mb-4">Recommendations</h2>
                          <DashboardGrid columns={2}>
                            {analysis.results.recommendations.map((rec) => (
                              <RecommendationCard key={rec.symbol} recommendation={rec} />
                            ))}
                          </DashboardGrid>
                        </div>
                      )}

                      {analysis.results.risk && Object.keys(analysis.results.risk).length > 0 && (
                        <div>
                          <h2 className="text-xl font-bold text-white mb-4">Risk Analysis</h2>
                          <DashboardGrid columns={2}>
                            {Object.entries(analysis.results.risk).map(([symbol, risk]) => (
                              <RiskMetrics key={symbol} risk={risk} symbol={symbol} />
                            ))}
                          </DashboardGrid>
                        </div>
                      )}

                      {analysis.results.sentiment && Object.keys(analysis.results.sentiment).length > 0 && (
                        <Card title="Sentiment Analysis">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(analysis.results.sentiment).map(([symbol, sentiment]) => (
                              <div key={symbol} className="bg-gray-700/30 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <span className="font-medium text-white">{symbol}</span>
                                  <span className={`px-2 py-1 text-xs rounded-full ${
                                    sentiment.overall === 'bullish' ? 'bg-green-900/50 text-green-400' :
                                    sentiment.overall === 'bearish' ? 'bg-red-900/50 text-red-400' :
                                    'bg-gray-700 text-gray-400'
                                  }`}>
                                    {sentiment.overall}
                                  </span>
                                </div>
                                <div className="space-y-2">
                                  <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">Sentiment Score</span>
                                    <span className="text-white">{sentiment.score.toFixed(2)}</span>
                                  </div>
                                  <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">News Articles</span>
                                    <span className="text-white">{sentiment.newsCount}</span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </Card>
                      )}

                      {/* Show message if analysis completed but no results */}
                      {(!analysis.results.recommendations || analysis.results.recommendations.length === 0) &&
                       (!analysis.results.risk || Object.keys(analysis.results.risk).length === 0) &&
                       (!analysis.results.sentiment || Object.keys(analysis.results.sentiment).length === 0) && (
                        <Card>
                          <div className="text-center py-8">
                            <p className="text-gray-400">Analysis completed but no results were generated.</p>
                            <p className="text-gray-500 text-sm mt-2">This may be due to API configuration issues.</p>
                          </div>
                        </Card>
                      )}
                    </>
                  )}

                  {analysis.status === 'failed' && (
                    <Card><ErrorState title="Analysis Failed" message={analysis.error || 'An error occurred'} /></Card>
                  )}
                </>
              ) : null}
            </div>
          ) : (
            <Card>
              <div className="text-center py-12">
                <Play className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                <h3 className="text-lg font-medium text-white mb-2">Select or Start an Analysis</h3>
                <p className="text-gray-400 mb-4">Choose from history or create a new analysis</p>
                <button onClick={() => setShowNewAnalysis(true)} className="btn btn-primary">New Analysis</button>
              </div>
            </Card>
          )}
        </GridItem>
      </DashboardGrid>
    </PageContainer>
  );
}

export default Analysis;
