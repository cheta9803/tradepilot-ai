import {
    Injectable,
    inject,
    signal,
} from '@angular/core';

import {
    HttpErrorResponse,
} from '@angular/common/http';

import {
    finalize,
} from 'rxjs';

import {
    MatSnackBar,
} from '@angular/material/snack-bar';

import {
    StrategyResponse,
} from '../models/strategy.model';

import {
    StrategyService,
} from '../services/strategy.service';

@Injectable({
    providedIn: 'root',
})
export class StrategyStore {

    private readonly service = inject(
        StrategyService,
    );

    private readonly snackBar = inject(
        MatSnackBar,
    );

    readonly strategy = signal<
        StrategyResponse | null
    >(null);

    readonly loading = signal(
        false,
    );

    load(
        symbol: string,
        timeframe = '1m',
    ): void {

        this.loading.set(
            true,
        );

        this.service
            .analyze(
                symbol,
                timeframe,
            )
            .pipe(
                finalize(() => {

                    this.loading.set(
                        false,
                    );

                }),
            )
            .subscribe({

                next: (
                    response: StrategyResponse,
                ) => {

                    this.strategy.set(
                        response,
                    );

                },

                error: (
                    error: HttpErrorResponse,
                ) => {

                    this.strategy.set(
                        null,
                    );

                    this.snackBar.open(
                        error.error?.detail ??
                        'Unable to load strategy.',
                        'Close',
                        {
                            duration: 3000,
                        },
                    );

                },

            });

    }

}