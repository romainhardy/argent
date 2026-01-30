import { useQuery } from '@tanstack/react-query';
import {
  getPortfolio,
  getPortfolioPerformance,
  getTransactions,
  listPortfolios,
} from '../api/endpoints';

export function usePortfolioList() {
  return useQuery({
    queryKey: ['portfolios'],
    queryFn: listPortfolios,
    staleTime: 60000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

export function usePortfolio(portfolioId: string | null) {
  return useQuery({
    queryKey: ['portfolio', portfolioId],
    queryFn: () => getPortfolio(portfolioId!),
    enabled: !!portfolioId,
    staleTime: 30000,
    refetchInterval: 60000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

export function usePortfolioPerformance(portfolioId: string | null, period: string = '1y') {
  return useQuery({
    queryKey: ['portfolioPerformance', portfolioId, period],
    queryFn: () => getPortfolioPerformance(portfolioId!, period),
    enabled: !!portfolioId,
    staleTime: 60000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

export function useTransactions(portfolioId: string | null, limit: number = 50) {
  return useQuery({
    queryKey: ['transactions', portfolioId, limit],
    queryFn: () => getTransactions(portfolioId!, limit),
    enabled: !!portfolioId,
    staleTime: 30000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

// Utility functions for portfolio calculations
export function calculatePortfolioMetrics(positions: { marketValue: number; unrealizedPnL: number }[]) {
  const totalValue = positions.reduce((sum, p) => sum + p.marketValue, 0);
  const totalPnL = positions.reduce((sum, p) => sum + p.unrealizedPnL, 0);
  const totalPnLPercent = totalValue > 0 ? (totalPnL / (totalValue - totalPnL)) * 100 : 0;

  return {
    totalValue,
    totalPnL,
    totalPnLPercent,
  };
}

export function groupPositionsByAllocation(
  positions: { symbol: string; marketValue: number; allocation: number }[]
) {
  return positions.map((p) => ({
    name: p.symbol,
    value: p.marketValue,
    percentage: p.allocation,
  }));
}

export function calculateDiversificationScore(
  positions: { allocation: number }[]
): number {
  if (positions.length === 0) return 0;
  if (positions.length === 1) return 0;

  // Herfindahl-Hirschman Index (inverted for diversification)
  const hhi = positions.reduce((sum, p) => sum + Math.pow(p.allocation / 100, 2), 0);
  const maxDiversification = 1 / positions.length;

  // Normalize to 0-100 scale
  return Math.round((1 - hhi) / (1 - maxDiversification) * 100);
}
