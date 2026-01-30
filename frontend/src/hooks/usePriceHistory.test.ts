import { describe, it, expect } from 'vitest';
import {
  calculateIndicators,
  generateIndicatorSeries,
  generateBollingerBandsSeries,
  generateRSISeries,
  generateMACDSeries,
} from './usePriceHistory';
import { PriceBar } from '../api/types';

// Generate mock price data
const generateMockBars = (count: number, startPrice: number = 100): PriceBar[] => {
  const bars: PriceBar[] = [];
  let price = startPrice;

  for (let i = 0; i < count; i++) {
    const change = (Math.random() - 0.5) * 5;
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.random() * 2;
    const low = Math.min(open, close) - Math.random() * 2;

    const date = new Date();
    date.setDate(date.getDate() - (count - i));

    bars.push({
      timestamp: date.toISOString(),
      open,
      high,
      low,
      close,
      volume: Math.floor(Math.random() * 1000000) + 100000,
    });

    price = close;
  }

  return bars;
};

describe('usePriceHistory', () => {
  describe('calculateIndicators', () => {
    it('should return empty object for empty data', () => {
      const result = calculateIndicators([]);
      expect(result).toEqual({});
    });

    it('should calculate SMA20 when enough data is available', () => {
      const bars = generateMockBars(30);
      const result = calculateIndicators(bars);

      expect(result.sma20).toBeDefined();
      expect(typeof result.sma20).toBe('number');
      expect(result.sma20).toBeGreaterThan(0);
    });

    it('should not calculate SMA50 when insufficient data', () => {
      const bars = generateMockBars(30);
      const result = calculateIndicators(bars);

      expect(result.sma50).toBeUndefined();
    });

    it('should calculate SMA50 when enough data is available', () => {
      const bars = generateMockBars(60);
      const result = calculateIndicators(bars);

      expect(result.sma50).toBeDefined();
      expect(typeof result.sma50).toBe('number');
    });

    it('should calculate RSI', () => {
      const bars = generateMockBars(30);
      const result = calculateIndicators(bars);

      expect(result.rsi).toBeDefined();
      expect(result.rsi).toBeGreaterThanOrEqual(0);
      expect(result.rsi).toBeLessThanOrEqual(100);
    });

    it('should calculate MACD', () => {
      const bars = generateMockBars(35);
      const result = calculateIndicators(bars);

      expect(result.macd).toBeDefined();
      expect(result.macd?.macd).toBeDefined();
      expect(result.macd?.signal).toBeDefined();
      expect(result.macd?.histogram).toBeDefined();
    });

    it('should calculate Bollinger Bands', () => {
      const bars = generateMockBars(25);
      const result = calculateIndicators(bars);

      expect(result.bollingerBands).toBeDefined();
      expect(result.bollingerBands?.upper).toBeGreaterThan(result.bollingerBands?.middle || 0);
      expect(result.bollingerBands?.lower).toBeLessThan(result.bollingerBands?.middle || 0);
    });

    it('should calculate ATR', () => {
      const bars = generateMockBars(20);
      const result = calculateIndicators(bars);

      expect(result.atr).toBeDefined();
      expect(result.atr).toBeGreaterThan(0);
    });
  });

  describe('generateIndicatorSeries', () => {
    it('should generate SMA series with correct length', () => {
      const bars = generateMockBars(30);
      const series = generateIndicatorSeries(bars, 20, 'sma');

      expect(series.length).toBe(bars.length - 19); // period - 1 fewer points
      expect(series[0]).toHaveProperty('time');
      expect(series[0]).toHaveProperty('value');
    });

    it('should generate EMA series', () => {
      const bars = generateMockBars(30);
      const series = generateIndicatorSeries(bars, 12, 'ema');

      expect(series.length).toBeGreaterThan(0);
      expect(series[0]).toHaveProperty('value');
    });
  });

  describe('generateBollingerBandsSeries', () => {
    it('should generate three bands with same length', () => {
      const bars = generateMockBars(30);
      const { upper, middle, lower } = generateBollingerBandsSeries(bars, 20, 2);

      expect(upper.length).toBe(middle.length);
      expect(middle.length).toBe(lower.length);
      expect(upper.length).toBeGreaterThan(0);
    });

    it('should have upper > middle > lower at each point', () => {
      const bars = generateMockBars(30);
      const { upper, middle, lower } = generateBollingerBandsSeries(bars, 20, 2);

      for (let i = 0; i < upper.length; i++) {
        expect(upper[i].value).toBeGreaterThan(middle[i].value);
        expect(middle[i].value).toBeGreaterThan(lower[i].value);
      }
    });
  });

  describe('generateRSISeries', () => {
    it('should generate RSI values between 0 and 100', () => {
      const bars = generateMockBars(50);
      const series = generateRSISeries(bars, 14);

      expect(series.length).toBeGreaterThan(0);
      series.forEach((point) => {
        expect(point.value).toBeGreaterThanOrEqual(0);
        expect(point.value).toBeLessThanOrEqual(100);
      });
    });

    it('should return empty array for insufficient data', () => {
      const bars = generateMockBars(10);
      const series = generateRSISeries(bars, 14);

      expect(series.length).toBe(0);
    });
  });

  describe('generateMACDSeries', () => {
    it('should generate MACD line, signal line, and histogram', () => {
      const bars = generateMockBars(50);
      const { macdLine, signalLine, histogram } = generateMACDSeries(bars);

      expect(macdLine.length).toBeGreaterThan(0);
      expect(signalLine.length).toBeGreaterThan(0);
      expect(histogram.length).toBeGreaterThan(0);
    });

    it('should have histogram as difference between MACD and signal', () => {
      const bars = generateMockBars(50);
      const { macdLine, signalLine, histogram } = generateMACDSeries(bars);

      // Check a few points where all three series overlap
      const startIdx = macdLine.length - histogram.length;
      for (let i = 0; i < Math.min(5, histogram.length); i++) {
        const macdVal = macdLine[startIdx + i].value;
        const signalVal = signalLine[i].value;
        const histVal = histogram[i].value;

        expect(Math.abs(histVal - (macdVal - signalVal))).toBeLessThan(0.01);
      }
    });

    it('should return empty arrays for insufficient data', () => {
      const bars = generateMockBars(20);
      const { macdLine, signalLine, histogram } = generateMACDSeries(bars);

      expect(macdLine.length).toBe(0);
      expect(signalLine.length).toBe(0);
      expect(histogram.length).toBe(0);
    });
  });
});
