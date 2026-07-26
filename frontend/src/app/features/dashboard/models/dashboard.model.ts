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