import { useEffect, useRef } from 'react';
import {
  createChart,
  IChartApi,
  ColorType,
  CrosshairMode,
  LineData,
  HistogramData,
} from 'lightweight-charts';
import { PriceBar } from '../../api/types';
import { generateRSISeries, generateMACDSeries } from '../../hooks/usePriceHistory';

interface IndicatorPanelProps {
  data: PriceBar[];
  type: 'rsi' | 'macd';
  height?: number;
}

export function IndicatorPanel({ data, type, height = 150 }: IndicatorPanelProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

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

    if (type === 'rsi') {
      // RSI chart
      const rsiSeries = chart.addLineSeries({
        color: '#8b5cf6',
        lineWidth: 2,
        title: 'RSI (14)',
      });

      const rsiData = generateRSISeries(data, 14);
      rsiSeries.setData(rsiData as LineData[]);

      // Add overbought/oversold lines
      const overboughtLine = chart.addLineSeries({
        color: 'rgba(239, 68, 68, 0.5)',
        lineWidth: 1,
        lineStyle: 2,
      });
      const oversoldLine = chart.addLineSeries({
        color: 'rgba(16, 185, 129, 0.5)',
        lineWidth: 1,
        lineStyle: 2,
      });

      if (rsiData.length > 0) {
        const times = rsiData.map((d) => d.time);
        overboughtLine.setData(times.map((t) => ({ time: t, value: 70 })) as LineData[]);
        oversoldLine.setData(times.map((t) => ({ time: t, value: 30 })) as LineData[]);
      }

      // Set price scale for RSI (0-100)
      chart.priceScale('right').applyOptions({
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      });
    } else if (type === 'macd') {
      // MACD chart
      const { macdLine, signalLine, histogram } = generateMACDSeries(data);

      // MACD histogram
      const histogramSeries = chart.addHistogramSeries({
        priceFormat: {
          type: 'price',
          precision: 2,
        },
        priceScaleId: 'macd',
      });
      histogramSeries.setData(histogram as HistogramData[]);

      // MACD line
      const macdLineSeries = chart.addLineSeries({
        color: '#3b82f6',
        lineWidth: 2,
        title: 'MACD',
        priceScaleId: 'macd',
      });
      macdLineSeries.setData(macdLine as LineData[]);

      // Signal line
      const signalLineSeries = chart.addLineSeries({
        color: '#f59e0b',
        lineWidth: 2,
        title: 'Signal',
        priceScaleId: 'macd',
      });
      signalLineSeries.setData(signalLine as LineData[]);

      // Zero line
      if (macdLine.length > 0) {
        const zeroLine = chart.addLineSeries({
          color: 'rgba(156, 163, 175, 0.5)',
          lineWidth: 1,
          lineStyle: 2,
          priceScaleId: 'macd',
        });
        const times = macdLine.map((d) => d.time);
        zeroLine.setData(times.map((t) => ({ time: t, value: 0 })) as LineData[]);
      }
    }

    chart.timeScale().fitContent();

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
  }, [data, type, height]);

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 bg-gray-800 rounded-lg">
        <p className="text-gray-400">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden">
      <div className="px-3 py-2 border-b border-gray-700">
        <span className="text-sm font-medium text-gray-300">
          {type === 'rsi' ? 'RSI (14)' : 'MACD (12, 26, 9)'}
        </span>
      </div>
      <div ref={chartContainerRef} />
    </div>
  );
}

export default IndicatorPanel;
