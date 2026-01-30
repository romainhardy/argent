import { describe, it, expect } from 'vitest';
import {
  calculateDrawdownSeries,
  calculateRollingMetrics,
  analyzeTradeDistribution,
  compareBacktestMetrics,
} from './useBacktest';
import { EquityPoint, Trade, BacktestResult, BacktestMetrics } from '../api/types';

describe('useBacktest utilities', () => {
  describe('calculateDrawdownSeries', () => {
    it('should return empty array for empty input', () => {
      const result = calculateDrawdownSeries([]);
      expect(result).toEqual([]);
    });

    it('should calculate drawdowns correctly', () => {
      const equityCurve: EquityPoint[] = [
        { date: '2023-01-01', equity: 100 },
        { date: '2023-01-02', equity: 110 }, // New peak
        { date: '2023-01-03', equity: 100 }, // -9.09% drawdown
        { date: '2023-01-04', equity: 105 }, // -4.55% drawdown
        { date: '2023-01-05', equity: 120 }, // New peak, no drawdown
      ];

      const result = calculateDrawdownSeries(equityCurve);

      expect(result[0].drawdown).toBe(0); // First point, no drawdown
      expect(result[1].drawdown).toBe(0); // New peak
      expect(result[2].drawdown).toBeCloseTo(-9.09, 1); // 100 vs 110 peak
      expect(result[4].drawdown).toBe(0); // New peak at 120
    });

    it('should preserve original data', () => {
      const equityCurve: EquityPoint[] = [
        { date: '2023-01-01', equity: 100, benchmark: 100 },
        { date: '2023-01-02', equity: 90, benchmark: 95 },
      ];

      const result = calculateDrawdownSeries(equityCurve);

      expect(result[0].date).toBe('2023-01-01');
      expect(result[0].equity).toBe(100);
      expect(result[0].benchmark).toBe(100);
    });
  });

  describe('calculateRollingMetrics', () => {
    it('should return empty array for insufficient data', () => {
      const equityCurve: EquityPoint[] = Array.from({ length: 20 }, (_, i) => ({
        date: `2023-01-${i + 1}`,
        equity: 100 + i,
      }));

      const result = calculateRollingMetrics(equityCurve, 30);

      expect(result).toEqual([]);
    });

    it('should calculate rolling metrics for sufficient data', () => {
      const equityCurve: EquityPoint[] = Array.from({ length: 60 }, (_, i) => ({
        date: `2023-${String(Math.floor(i / 30) + 1).padStart(2, '0')}-${String((i % 30) + 1).padStart(2, '0')}`,
        equity: 100 * (1 + i * 0.01 + Math.random() * 0.02),
      }));

      const result = calculateRollingMetrics(equityCurve, 30);

      expect(result.length).toBeGreaterThan(0);
      expect(result[0]).toHaveProperty('date');
      expect(result[0]).toHaveProperty('sharpe');
      expect(result[0]).toHaveProperty('volatility');
    });
  });

  describe('analyzeTradeDistribution', () => {
    it('should handle empty trades', () => {
      const result = analyzeTradeDistribution([]);

      expect(result.bins).toEqual([]);
      expect(result.winRate).toBe(0);
      expect(result.avgWin).toBe(0);
      expect(result.avgLoss).toBe(0);
    });

    it('should calculate win rate correctly', () => {
      const trades: Trade[] = [
        { id: '1', symbol: 'AAPL', entryDate: '2023-01-01', entryPrice: 100, exitDate: '2023-01-10', exitPrice: 110, quantity: 10, side: 'long', pnl: 100, pnlPercent: 10, status: 'closed' },
        { id: '2', symbol: 'AAPL', entryDate: '2023-01-11', entryPrice: 110, exitDate: '2023-01-20', exitPrice: 100, quantity: 10, side: 'long', pnl: -100, pnlPercent: -9.09, status: 'closed' },
        { id: '3', symbol: 'AAPL', entryDate: '2023-01-21', entryPrice: 100, exitDate: '2023-01-30', exitPrice: 115, quantity: 10, side: 'long', pnl: 150, pnlPercent: 15, status: 'closed' },
      ];

      const result = analyzeTradeDistribution(trades);

      expect(result.winRate).toBeCloseTo(66.67, 1); // 2 out of 3 trades won
    });

    it('should calculate average win and loss', () => {
      const trades: Trade[] = [
        { id: '1', symbol: 'AAPL', entryDate: '2023-01-01', entryPrice: 100, exitDate: '2023-01-10', exitPrice: 110, quantity: 10, side: 'long', pnl: 100, pnlPercent: 10, status: 'closed' },
        { id: '2', symbol: 'AAPL', entryDate: '2023-01-11', entryPrice: 110, exitDate: '2023-01-20', exitPrice: 100, quantity: 10, side: 'long', pnl: -100, pnlPercent: -10, status: 'closed' },
        { id: '3', symbol: 'AAPL', entryDate: '2023-01-21', entryPrice: 100, exitDate: '2023-01-30', exitPrice: 120, quantity: 10, side: 'long', pnl: 200, pnlPercent: 20, status: 'closed' },
      ];

      const result = analyzeTradeDistribution(trades);

      expect(result.avgWin).toBe(15); // (10 + 20) / 2
      expect(result.avgLoss).toBe(-10); // -10 / 1
    });

    it('should ignore open trades', () => {
      const trades: Trade[] = [
        { id: '1', symbol: 'AAPL', entryDate: '2023-01-01', entryPrice: 100, quantity: 10, side: 'long', status: 'open' },
        { id: '2', symbol: 'AAPL', entryDate: '2023-01-11', entryPrice: 110, exitDate: '2023-01-20', exitPrice: 120, quantity: 10, side: 'long', pnl: 100, pnlPercent: 9.09, status: 'closed' },
      ];

      const result = analyzeTradeDistribution(trades);

      expect(result.winRate).toBe(100); // Only 1 closed trade, which is a winner
    });
  });

  describe('compareBacktestMetrics', () => {
    it('should return empty array for empty input', () => {
      const result = compareBacktestMetrics([]);
      expect(result).toEqual([]);
    });

    it('should compare metrics across strategies', () => {
      const metrics1: BacktestMetrics = {
        totalReturn: 20,
        annualizedReturn: 22,
        sharpeRatio: 1.5,
        sortinoRatio: 2.0,
        maxDrawdown: -10,
        winRate: 60,
        profitFactor: 1.8,
        totalTrades: 50,
        winningTrades: 30,
        losingTrades: 20,
        avgWin: 5,
        avgLoss: -3,
        avgHoldingPeriod: 5,
      };

      const metrics2: BacktestMetrics = {
        totalReturn: 15,
        annualizedReturn: 16,
        sharpeRatio: 1.2,
        sortinoRatio: 1.5,
        maxDrawdown: -15,
        winRate: 55,
        profitFactor: 1.5,
        totalTrades: 40,
        winningTrades: 22,
        losingTrades: 18,
        avgWin: 4,
        avgLoss: -2.5,
        avgHoldingPeriod: 7,
      };

      const results: BacktestResult[] = [
        { id: '1', strategyName: 'Strategy A', symbol: 'AAPL', startDate: '2023-01-01', endDate: '2023-12-31', initialCapital: 100000, finalValue: 120000, metrics: metrics1, equityCurve: [], trades: [], status: 'completed' },
        { id: '2', strategyName: 'Strategy B', symbol: 'AAPL', startDate: '2023-01-01', endDate: '2023-12-31', initialCapital: 100000, finalValue: 115000, metrics: metrics2, equityCurve: [], trades: [], status: 'completed' },
      ];

      const comparison = compareBacktestMetrics(results);

      expect(comparison.length).toBeGreaterThan(0);

      // Find the total return comparison
      const returnComparison = comparison.find((c) => c.metric === 'Total Return (%)');
      expect(returnComparison).toBeDefined();
      expect(returnComparison?.values).toHaveLength(2);

      // Strategy A should be best for total return
      const stratAReturn = returnComparison?.values.find((v) => v.name === 'Strategy A');
      expect(stratAReturn?.best).toBe(true);
    });

    it('should mark lower drawdown as best', () => {
      const metrics1: BacktestMetrics = {
        totalReturn: 20, annualizedReturn: 22, sharpeRatio: 1.5, sortinoRatio: 2.0,
        maxDrawdown: -10, winRate: 60, profitFactor: 1.8, totalTrades: 50,
        winningTrades: 30, losingTrades: 20, avgWin: 5, avgLoss: -3, avgHoldingPeriod: 5,
      };

      const metrics2: BacktestMetrics = {
        totalReturn: 15, annualizedReturn: 16, sharpeRatio: 1.2, sortinoRatio: 1.5,
        maxDrawdown: -5, // Better (lower) drawdown
        winRate: 55, profitFactor: 1.5, totalTrades: 40,
        winningTrades: 22, losingTrades: 18, avgWin: 4, avgLoss: -2.5, avgHoldingPeriod: 7,
      };

      const results: BacktestResult[] = [
        { id: '1', strategyName: 'Strategy A', symbol: 'AAPL', startDate: '2023-01-01', endDate: '2023-12-31', initialCapital: 100000, finalValue: 120000, metrics: metrics1, equityCurve: [], trades: [], status: 'completed' },
        { id: '2', strategyName: 'Strategy B', symbol: 'AAPL', startDate: '2023-01-01', endDate: '2023-12-31', initialCapital: 100000, finalValue: 115000, metrics: metrics2, equityCurve: [], trades: [], status: 'completed' },
      ];

      const comparison = compareBacktestMetrics(results);

      const drawdownComparison = comparison.find((c) => c.metric === 'Max Drawdown (%)');
      const stratBDrawdown = drawdownComparison?.values.find((v) => v.name === 'Strategy B');
      expect(stratBDrawdown?.best).toBe(true); // -5 is better than -10
    });
  });
});
