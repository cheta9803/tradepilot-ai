import {
    Injectable,
    inject,
    signal,
} from '@angular/core';

import {
    finalize,
} from 'rxjs';

import {
    Trade,
} from '../models/trade.model';

import {
    TradesService,
} from '../services/trades.service';

@Injectable({
    providedIn: 'root',
})
export class TradesStore {

    private readonly service = inject(
        TradesService,
    );

    readonly trades = signal<Trade[]>([]);

    readonly loading = signal(
        false,
    );

    load(): void {

        this.loading.set(
            true,
        );

        this.service
            .getAll()
            .pipe(
                finalize(() => {

                    this.loading.set(
                        false,
                    );

                }),
            )
            .subscribe({

                next: trades => {

                    this.trades.set(
                        trades,
                    );

                },

            });

    }

}