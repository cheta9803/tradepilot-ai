export interface DailyPnl {
    date: string;
    tradeCount: number;
    winningTrades: number;
    losingTrades: number;
    grossProfit: number;
    grossLoss: number;
    netPnl: number;
}

export interface DailyPnlTrade {
    time: string;
    symbol: string;
    side: string;
    quantity: number;
    entryPrice: number;
    exitPrice: number;
    pnl: number;
    reason: string | null;
}