import { Injectable, signal } from '@angular/core';
import {
    DashboardSummary,
    MarketIndex,
    Order,
    Position,
} from '../models/dashboard.model';

@Injectable({
    providedIn: 'root',
})
export class DashboardService {
    readonly summary = signal<DashboardSummary>({
        portfolioValue: 152340,
        todayPnL: 2450,
        availableMargin: 82000,
        openPositions: 3,
    });

    readonly indices = signal([
        {
            name: 'NIFTY 50',
            value: 25186.40,
            change: 118.35,
            changePercent: 0.47,
        },
        {
            name: 'BANK NIFTY',
            value: 56632.15,
            change: -62.40,
            changePercent: -0.11,
        },
        {
            name: 'FINNIFTY',
            value: 27492.20,
            change: 58.75,
            changePercent: 0.21,
        },
    ]);

    readonly positions = signal([
        {
            symbol: 'RELIANCE',
            quantity: 20,
            averagePrice: 2700,
            ltp: 2725,
            pnl: 500,
        },
        {
            symbol: 'TCS',
            quantity: 15,
            averagePrice: 3650,
            ltp: 3605,
            pnl: -675,
        },
        {
            symbol: 'INFY',
            quantity: 30,
            averagePrice: 1580,
            ltp: 1608,
            pnl: 840,
        },
    ]);

    readonly orders = signal([
        {
            symbol: 'RELIANCE',
            type: 'BUY',
            quantity: 20,
            status: 'Completed',
        },
        {
            symbol: 'TCS',
            type: 'SELL',
            quantity: 10,
            status: 'Pending',
        },
        {
            symbol: 'INFY',
            type: 'BUY',
            quantity: 15,
            status: 'Completed',
        },
    ]);
}