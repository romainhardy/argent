import { apiClient } from './client';
import {
  AnalysisResult,
  BacktestResult,
  CurrentPrice,
  HealthStatus,
  Portfolio,
  PortfolioPerformance,
  PriceHistory,
  RiskAnalysis,
  SentimentAnalysis,
  TechnicalAnalysis,
  Transaction,
  Recommendation,
} from './types';

// Health check
export const checkHealth = (): Promise<HealthStatus> => {
  return apiClient.get<HealthStatus>('/health');
};

// Price data
export const getPriceHistory = async (
  symbol: string,
  interval: string = '1d',
  period: string = '1y'
): Promise<PriceHistory> => {
  const response = await apiClient.get<{ symbol: string; data: PriceHistory['bars']; period: string }>(
    `/symbols/${symbol}/history`,
    { params: { interval, period } }
  );
  return {
    symbol: response.symbol,
    bars: response.data,
    interval,
  };
};

export const getCurrentPrice = async (symbol: string): Promise<CurrentPrice> => {
  const response = await apiClient.get<{
    symbol: string;
    price: number;
    change_pct: number;
    previous_close: number;
    volume: number;
  }>(`/symbols/${symbol}/price`);
  return {
    symbol: response.symbol,
    price: response.price,
    change: response.price - response.previous_close,
    changePercent: response.change_pct,
    volume: response.volume,
    timestamp: new Date().toISOString(),
  };
};

// Analysis
export interface StartAnalysisParams {
  symbols: string[];
  assetType: 'stock' | 'crypto';
  analysisTypes?: string[];
}

interface ApiAnalysisResult {
  id: string;
  status: string;
  symbols: string[];
  horizon?: string;
  created_at: string;
  completed_at?: string;
  current_phase?: string;
  progress?: unknown;
  results?: {
    technical_analysis?: {
      symbols?: Record<string, {
        current_price?: number;
        trend?: { direction?: string; strength?: number; ma_alignment?: string };
        momentum?: { rsi?: number; rsi_signal?: string; macd_trend?: string };
        volatility?: { bb_position?: number; bb_signal?: string; volatility_level?: string };
        levels?: { nearest_support?: number; nearest_resistance?: number };
        signals?: { overall?: string; confidence?: string; score?: number };
        interpretation?: string;
      }>;
      summary?: string;
    } | null;
    fundamental_analysis?: {
      symbols?: Record<string, {
        name?: string;
        sector?: string;
        valuation?: { pe_ratio?: number; peg_ratio?: number; price_to_book?: number; assessment?: string; score?: number };
        profitability?: { profit_margin?: number; roe?: number; assessment?: string; score?: number };
        growth?: { revenue_growth?: number; earnings_growth?: number; assessment?: string };
        financial_health?: { debt_to_equity?: number; current_ratio?: number; assessment?: string };
        overall_score?: number;
        fair_value_assessment?: string;
      }>;
      summary?: string;
    } | null;
    sentiment_analysis?: {
      symbols?: Record<string, {
        overall?: string;
        score?: number;
        news_count?: number;
        positive_count?: number;
        negative_count?: number;
        neutral_count?: number;
        recent_headlines?: Array<{
          title?: string;
          sentiment?: string;
          source?: string;
          date?: string;
        }>;
        interpretation?: string;
      }>;
      summary?: string;
    } | null;
    risk_analysis?: {
      symbols?: Record<string, {
        volatility?: { annualized?: number; annualized_pct?: number; level?: string };
        value_at_risk?: { daily_95?: number; daily_95_pct?: number; cvar?: number };
        max_drawdown?: { value?: number; value_pct?: number; level?: string };
        risk_adjusted_returns?: { sharpe_ratio?: number; sortino_ratio?: number };
        beta?: number | null;
        overall_risk?: { score?: number; level?: string };
      }>;
      correlation?: Record<string, Record<string, number>>;
      diversification?: string;
      summary?: string;
    } | null;
    macro_analysis?: {
      economic_cycle?: { phase?: string };
      market_conditions?: { risk_appetite?: string };
      inflation?: { trend?: string; current_rate?: number };
      growth?: { gdp_trend?: string };
      summary?: string;
    } | null;
    recommendations?: Array<{
      symbol: string;
      action: string;
      conviction: string;
      target_price?: number | null;
      stop_loss?: number | null;
      position_size_pct?: number;
      rationale?: string;
      risks?: string[];
    }>;
  } | null;
  error?: string | null;
}

