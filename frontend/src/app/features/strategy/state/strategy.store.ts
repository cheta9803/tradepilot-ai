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

import {
    PaperTradingService,
} from '../../paper-trading/services/paper-trading.service';

@Injectable({
    providedIn: 'root',
})
export class StrategyStore {

    private readonly service = inject(
        StrategyService,
    );

    private readonly paperTradingService = inject(
        PaperTradingService,
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

    readonly creatingPaperTrade = signal(
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

    createPaperTrade(): void {

        const strategy = this.strategy();

        if (!strategy) {

            return;

        }

        this.creatingPaperTrade.set(
            true,
        );

        this.paperTradingService
            .create({

                exchange: 'NSE',

                token: strategy.token,

                timeframe: strategy.timeframe,

            })
            .pipe(
                finalize(() => {

                    this.creatingPaperTrade.set(
                        false,
                    );

                }),
            )
            .subscribe({

                next: (
                    response: { message: string },
                ) => {

                    this.snackBar.open(
                        response.message,
                        'Close',
                        {
                            duration: 3000,
                        },
                    );

                },

                error: (
                    error: HttpErrorResponse,
                ) => {

                    this.snackBar.open(
                        error.error?.detail ??
                        'Unable to create paper trade.',
                        'Close',
                        {
                            duration: 3000,
                        },
                    );

                },

            });

    }

}