export interface DashboardSummary {
  portfolioValue: number;
  todayPnL: number;
  availableMargin: number;
  openPositions: number;
}

export interface MarketIndex {
  name: string;
  value: number;
  change: number;
  changePercent: number;
}

export interface Position {
  symbol: string;
  quantity: number;
  averagePrice: number;
  ltp: number;
  pnl: number;
}

export interface Order {
  symbol: string;
  type: 'BUY' | 'SELL';
  quantity: number;
  status: string;
}

/**
 * Scanner result returned by /scanner/top.
 *
 * Keep optional fields here because the backend contract is still
 * evolving and we don't want the UI to break when a field is absent.
 */
export interface ScannerOpportunity {
  exchange?: string;
  symbol: string;
  token?: string | number;

  score?: number;
  confidence?: number;

  recommendation?: string;
  signal?: string;

  reasons?: string[];

  indicators?: Record<string, unknown>;
  timeframes?: Record<string, unknown>;

  updated_at?: string;
  market_status?: string;
  data_status?: string;
  data_age_seconds?: number;

  recommendations_available?: boolean;

  trade_ready?: boolean;
  direction?: string;

  entry?: number;
  stop_loss?: number;
  target?: number;
  risk_reward?: number;
}

/**
 * AI result returned by /ai/top.
 *
 * We intentionally keep the nested AI-specific structures flexible
 * until the backend response contract is finalized.
 */
export interface AiOpportunity {
  exchange?: string;
  symbol: string;
  token?: string | number;

  score?: number;
  confidence?: number;

  recommendation?: string;
  signal?: string;

  reasons?: string[];

  indicators?: Record<string, unknown>;
  strategy?: Record<string, unknown>;
  patterns?: Record<string, unknown>;

  timeframes?: Record<string, string>;
  timeframe_confidences?: Record<string, number>;
  trade_ready?: boolean;
  direction?: string;

  updated_at?: string;
  market_status?: string;
  data_status?: string;
  data_age_seconds?: number;

  recommendations_available?: boolean;

  entry?: number;
  stop_loss?: number;
  target?: number;
  risk_reward?: number;
}