function transformTechnicalAnalysis(
  apiTech: NonNullable<NonNullable<ApiAnalysisResult['results']>['technical_analysis']>
): Record<string, TechnicalAnalysis> {
  const result: Record<string, TechnicalAnalysis> = {};

  if (apiTech.symbols) {
    for (const [symbol, data] of Object.entries(apiTech.symbols)) {
      result[symbol] = {
        trend: (data.trend?.direction as 'bullish' | 'bearish' | 'neutral') || 'neutral',
        strength: data.trend?.strength || 0,
        indicators: {
          rsi: data.momentum?.rsi,
          bollingerBands: data.volatility?.bb_position !== undefined ? {
            upper: 0,
            middle: 0,
            lower: 0,
          } : undefined,
        },
        supportLevels: data.levels?.nearest_support ? [data.levels.nearest_support] : [],
        resistanceLevels: data.levels?.nearest_resistance ? [data.levels.nearest_resistance] : [],
        signals: [
          data.signals?.overall ? `Overall: ${data.signals.overall}` : '',
          data.momentum?.rsi_signal ? `RSI: ${data.momentum.rsi_signal}` : '',
          data.momentum?.macd_trend ? `MACD: ${data.momentum.macd_trend}` : '',
        ].filter(Boolean),
      };
    }
  }

  return result;
}

function transformSentimentAnalysis(
  apiSent: NonNullable<NonNullable<ApiAnalysisResult['results']>['sentiment_analysis']>
): Record<string, SentimentAnalysis> {
  const result: Record<string, SentimentAnalysis> = {};

  if (apiSent.symbols) {
    for (const [symbol, data] of Object.entries(apiSent.symbols)) {
      result[symbol] = {
        overall: (data.overall as 'bullish' | 'bearish' | 'neutral') || 'neutral',
        score: data.score || 0,
        newsCount: data.news_count || 0,
        positiveCount: data.positive_count || 0,
        negativeCount: data.negative_count || 0,
        recentHeadlines: (data.recent_headlines || []).map(h => ({
          title: h.title || '',
          sentiment: (h.sentiment as 'positive' | 'negative' | 'neutral') || 'neutral',
          source: h.source || 'Unknown',
          date: h.date || '',
        })),
      };
    }
  }

  return result;
}

function transformRiskAnalysis(
  apiRisk: NonNullable<NonNullable<ApiAnalysisResult['results']>['risk_analysis']>
): Record<string, RiskAnalysis> {
  const result: Record<string, RiskAnalysis> = {};

  if (apiRisk.symbols) {
    for (const [symbol, data] of Object.entries(apiRisk.symbols)) {
      result[symbol] = {
        volatility: data.volatility?.annualized || 0,
        beta: data.beta ?? undefined,
        sharpeRatio: data.risk_adjusted_returns?.sharpe_ratio,
        sortinoRatio: data.risk_adjusted_returns?.sortino_ratio,
        maxDrawdown: data.max_drawdown?.value || 0,
        valueAtRisk: data.value_at_risk?.daily_95 || 0,
        riskLevel: (data.overall_risk?.level as 'low' | 'medium' | 'high') || 'medium',
      };
    }
  }

  return result;
}

function transformRecommendations(
  apiRecs: NonNullable<NonNullable<ApiAnalysisResult['results']>['recommendations']>
): Recommendation[] {
  return apiRecs.map(rec => {
    // Map action strings to expected types
    let action: Recommendation['action'] = 'hold';
    const actionUpper = (rec.action || '').toUpperCase();
    if (actionUpper === 'BUY') {
      action = rec.conviction === 'HIGH' ? 'strong_buy' : 'buy';
    } else if (actionUpper === 'SELL') {
      action = rec.conviction === 'HIGH' ? 'strong_sell' : 'sell';
    } else {
      action = 'hold';
    }

    return {
      symbol: rec.symbol,
      action,
      confidence: rec.conviction === 'HIGH' ? 0.8 : rec.conviction === 'MEDIUM' ? 0.6 : 0.4,
      targetPrice: rec.target_price ?? undefined,
      stopLoss: rec.stop_loss ?? undefined,
      rationale: rec.rationale || 'No rationale provided',
      risks: rec.risks || [],
    };
  });
}

