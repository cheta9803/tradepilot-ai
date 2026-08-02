import {
    Injectable,
    inject,
    signal,
} from '@angular/core';

import {
    finalize,
} from 'rxjs';

import {
    Instrument,
} from '../models/instrument.model';

import {
    Candle,
} from '../models/candle.model';

import {
    MarketService,
} from '../services/market.service';

import {
    MarketStore,
} from '../../../core/market/state/market.store';


@Injectable({
    providedIn: 'root',
})
export class MarketPageStore {

    private readonly marketService = inject(
        MarketService,
    );

    readonly realtime = inject(
        MarketStore,
    );

    readonly loading = signal(
        false,
    );

    readonly instruments = signal<
        Instrument[]
    >([]);

    readonly selectedInstrument =
        signal<
            Instrument | null
        >(null);

    readonly candles = signal<
        Candle[]
    >([]);

    readonly ltp = signal<
        number | null
    >(null);

    search(
        query: string,
    ): void {

        if (
            query.trim().length < 2
        ) {

            this.instruments.set([]);

            return;

        }

        this.marketService
            .search(query)
            .subscribe({

                next: (
                    instruments,
                ) => {

                    this.instruments.set(
                        instruments,
                    );

                },

            });

    }

    select(
        instrument: Instrument,
    ): void {

        this.selectedInstrument.set(
            instrument,
        );

        this.loadHistory();

        this.loadLtp();

    }

    loadHistory(): void {

        const instrument =
            this.selectedInstrument();

        if (!instrument) {

            return;

        }

        this.loading.set(
            true,
        );

        this.marketService
            .history(
                instrument.symbol,
            )
            .pipe(

                finalize(
                    () => {

                        this.loading.set(
                            false,
                        );

                    },
                ),

            )
            .subscribe({

                next: (
                    candles,
                ) => {

                    this.candles.set(
                        candles,
                    );

                },

            });

    }

    loadLtp(): void {

        const instrument =
            this.selectedInstrument();

        if (!instrument) {

            return;

        }

        this.marketService
            .ltp(
                instrument.exchange,
                instrument.symbol,
                instrument.token,
            )
            .subscribe({

                next: (
                    response,
                ) => {

                    this.ltp.set(
                        response.ltp,
                    );

                },

            });

    }

    livePrice(): number | null {

        const instrument =
            this.selectedInstrument();

        if (!instrument) {

            return null;

        }

        const tick =
            this.realtime.getByToken(
                instrument.token,
            );

        return (
            tick?.ltp ??
            this.ltp()
        );

    }

}