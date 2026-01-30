import { describe, it, expect } from 'vitest';
import {
  calculatePortfolioMetrics,
  groupPositionsByAllocation,
  calculateDiversificationScore,
} from './usePortfolio';

describe('usePortfolio utilities', () => {
  describe('calculatePortfolioMetrics', () => {
    it('should calculate total value correctly', () => {
      const positions = [
        { marketValue: 10000, unrealizedPnL: 500 },
        { marketValue: 20000, unrealizedPnL: -200 },
        { marketValue: 15000, unrealizedPnL: 1000 },
      ];

      const result = calculatePortfolioMetrics(positions);

      expect(result.totalValue).toBe(45000);
    });

    it('should calculate total P&L correctly', () => {
      const positions = [
        { marketValue: 10000, unrealizedPnL: 500 },
        { marketValue: 20000, unrealizedPnL: -200 },
        { marketValue: 15000, unrealizedPnL: 1000 },
      ];

      const result = calculatePortfolioMetrics(positions);

      expect(result.totalPnL).toBe(1300);
    });

    it('should calculate P&L percent correctly', () => {
      const positions = [
        { marketValue: 11000, unrealizedPnL: 1000 }, // Cost was 10000
      ];

      const result = calculatePortfolioMetrics(positions);

      expect(result.totalPnLPercent).toBeCloseTo(10, 1); // 10% gain
    });

    it('should handle empty positions', () => {
      const result = calculatePortfolioMetrics([]);

      expect(result.totalValue).toBe(0);
      expect(result.totalPnL).toBe(0);
      expect(result.totalPnLPercent).toBe(0);
    });
  });

  describe('groupPositionsByAllocation', () => {
    it('should transform positions to allocation format', () => {
      const positions = [
        { symbol: 'AAPL', marketValue: 10000, allocation: 50 },
        { symbol: 'GOOGL', marketValue: 10000, allocation: 50 },
      ];

      const result = groupPositionsByAllocation(positions);

      expect(result).toHaveLength(2);
      expect(result[0]).toEqual({ name: 'AAPL', value: 10000, percentage: 50 });
      expect(result[1]).toEqual({ name: 'GOOGL', value: 10000, percentage: 50 });
    });
  });

  describe('calculateDiversificationScore', () => {
    it('should return 0 for empty portfolio', () => {
      const score = calculateDiversificationScore([]);
      expect(score).toBe(0);
    });

    it('should return 0 for single position', () => {
      const score = calculateDiversificationScore([{ allocation: 100 }]);
      expect(score).toBe(0);
    });

    it('should return high score for evenly distributed portfolio', () => {
      // 4 positions with 25% each is very diversified
      const positions = [
        { allocation: 25 },
        { allocation: 25 },
        { allocation: 25 },
        { allocation: 25 },
      ];

      const score = calculateDiversificationScore(positions);

      expect(score).toBeGreaterThan(90); // Should be close to 100
    });

    it('should return lower score for concentrated portfolio', () => {
      // One position dominates
      const positions = [
        { allocation: 80 },
        { allocation: 10 },
        { allocation: 5 },
        { allocation: 5 },
      ];

      const score = calculateDiversificationScore(positions);

      expect(score).toBeLessThan(50); // More concentrated = lower score
    });

    it('should return score between 0 and 100', () => {
      const positions = [
        { allocation: 40 },
        { allocation: 30 },
        { allocation: 20 },
        { allocation: 10 },
      ];

      const score = calculateDiversificationScore(positions);

      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    });
  });
});
