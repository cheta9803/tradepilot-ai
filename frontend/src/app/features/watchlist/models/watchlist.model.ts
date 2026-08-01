export interface Watchlist {

  id: number;

  exchange: string;

  symbol: string;

  created_at: string;

}

export interface WatchlistLive {

  id: number;

  exchange: string;

  symbol: string;

  token: string;

  trading_symbol: string;

  ltp: number | null;

  change: number | null;

  change_percent: number | null;

  open: number | null;

  high: number | null;

  low: number | null;

  close: number | null;

  volume: number | null;

  timestamp: string | null;

}