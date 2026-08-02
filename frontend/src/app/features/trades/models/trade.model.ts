export interface Trade {

    exchange: string;

    token: string;

    symbol: string;

    timeframe: string;

    state: string;

    signal: string;

    execution_mode: string;

    entry_price: number;

    current_price: number;

    exit_price: number | null;

    stop_loss: number;

    target: number;

    quantity: number;

    pnl: number;

    reason: string | null;

    order_id: string | null;

    order_status: string | null;

    broker: string | null;

    highest_price: number;

    lowest_price: number;

    trail_started: boolean;

    breakeven_done: boolean;

    opened_at: string | null;

    closed_at: string | null;

    updated_at: string;

}