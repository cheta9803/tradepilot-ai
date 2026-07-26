import { computed, inject, Injectable, signal } from '@angular/core';

import { DashboardApi } from '../api/dashboard-api';
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

  private readonly dashboardApi = inject(DashboardApi);

  private readonly _summary = signal<DashboardSummary>({
    portfolioValue: 0,
    todayPnL: 0,
    availableMargin: 0,
    openPositions: 0,
  });

  private readonly _indices = signal<MarketIndex[]>([]);
  private readonly _positions = signal<Position[]>([]);
  private readonly _orders = signal<Order[]>([]);

  readonly summary = computed(() => this._summary());
  readonly indices = computed(() => this._indices());
  readonly positions = computed(() => this._positions());
  readonly orders = computed(() => this._orders());

  load(): void {
    this.dashboardApi.getDashboard().subscribe({
      next: (response) => {
        this._summary.set(response.summary);
        this._indices.set(response.indices);
        this._positions.set(response.positions);
        this._orders.set(response.orders);
      },
      error: (error) => {
        console.error(error);
      },
    });
  }

}