function transformAnalysisResult(api: ApiAnalysisResult): AnalysisResult {
  let results: AnalysisResult['results'] | undefined;

  if (api.results) {
    const technical = api.results.technical_analysis
      ? transformTechnicalAnalysis(api.results.technical_analysis)
      : {};

    const sentiment = api.results.sentiment_analysis
      ? transformSentimentAnalysis(api.results.sentiment_analysis)
      : {};

    const risk = api.results.risk_analysis
      ? transformRiskAnalysis(api.results.risk_analysis)
      : {};

    const recommendations = api.results.recommendations
      ? transformRecommendations(api.results.recommendations)
      : [];

    results = {
      technical,
      sentiment,
      risk,
      recommendations,
    };
  }

  return {
    id: api.id,
    status: api.status as AnalysisResult['status'],
    symbols: api.symbols,
    assetType: 'stock',
    createdAt: api.created_at,
    completedAt: api.completed_at,
    error: api.error || undefined,
    results,
  };
}

export const startAnalysis = async (params: StartAnalysisParams): Promise<AnalysisResult> => {
  const response = await apiClient.post<ApiAnalysisResult>('/analysis', {
    symbols: params.symbols,
    asset_type: params.assetType,
    analysis_types: params.analysisTypes,
  });
  return transformAnalysisResult(response);
};

export const getAnalysis = async (analysisId: string): Promise<AnalysisResult> => {
  const response = await apiClient.get<ApiAnalysisResult>(`/analysis/${analysisId}`);
  return transformAnalysisResult(response);
};

export const listAnalyses = async (limit: number = 10): Promise<AnalysisResult[]> => {
  const response = await apiClient.get<{ analyses: ApiAnalysisResult[]; total: number }>('/analysis', {
    params: { limit },
  });
  return response.analyses.map(transformAnalysisResult);
};

export const getAnalysisStreamUrl = (analysisId: string): string => {
  return `${apiClient.getBaseUrl()}/analysis/${analysisId}/stream`;
};

// Portfolio
export const getPortfolio = (portfolioId: string): Promise<Portfolio> => {
  return apiClient.get<Portfolio>(`/portfolio/${portfolioId}`);
};

export const listPortfolios = (): Promise<Portfolio[]> => {
  return apiClient.get<Portfolio[]>('/portfolio');
};

export const getPortfolioPerformance = (
  portfolioId: string,
  period: string = '1y'
): Promise<PortfolioPerformance[]> => {
  return apiClient.get<PortfolioPerformance[]>(`/portfolio/${portfolioId}/performance`, {
    params: { period },
  });
};

export const getTransactions = (
  portfolioId: string,
  limit: number = 50
): Promise<Transaction[]> => {
  return apiClient.get<Transaction[]>(`/portfolio/${portfolioId}/transactions`, {
    params: { limit },
  });
};

// Backtest
export interface RunBacktestParams {
  symbol: string;
  strategy: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  params?: Record<string, unknown>;
}

export const runBacktest = (params: RunBacktestParams): Promise<BacktestResult> => {
  return apiClient.post<BacktestResult>('/backtest', params);
};

export const getBacktest = (backtestId: string): Promise<BacktestResult> => {
  return apiClient.get<BacktestResult>(`/backtest/${backtestId}`);
};

export const listBacktests = (limit: number = 10): Promise<BacktestResult[]> => {
  return apiClient.get<BacktestResult[]>('/backtest', {
    params: { limit },
  });
};

export const compareStrategies = (backtestIds: string[]): Promise<BacktestResult[]> => {
  return apiClient.get<BacktestResult[]>('/backtest/compare', {
    params: { ids: backtestIds.join(',') },
  });
};
