import { useQuery } from '@tanstack/react-query';
import { getCurrentPrice, getPriceHistory } from '../api/endpoints';
import { PriceBar, TechnicalIndicators } from '../api/types';

export function usePriceHistory(
  symbol: string | null,
  interval: string = '1d',
  period: string = '1y'
) {
  return useQuery({
    queryKey: ['priceHistory', symbol, interval, period],
    queryFn: () => getPriceHistory(symbol!, interval, period),
    enabled: !!symbol,
    staleTime: 60000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

export function useCurrentPrice(symbol: string | null) {
  return useQuery({
    queryKey: ['currentPrice', symbol],
    queryFn: () => getCurrentPrice(symbol!),
    enabled: !!symbol,
    refetchInterval: 60000,
    staleTime: 30000,
    refetchOnWindowFocus: false,
    placeholderData: (previousData) => previousData,
  });
}

// Calculate technical indicators from price data
export function calculateIndicators(bars: PriceBar[]): TechnicalIndicators {
  if (bars.length === 0) return {};

  const closes = bars.map((b) => b.close);
  const highs = bars.map((b) => b.high);
  const lows = bars.map((b) => b.low);

  return {
    sma20: calculateSMA(closes, 20),
    sma50: calculateSMA(closes, 50),
    sma200: calculateSMA(closes, 200),
    ema12: calculateEMA(closes, 12),
    ema26: calculateEMA(closes, 26),
    rsi: calculateRSI(closes, 14),
    macd: calculateMACD(closes),
    bollingerBands: calculateBollingerBands(closes, 20, 2),
    atr: calculateATR(highs, lows, closes, 14),
  };
}

function calculateSMA(data: number[], period: number): number | undefined {
  if (data.length < period) return undefined;
  const sum = data.slice(-period).reduce((a, b) => a + b, 0);
  return sum / period;
}

function calculateEMA(data: number[], period: number): number | undefined {
  if (data.length < period) return undefined;

  const multiplier = 2 / (period + 1);
  let ema = data.slice(0, period).reduce((a, b) => a + b, 0) / period;

  for (let i = period; i < data.length; i++) {
    ema = (data[i] - ema) * multiplier + ema;
  }

  return ema;
}

function calculateRSI(data: number[], period: number = 14): number | undefined {
  if (data.length < period + 1) return undefined;

  let gains = 0;
  let losses = 0;

  for (let i = 1; i <= period; i++) {
    const change = data[i] - data[i - 1];
    if (change > 0) gains += change;
    else losses -= change;
  }

  let avgGain = gains / period;
  let avgLoss = losses / period;

  for (let i = period + 1; i < data.length; i++) {
    const change = data[i] - data[i - 1];
    if (change > 0) {
      avgGain = (avgGain * (period - 1) + change) / period;
      avgLoss = (avgLoss * (period - 1)) / period;
    } else {
      avgGain = (avgGain * (period - 1)) / period;
      avgLoss = (avgLoss * (period - 1) - change) / period;
    }
  }

  if (avgLoss === 0) return 100;
  const rs = avgGain / avgLoss;
  return 100 - 100 / (1 + rs);
}

function calculateMACD(
  data: number[]
): { macd: number; signal: number; histogram: number } | undefined {
  const ema12 = calculateEMA(data, 12);
  const ema26 = calculateEMA(data, 26);

  if (ema12 === undefined || ema26 === undefined) return undefined;

  // Calculate MACD line
  const macdValues: number[] = [];
  let ema12Running = data.slice(0, 12).reduce((a, b) => a + b, 0) / 12;
  let ema26Running = data.slice(0, 26).reduce((a, b) => a + b, 0) / 26;

  for (let i = 26; i < data.length; i++) {
    ema12Running = (data[i] - ema12Running) * (2 / 13) + ema12Running;
    ema26Running = (data[i] - ema26Running) * (2 / 27) + ema26Running;
    macdValues.push(ema12Running - ema26Running);
  }

  const macdLine = ema12 - ema26;
  const signalLine = calculateEMA(macdValues, 9) || macdLine;

  return {
    macd: macdLine,
    signal: signalLine,
    histogram: macdLine - signalLine,
  };
}

function calculateBollingerBands(
  data: number[],
  period: number = 20,
  stdDev: number = 2
): { upper: number; middle: number; lower: number } | undefined {
  if (data.length < period) return undefined;

  const sma = calculateSMA(data, period);
  if (sma === undefined) return undefined;

  const recentData = data.slice(-period);
  const squaredDiffs = recentData.map((v) => Math.pow(v - sma, 2));
  const variance = squaredDiffs.reduce((a, b) => a + b, 0) / period;
  const std = Math.sqrt(variance);

  return {
    upper: sma + stdDev * std,
    middle: sma,
    lower: sma - stdDev * std,
  };
}

function calculateATR(
  highs: number[],
  lows: number[],
  closes: number[],
  period: number = 14
): number | undefined {
  if (highs.length < period + 1) return undefined;

  const trueRanges: number[] = [];

  for (let i = 1; i < highs.length; i++) {
    const tr = Math.max(
      highs[i] - lows[i],
      Math.abs(highs[i] - closes[i - 1]),
      Math.abs(lows[i] - closes[i - 1])
    );
    trueRanges.push(tr);
  }

  return calculateSMA(trueRanges, period);
}

// Generate indicator series for charting
export function generateIndicatorSeries(bars: PriceBar[], period: number, type: 'sma' | 'ema') {
  const closes = bars.map((b) => b.close);
  const result: { time: string; value: number }[] = [];

  for (let i = period - 1; i < closes.length; i++) {
    const slice = closes.slice(i - period + 1, i + 1);
    const value =
      type === 'sma'
        ? slice.reduce((a, b) => a + b, 0) / period
        : calculateEMAForSeries(slice, period);

    result.push({
      time: bars[i].timestamp.split('T')[0],
      value,
    });
  }

  return result;
}

function calculateEMAForSeries(data: number[], period: number): number {
  const multiplier = 2 / (period + 1);
  let ema = data[0];

  for (let i = 1; i < data.length; i++) {
    ema = (data[i] - ema) * multiplier + ema;
  }

  return ema;
}

export function generateBollingerBandsSeries(bars: PriceBar[], period: number = 20, stdDev: number = 2) {
  const closes = bars.map((b) => b.close);
  const upper: { time: string; value: number }[] = [];
  const middle: { time: string; value: number }[] = [];
  const lower: { time: string; value: number }[] = [];

  for (let i = period - 1; i < closes.length; i++) {
    const slice = closes.slice(i - period + 1, i + 1);
    const sma = slice.reduce((a, b) => a + b, 0) / period;
    const variance = slice.reduce((sum, val) => sum + Math.pow(val - sma, 2), 0) / period;
    const std = Math.sqrt(variance);

    const time = bars[i].timestamp.split('T')[0];
    upper.push({ time, value: sma + stdDev * std });
    middle.push({ time, value: sma });
    lower.push({ time, value: sma - stdDev * std });
  }

  return { upper, middle, lower };
}

export function generateRSISeries(bars: PriceBar[], period: number = 14) {
  const closes = bars.map((b) => b.close);
  const result: { time: string; value: number }[] = [];

  if (closes.length < period + 1) return result;

  let avgGain = 0;
  let avgLoss = 0;

  for (let i = 1; i <= period; i++) {
    const change = closes[i] - closes[i - 1];
    if (change > 0) avgGain += change;
    else avgLoss -= change;
  }

  avgGain /= period;
  avgLoss /= period;

  const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
  result.push({
    time: bars[period].timestamp.split('T')[0],
    value: 100 - 100 / (1 + rs),
  });

  for (let i = period + 1; i < closes.length; i++) {
    const change = closes[i] - closes[i - 1];
    if (change > 0) {
      avgGain = (avgGain * (period - 1) + change) / period;
      avgLoss = (avgLoss * (period - 1)) / period;
    } else {
      avgGain = (avgGain * (period - 1)) / period;
      avgLoss = (avgLoss * (period - 1) - change) / period;
    }

    const currentRs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    result.push({
      time: bars[i].timestamp.split('T')[0],
      value: 100 - 100 / (1 + currentRs),
    });
  }

  return result;
}

export function generateMACDSeries(bars: PriceBar[]) {
  const closes = bars.map((b) => b.close);
  const macdLine: { time: string; value: number }[] = [];
  const signalLine: { time: string; value: number }[] = [];
  const histogram: { time: string; value: number; color: string }[] = [];

  if (closes.length < 26) return { macdLine, signalLine, histogram };

  let ema12 = closes.slice(0, 12).reduce((a, b) => a + b, 0) / 12;
  let ema26 = closes.slice(0, 26).reduce((a, b) => a + b, 0) / 26;

  const macdValues: number[] = [];

  for (let i = 26; i < closes.length; i++) {
    ema12 = (closes[i] - ema12) * (2 / 13) + ema12;
    ema26 = (closes[i] - ema26) * (2 / 27) + ema26;
    const macd = ema12 - ema26;
    macdValues.push(macd);

    macdLine.push({
      time: bars[i].timestamp.split('T')[0],
      value: macd,
    });
  }

  // Calculate signal line (9-period EMA of MACD)
  if (macdValues.length >= 9) {
    let signal = macdValues.slice(0, 9).reduce((a, b) => a + b, 0) / 9;

    for (let i = 8; i < macdValues.length; i++) {
      signal = (macdValues[i] - signal) * (2 / 10) + signal;
      const time = bars[i + 26].timestamp.split('T')[0];
      const histValue = macdValues[i] - signal;

      signalLine.push({ time, value: signal });
      histogram.push({
        time,
        value: histValue,
        color: histValue >= 0 ? '#26a69a' : '#ef5350',
      });
    }
  }

  return { macdLine, signalLine, histogram };
}
