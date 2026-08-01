import {
    computed,
    effect,
    inject,
    Injectable,
    signal,
} from '@angular/core';

import { MarketStore } from '../../../core/realtime/services/market.store';
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
    private static nextId = 1;

    private readonly instanceId = DashboardService.nextId++;

    private readonly dashboardApi = inject(
        DashboardApi,
    );

    private readonly marketStore = inject(
        MarketStore,
    );

    private readonly _summary = signal<DashboardSummary>({
        portfolioValue: 0,
        todayPnL: 0,
        availableMargin: 0,
        openPositions: 0,
    });

    private readonly _indices = signal<MarketIndex[]>([]);

    private readonly _positions = signal<Position[]>([]);

    private readonly _orders = signal<Order[]>([]);

    readonly summary = computed(
        () => this._summary(),
    );

    readonly indices = computed(
        () => this._indices(),
    );

    readonly positions = computed(
        () => this._positions(),
    );

    readonly orders = computed(
        () => this._orders(),
    );

    constructor() {

        console.log(
            'DashboardService instance:',
            this.instanceId,
        );

        effect(() => {

            this.updateLivePrices();

        });

    }

    load(): void {

        this.dashboardApi
            .getDashboard()
            .subscribe({

                next: response => {

                    this._summary.set(
                        response.summary,
                    );

                    this._indices.set(
                        response.indices,
                    );

                    this._positions.set(
                        response.positions,
                    );

                    this._orders.set(
                        response.orders,
                    );

                },

                error: error => {

                    console.error(
                        error,
                    );

                },

            });

    }

    private updateLivePrices(): void {

        this._indices.update(indices =>

            indices.map(index => {

                const tick = this.marketStore.getTick(
                    index.name,
                );

                if (!tick) {
                    return index;
                }

                return {
                    ...index,
                    value: tick.ltp,
                };

            }),

        );

        this._positions.update(positions =>

            positions.map(position => {

                const tick = this.marketStore.getTick(position.symbol);

                if (!tick) {
                    return position;
                }

                const pnl =
                    (tick.ltp - position.averagePrice) *
                    position.quantity;

                const updated = {
                    ...position,
                    ltp: tick.ltp,
                    pnl: Number(pnl.toFixed(2)),
                };

                return updated;
            }),
        );

        console.log(
            'Positions Signal:',
            this._positions(),
        );

        const positions = this._positions();

        const todayPnL = positions.reduce(

            (
                total,
                position,
            ) => total + position.pnl,

            0,

        );

        const portfolioValue = positions.reduce(

            (
                total,
                position,
            ) => total + (position.ltp * position.quantity),

            0,

        );

        this._summary.update(summary => ({

            ...summary,

            todayPnL: Number(
                todayPnL.toFixed(2),
            ),

            portfolioValue: Number(
                portfolioValue.toFixed(2),
            ),

        }));

    }

}