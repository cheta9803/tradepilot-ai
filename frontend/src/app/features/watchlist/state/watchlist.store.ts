import {
    Injectable,
    computed,
    inject,
    signal,
    effect,
} from '@angular/core';

import {
    finalize,
} from 'rxjs';

import {
    MatSnackBar,
} from '@angular/material/snack-bar';

import {
    WatchlistLive,
} from '../models/watchlist.model';

import {
    CreateWatchlistRequest,
} from '../models/watchlist-request.model';

import {
    WatchlistService,
} from '../services/watchlist.service';

import {
    WebSocketService,
} from '../../../core/realtime/services/websocket.service';

@Injectable({
    providedIn: 'root',
})
export class WatchlistStore {

    private readonly service = inject(
        WatchlistService,
    );

    private readonly websocket = inject(
        WebSocketService,
    );

    private readonly snackBar = inject(
        MatSnackBar,
    );

    private readonly watchlistSignal = signal<WatchlistLive[]>([]);

    readonly watchlist = computed(
        () => this.watchlistSignal(),
    );

    readonly loading = signal(false);

    readonly adding = signal(false);

    readonly deletingId = signal<number | null>(null);

    constructor() {

        effect(() => {

            const tick = this.websocket.lastTick();

            if (!tick) {

                return;

            }

            this.watchlistSignal.update(
                items =>
                    items.map(item => {

                        if (item.token !== tick.token) {

                            return item;

                        }

                        const change =
                            tick.ltp - tick.close;

                        const changePercent =
                            tick.close === 0
                                ? 0
                                : (change / tick.close) * 100;

                        return {

                            ...item,

                            ltp: tick.ltp,

                            open: tick.open,

                            high: tick.high,

                            low: tick.low,

                            close: tick.close,

                            volume: tick.volume,

                            timestamp: tick.timestamp,

                            change,

                            change_percent: changePercent,

                        };

                    }),
            );

        });

    }

    load(): void {

        this.loading.set(true);

        this.service
            .getLiveWatchlist()
            .pipe(
                finalize(() =>
                    this.loading.set(false),
                ),
            )
            .subscribe({

                next: response => {

                    this.watchlistSignal.set(
                        response,
                    );

                },

            });

    }

    add(
        request: CreateWatchlistRequest,
    ): void {

        this.adding.set(true);

        this.service
            .create(request)
            .pipe(
                finalize(() =>
                    this.adding.set(false),
                ),
            )
            .subscribe({

                next: () => {

                    this.snackBar.open(
                        'Symbol added successfully.',
                        'Close',
                        {
                            duration: 2500,
                        },
                    );

                    this.load();

                },

                error: error => {

                    this.snackBar.open(
                        error.error?.detail ??
                        'Unable to add symbol.',
                        'Close',
                        {
                            duration: 3500,
                        },
                    );

                },

            });

    }

    remove(
        id: number,
    ): void {

        this.deletingId.set(id);

        this.service
            .delete(id)
            .pipe(
                finalize(() =>
                    this.deletingId.set(null),
                ),
            )
            .subscribe({

                next: () => {

                    this.snackBar.open(
                        'Symbol removed.',
                        'Close',
                        {
                            duration: 2500,
                        },
                    );

                    this.load();

                },

                error: () => {

                    this.snackBar.open(
                        'Unable to delete symbol.',
                        'Close',
                        {
                            duration: 3500,
                        },
                    );

                },

            });

    }

}