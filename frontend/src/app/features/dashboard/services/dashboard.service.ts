import {
    computed,
    DestroyRef,
    effect,
    inject,
    Injectable,
    signal,
} from '@angular/core';

import { MarketStore } from '../../../core/realtime/services/market.store';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';
import { DashboardApi } from '../api/dashboard-api';
import {
    AiOpportunity,
    DashboardSummary,
    MarketIndex,
    Order,
    Position,
    ScannerOpportunity,
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

    private readonly destroyRef = inject(
        DestroyRef,
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

    private readonly _scannerOpportunities =
        signal<ScannerOpportunity[]>([]);

    private readonly _aiOpportunities =
        signal<AiOpportunity[]>([]);

    readonly scannerOpportunities = computed(
        () => this._scannerOpportunities(),
    );

    readonly aiOpportunities = computed(
        () => this._aiOpportunities(),
    );

    constructor() {

        console.log(
            'DashboardService instance:',
            this.instanceId,
        );

        effect(() => {

            this.updateLivePrices();

        });

        // Refresh dashboard recommendations automatically during
        // the NSE trading session. The first load is still triggered
        // by the Dashboard component.
        interval(30_000)
            .pipe(
                takeUntilDestroyed(this.destroyRef),
            )
            .subscribe(() => {

                if (this.isTradingHours()) {
                    this.refreshRecommendations();
                }

            });

    }

    load(): void {

        this.loadDashboard();
        this.refreshRecommendations();

    }

    private loadDashboard(): void {

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
                        'Dashboard API failed:',
                        error,
                    );

                },

            });

    }

    private refreshRecommendations(): void {

        this.dashboardApi
            .getTopScanner(5)
            .subscribe({

                next: opportunities => {

                    this._scannerOpportunities.set(
                        opportunities,
                    );

                },

                error: error => {

                    console.error(
                        'Scanner API failed:',
                        error,
                    );

                },

            });

        this.dashboardApi
            .getTopAi(5)
            .subscribe({

                next: opportunities => {

                    this._aiOpportunities.set(
                        opportunities,
                    );

                },

                error: error => {

                    console.error(
                        'AI API failed:',
                        error,
                    );

                },

            });

    }

    private isTradingHours(): boolean {

        const now = new Date();
        const day = now.getDay();

        // NSE regular session: Monday-Friday, 09:15-15:30 IST.
        if (day === 0 || day === 6) {
            return false;
        }

        const minutes =
            now.getHours() * 60 +
            now.getMinutes();

        return minutes >= 9 * 60 + 15
            && minutes < 15 * 60 + 30;

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

        const portfolioValue = positions.reduce(

            (
                total,
                position,
            ) => total + (position.ltp * position.quantity),

            0,

        );

        this._summary.update(summary => ({

            ...summary,

            portfolioValue: Number(
                portfolioValue.toFixed(2),
            ),

        }));

    }

}