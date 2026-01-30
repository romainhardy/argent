import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  compareStrategies,
  getBacktest,
  listBacktests,
  runBacktest,
  RunBacktestParams,
} from '../api/endpoints';
import { BacktestMetrics, BacktestResult, EquityPoint, Trade } from '../api/types';

export function useBacktestList(limit: number = 10) {
  return useQuery({
    queryKey: ['backtests', limit],
    queryFn: () => listBacktests(limit),
    staleTime: 30000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

export function useBacktestById(backtestId: string | null) {
  return useQuery({
    queryKey: ['backtest', backtestId],
    queryFn: () => getBacktest(backtestId!),
    enabled: !!backtestId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'running' || data?.status === 'pending') {
        return 5000;
      }
      return false;
    },
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

export function useRunBacktest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: RunBacktestParams) => runBacktest(params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backtests'] });
    },
  });
}

export function useCompareStrategies(backtestIds: string[]) {
  return useQuery({
    queryKey: ['backtestComparison', backtestIds],
    queryFn: () => compareStrategies(backtestIds),
    enabled: backtestIds.length > 0,
    staleTime: 60000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

// Utility functions for backtest analysis
export function calculateDrawdownSeries(equityCurve: EquityPoint[]): EquityPoint[] {
  if (equityCurve.length === 0) return [];

  let peak = equityCurve[0].equity;
  return equityCurve.map((point) => {
    if (point.equity > peak) peak = point.equity;
    const drawdown = ((point.equity - peak) / peak) * 100;
    return {
      ...point,
      drawdown,
    };
  });
}

export function calculateRollingMetrics(
  equityCurve: EquityPoint[],
  window: number = 30
): { date: string; sharpe: number; volatility: number }[] {
  const result: { date: string; sharpe: number; volatility: number }[] = [];

  if (equityCurve.length < window) return result;

  for (let i = window; i < equityCurve.length; i++) {
    const slice = equityCurve.slice(i - window, i);
    const returns = slice.slice(1).map((p, idx) =>
      (p.equity - slice[idx].equity) / slice[idx].equity
    );

    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
    const volatility = Math.sqrt(variance) * Math.sqrt(252) * 100;
    const sharpe = volatility > 0 ? (avgReturn * 252) / (volatility / 100) : 0;

    result.push({
      date: equityCurve[i].date,
      sharpe,
      volatility,
    });
  }

  return result;
}

export function analyzeTradeDistribution(trades: Trade[]) {
  const closedTrades = trades.filter((t) => t.status === 'closed' && t.pnlPercent !== undefined);

  if (closedTrades.length === 0) {
    return { bins: [], winRate: 0, avgWin: 0, avgLoss: 0 };
  }

  const winners = closedTrades.filter((t) => (t.pnlPercent || 0) > 0);
  const losers = closedTrades.filter((t) => (t.pnlPercent || 0) <= 0);

  const winRate = (winners.length / closedTrades.length) * 100;
  const avgWin = winners.length > 0
    ? winners.reduce((sum, t) => sum + (t.pnlPercent || 0), 0) / winners.length
    : 0;
  const avgLoss = losers.length > 0
    ? losers.reduce((sum, t) => sum + (t.pnlPercent || 0), 0) / losers.length
    : 0;

  // Create histogram bins
  const pnls = closedTrades.map((t) => t.pnlPercent || 0);
  const min = Math.min(...pnls);
  const max = Math.max(...pnls);
  const binCount = 20;
  const binSize = (max - min) / binCount;

  const bins: { range: string; count: number; isPositive: boolean }[] = [];

  for (let i = 0; i < binCount; i++) {
    const start = min + i * binSize;
    const end = start + binSize;
    const count = pnls.filter((p) => p >= start && p < end).length;
    bins.push({
      range: `${start.toFixed(1)}%`,
      count,
      isPositive: start >= 0,
    });
  }

  return { bins, winRate, avgWin, avgLoss };
}

export function compareBacktestMetrics(results: BacktestResult[]): {
  metric: string;
  values: { name: string; value: number; best: boolean }[];
}[] {
  if (results.length === 0) return [];

  const metrics: (keyof BacktestMetrics)[] = [
    'totalReturn',
    'annualizedReturn',
    'sharpeRatio',
    'maxDrawdown',
    'winRate',
    'profitFactor',
  ];

  const metricLabels: Record<string, string> = {
    totalReturn: 'Total Return (%)',
    annualizedReturn: 'Annualized Return (%)',
    sharpeRatio: 'Sharpe Ratio',
    maxDrawdown: 'Max Drawdown (%)',
    winRate: 'Win Rate (%)',
    profitFactor: 'Profit Factor',
  };

  const higherIsBetter: Record<string, boolean> = {
    totalReturn: true,
    annualizedReturn: true,
    sharpeRatio: true,
    maxDrawdown: false,
    winRate: true,
    profitFactor: true,
  };

  return metrics.map((metric) => {
    const values = results.map((r) => ({
      name: r.strategyName,
      value: r.metrics[metric],
    }));

    // For maxDrawdown (negative values), "better" means closer to 0, so use Math.max
    const bestValue = higherIsBetter[metric]
      ? Math.max(...values.map((v) => v.value))
      : metric === 'maxDrawdown'
      ? Math.max(...values.map((v) => v.value)) // -5 is better than -10
      : Math.min(...values.map((v) => v.value));

    return {
      metric: metricLabels[metric] || metric,
      values: values.map((v) => ({
        ...v,
        best: v.value === bestValue,
      })),
    };
  });
}
