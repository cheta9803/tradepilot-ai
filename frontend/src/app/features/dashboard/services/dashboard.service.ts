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

  readonly indices = signal<MarketIndex[]>([
    {
      name: 'NIFTY 50',
      value: 25342.8,
      change: 118,
      changePercent: 0.47,
    },
    {
      name: 'BANK NIFTY',
      value: 56218,
      change: -86,
      changePercent: -0.15,
    },
  ]);

  readonly positions = signal<Position[]>([
    {
      symbol: 'RELIANCE',
      quantity: 10,
      averagePrice: 2978,
      ltp: 3012,
      pnl: 340,
    },
    {
      symbol: 'INFY',
      quantity: 20,
      averagePrice: 1652,
      ltp: 1674,
      pnl: 440,
    },
  ]);

  readonly orders = signal<Order[]>([
    {
      symbol: 'TCS',
      quantity: 5,
      type: 'BUY',
      status: 'Completed',
    },
  ]);
}