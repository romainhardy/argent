import { useEffect, useRef } from 'react';
import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  LineData,
  HistogramData,
  ColorType,
  CrosshairMode,
} from 'lightweight-charts';
import { PriceBar } from '../../api/types';
import {
  generateIndicatorSeries,
  generateBollingerBandsSeries,
} from '../../hooks/usePriceHistory';

interface CandlestickChartProps {
  data: PriceBar[];
  height?: number;
  showVolume?: boolean;
  showSMA?: boolean;
  showBollingerBands?: boolean;
  smaperiods?: number[];
}

export function CandlestickChart({
  data,
  height = 400,
  showVolume = true,
  showSMA = true,
  showBollingerBands = false,
  smaperiods = [20, 50, 200],
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const legendRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
      layout: {
        background: { type: ColorType.Solid, color: '#1f2937' },
        textColor: '#9ca3af',
      },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: '#6b7280',
          width: 1,
          style: 2,
          labelBackgroundColor: '#374151',
        },
        horzLine: {
          color: '#6b7280',
          width: 1,
          style: 2,
          labelBackgroundColor: '#374151',
        },
      },
      rightPriceScale: {
        borderColor: '#374151',
      },
      timeScale: {
        borderColor: '#374151',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderUpColor: '#10b981',
      borderDownColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    candlestickSeriesRef.current = candlestickSeries;

    // Format data for lightweight-charts
    const candlestickData: CandlestickData[] = data.map((bar) => ({
      time: bar.timestamp.split('T')[0],
      open: bar.open,
      high: bar.high,
      low: bar.low,
      close: bar.close,
    }));

    candlestickSeries.setData(candlestickData);

    // Add volume series
    if (showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        color: '#6b7280',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
      });

      volumeSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });

      const volumeData: HistogramData[] = data.map((bar) => ({
        time: bar.timestamp.split('T')[0],
        value: bar.volume,
        color: bar.close >= bar.open ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
      }));

      volumeSeries.setData(volumeData);
      volumeSeriesRef.current = volumeSeries;
    }

    // Add SMA lines
    if (showSMA) {
      const smaColors = ['#f59e0b', '#3b82f6', '#8b5cf6'];
      smaperiods.forEach((period, index) => {
        const smaData = generateIndicatorSeries(data, period, 'sma');
        if (smaData.length > 0) {
          const smaSeries = chart.addLineSeries({
            color: smaColors[index % smaColors.length],
            lineWidth: 1,
            title: `SMA ${period}`,
          });
          smaSeries.setData(smaData as LineData[]);
        }
      });
    }

    // Add Bollinger Bands
    if (showBollingerBands) {
      const bbData = generateBollingerBandsSeries(data, 20, 2);
      if (bbData.upper.length > 0) {
        const upperSeries = chart.addLineSeries({
          color: 'rgba(156, 163, 175, 0.5)',
          lineWidth: 1,
          lineStyle: 2,
        });
        upperSeries.setData(bbData.upper as LineData[]);

        const lowerSeries = chart.addLineSeries({
          color: 'rgba(156, 163, 175, 0.5)',
          lineWidth: 1,
          lineStyle: 2,
        });
        lowerSeries.setData(bbData.lower as LineData[]);
      }
    }

    // Subscribe to crosshair move for legend - update DOM directly to avoid re-renders
    chart.subscribeCrosshairMove((param) => {
      if (!legendRef.current) return;

      if (param.time && param.seriesData.size > 0) {
        const candleData = param.seriesData.get(candlestickSeries);
        if (candleData && 'open' in candleData) {
          const bar = data.find((b) => b.timestamp.split('T')[0] === param.time);
          if (bar) {
            legendRef.current.style.display = 'block';
            legendRef.current.innerHTML = `
              <span class="text-gray-400">O: <span class="text-white">${bar.open.toFixed(2)}</span></span>
              <span class="text-gray-400">H: <span class="text-green-400">${bar.high.toFixed(2)}</span></span>
              <span class="text-gray-400">L: <span class="text-red-400">${bar.low.toFixed(2)}</span></span>
              <span class="text-gray-400">C: <span class="text-white">${bar.close.toFixed(2)}</span></span>
              <span class="text-gray-400">Vol: <span class="text-white">${(bar.volume / 1000000).toFixed(2)}M</span></span>
            `;
          }
        }
      }
    });

    // Fit content
    chart.timeScale().fitContent();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, height, showVolume, showSMA, showBollingerBands, smaperiods]);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-800 rounded-lg">
        <p className="text-gray-400">No price data available</p>
      </div>
    );
  }

  return (
    <div className="relative">
      <div
        ref={legendRef}
        className="absolute top-2 left-2 z-10 bg-gray-800/90 rounded px-3 py-2 text-sm flex gap-4"
        style={{ display: 'none' }}
      />
      <div ref={chartContainerRef} />
    </div>
  );
}

export default CandlestickChart;
