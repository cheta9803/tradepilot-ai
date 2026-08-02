export interface StrategyResponse {

    exchange: string;

    token: string;

    symbol: string;

    timeframe: string;

    trend: string;

    signal: string;

    confidence: number;

    tradable: boolean;

    entry: number;

    stop_loss: number;

    target: number;

    risk_reward: number;

    ema20: number;

    ema50: number;

    rsi14: number;

    atr14: number;

    vwap: number | null;

    macd: number;

    signal_line: number;

    reasons: string[];

}