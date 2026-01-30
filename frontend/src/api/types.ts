// Price data types
export interface PriceBar {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PriceHistory {
  symbol: string;
  bars: PriceBar[];
  interval: string;
}

export interface CurrentPrice {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  timestamp: string;
}

// Technical indicators
export interface TechnicalIndicators {
  sma20?: number;
  sma50?: number;
  sma200?: number;
  ema12?: number;
  ema26?: number;
  rsi?: number;
  macd?: {
    macd: number;
    signal: number;
    histogram: number;
  };
  bollingerBands?: {
    upper: number;
    middle: number;
    lower: number;
  };
  atr?: number;
}

// Analysis types
export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed';
export type AnalysisPhase =
  | 'initializing'
  | 'data_collection'
  | 'technical_analysis'
  | 'fundamental_analysis'
  | 'sentiment_analysis'
  | 'risk_analysis'
  | 'macro_analysis'
  | 'generating_report'
  | 'completed';

export interface AnalysisProgress {
  phase: AnalysisPhase;
  progress: number;
  message?: string;
}

export interface TechnicalAnalysis {
  trend: 'bullish' | 'bearish' | 'neutral';
  strength: number;
  indicators: TechnicalIndicators;
  supportLevels: number[];
  resistanceLevels: number[];
  signals: string[];
}

export interface FundamentalAnalysis {
  peRatio?: number;
  pegRatio?: number;
  pbRatio?: number;
  debtToEquity?: number;
  currentRatio?: number;
  roe?: number;
  revenueGrowth?: number;
  earningsGrowth?: number;
  profitMargin?: number;
  score: number;
  summary: string;
}

export interface SentimentAnalysis {
  overall: 'bullish' | 'bearish' | 'neutral';
  score: number;
  newsCount: number;
  positiveCount: number;
  negativeCount: number;
  recentHeadlines: Array<{
    title: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    source: string;
    date: string;
  }>;
}

export interface RiskAnalysis {
  volatility: number;
  beta?: number;
  sharpeRatio?: number;
  sortinoRatio?: number;
  maxDrawdown: number;
  valueAtRisk: number;
  riskLevel: 'low' | 'medium' | 'high';
}

export interface MacroAnalysis {
  interestRateEnvironment: 'rising' | 'falling' | 'stable';
  inflationOutlook: 'high' | 'moderate' | 'low';
  economicGrowth: 'expanding' | 'contracting' | 'stable';
  marketConditions: 'risk-on' | 'risk-off' | 'neutral';
  summary: string;
}

export interface Recommendation {
  symbol: string;
  action: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell';
  confidence: number;
  targetPrice?: number;
  stopLoss?: number;
  rationale: string;
  risks: string[];
}

export interface AnalysisResult {
  id: string;
  status: AnalysisStatus;
  symbols: string[];
  assetType: 'stock' | 'crypto';
  createdAt: string;
  completedAt?: string;
  error?: string;
  results?: {
    technical: Record<string, TechnicalAnalysis>;
    fundamental?: Record<string, FundamentalAnalysis>;
    sentiment: Record<string, SentimentAnalysis>;
    risk: Record<string, RiskAnalysis>;
    macro?: MacroAnalysis;
    recommendations: Recommendation[];
  };
}

// SSE event types
export interface SSEEvent {
  type: 'progress' | 'partial_result' | 'complete' | 'error';
  data: AnalysisProgress | Partial<AnalysisResult> | { message: string };
}

// Portfolio types
export interface Position {
  id: string;
  symbol: string;
  quantity: number;
  avgCost: number;
  currentPrice: number;
  marketValue: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  allocation: number;
}

export interface Transaction {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  total: number;
  date: string;
  fees?: number;
}

export interface Portfolio {
  id: string;
  name: string;
  totalValue: number;
  cashBalance: number;
  positions: Position[];
  dayChange: number;
  dayChangePercent: number;
  totalReturn: number;
  totalReturnPercent: number;
}

export interface PortfolioPerformance {
  date: string;
  value: number;
  benchmark?: number;
}

// Backtest types
export interface Trade {
  id: string;
  symbol: string;
  entryDate: string;
  entryPrice: number;
  exitDate?: string;
  exitPrice?: number;
  quantity: number;
  side: 'long' | 'short';
  pnl?: number;
  pnlPercent?: number;
  status: 'open' | 'closed';
}

export interface BacktestMetrics {
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  sortinoRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitFactor: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  avgWin: number;
  avgLoss: number;
  avgHoldingPeriod: number;
}

export interface EquityPoint {
  date: string;
  equity: number;
  benchmark?: number;
  drawdown?: number;
}

export interface BacktestResult {
  id: string;
  strategyName: string;
  symbol: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  finalValue: number;
  metrics: BacktestMetrics;
  equityCurve: EquityPoint[];
  trades: Trade[];
  status: 'pending' | 'running' | 'completed' | 'failed';
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  uptime: number;
}
