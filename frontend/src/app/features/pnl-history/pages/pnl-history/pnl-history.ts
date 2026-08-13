import {
    ChangeDetectionStrategy,
    Component,
    DestroyRef,
    OnInit,
    inject,
    signal,
} from '@angular/core';

import {
    DecimalPipe,
    DatePipe,
    NgClass,
} from '@angular/common';

import {
    MatButtonModule,
} from '@angular/material/button';

import {
    MatIconModule,
} from '@angular/material/icon';

import {
    MatProgressSpinnerModule,
} from '@angular/material/progress-spinner';

import {
    interval,
} from 'rxjs';

import {
    takeUntilDestroyed,
} from '@angular/core/rxjs-interop';

import {
    PageHeader,
} from '../../../../shared/ui/page-header/page-header';

import {
    SectionCard,
} from '../../../../shared/ui/section-card/section-card';

import {
    DailyPnl,
    DailyPnlTrade,
} from '../../models/pnl-history.model';

import {
    PnlHistoryService,
} from '../../services/pnl-history.service';


@Component({
    selector: 'app-pnl-history',
    standalone: true,
    imports: [
        DecimalPipe,
        DatePipe,
        NgClass,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        PageHeader,
        SectionCard,
    ],
    templateUrl: './pnl-history.html',
    styleUrl: './pnl-history.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PnlHistory implements OnInit {

    private readonly service =
        inject(PnlHistoryService);

    private readonly destroyRef =
        inject(DestroyRef);

    readonly history =
        signal<DailyPnl[]>([]);

    readonly selectedDate =
        signal<string | null>(null);

    readonly dayTrades =
        signal<DailyPnlTrade[]>([]);

    readonly loading =
        signal(false);

    readonly detailsLoading =
        signal(false);


    ngOnInit(): void {

        /*
         * Load immediately when the page opens.
         */
        this.refresh();

        /*
         * Automatically refresh P&L history.
         *
         * This keeps today's:
         * - trade count
         * - winning trades
         * - losing trades
         * - gross profit
         * - gross loss
         * - net P&L
         *
         * up to date without browser refresh.
         */
        interval(5_000)
            .pipe(
                takeUntilDestroyed(
                    this.destroyRef,
                ),
            )
            .subscribe(() => {

                this.refresh();

                /*
                 * If the user currently has a day
                 * selected, refresh its trade details too.
                 */
                const date =
                    this.selectedDate();

                if (date) {

                    this.refreshDayTrades(
                        date,
                        false,
                    );

                }

            });

    }


    refresh(): void {

        /*
         * Don't show the full-page spinner for
         * every 5-second background refresh.
         *
         * Only show it when there is no data yet.
         */
        if (this.history().length === 0) {

            this.loading.set(true);

        }

        this.service
            .getDailyPnl()
            .subscribe({

                next: data => {

                    this.history.set(data);

                    this.loading.set(false);

                },

                error: error => {

                    console.error(
                        'P&L history API failed:',
                        error,
                    );

                    /*
                     * Don't destroy existing data just
                     * because one background request failed.
                     */
                    this.loading.set(false);

                },

            });

    }


    selectDay(
        date: string,
    ): void {

        this.selectedDate.set(date);

        this.dayTrades.set([]);

        this.refreshDayTrades(
            date,
            true,
        );

    }


    private refreshDayTrades(
        date: string,
        showLoading: boolean,
    ): void {

        if (showLoading) {

            this.detailsLoading.set(true);

        }

        this.service
            .getDayTrades(date)
            .subscribe({

                next: data => {

                    /*
                     * Ignore the response if the user has
                     * already selected another day.
                     */
                    if (
                        this.selectedDate() === date
                    ) {

                        this.dayTrades.set(data);

                    }

                    this.detailsLoading.set(false);

                },

                error: error => {

                    console.error(
                        'P&L day trades API failed:',
                        error,
                    );

                    /*
                     * During background refresh we keep
                     * the existing trade details visible.
                     */
                    if (showLoading) {

                        this.dayTrades.set([]);

                    }

                    this.detailsLoading.set(false);

                },

            });

    }


    closeDetails(): void {

        this.selectedDate.set(null);

        this.dayTrades.set([]);

    }




    grossLossClass(): string {

        return 'loss';
    }

    reasonLabel(
        reason: string | null,
    ): string {

        if (!reason) {
            return '—';
        }

        const labels: Record<string, string> = {
            TARGET: 'TARGET',
            STOPLOSS: 'STOP LOSS',
            TRAILING_STOP: 'TRAILING STOP',
            BREAKEVEN_STOP: 'BREAKEVEN STOP',
            EOD: 'END OF DAY',
            BROKER_EXIT_ORDER_FAILED:
                'EXIT ORDER FAILED',
        };

        return labels[reason] ?? reason.replaceAll(
            '_',
            ' ',
        );
    }

    pnlClass(
        value: number,
    ): string {

        if (value > 0) {

            return 'profit';

        }

        if (value < 0) {

            return 'loss';

        }

        return 'neutral';

    }

}
