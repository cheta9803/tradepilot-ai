export interface Instrument {

    id: number;

    exchange: string;

    symbol: string;

    trading_symbol: string;

    token: string;

    instrument_type: string;

    lot_size: number;

    tick_size: number;

}