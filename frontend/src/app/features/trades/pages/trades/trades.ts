import {
    ChangeDetectionStrategy,
    Component,
    OnInit,
    computed,
    inject,
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
    MatCardModule,
} from '@angular/material/card';

import {
    MatChipsModule,
} from '@angular/material/chips';

import {
    MatIconModule,
} from '@angular/material/icon';

import {
    MatProgressSpinnerModule,
} from '@angular/material/progress-spinner';

import {
    PageHeader,
} from '../../../../shared/ui/page-header/page-header';

import {
    SectionCard,
} from '../../../../shared/ui/section-card/section-card';

import {
    TradesStore,
} from '../../state/trades.store';

import {
    Trade,
} from '../../models/trade.model';

@Component({
    selector: 'app-trades',
    standalone: true,
    imports: [
        DecimalPipe,
        DatePipe,
        NgClass,
        MatButtonModule,
        MatCardModule,
        MatChipsModule,
        MatIconModule,
        MatProgressSpinnerModule,
        PageHeader,
        SectionCard,
    ],
    templateUrl: './trades.html',
    styleUrl: './trades.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Trades implements OnInit {

    readonly store = inject(
        TradesStore,
    );

    readonly trades =
        this.store.trades;

    readonly loading =
        this.store.loading;

    readonly totalTrades = computed(
        () => this.trades().length,
    );

    readonly openTrades = computed(
        () =>
            this.trades().filter(
                trade => trade.state !== 'EXIT',
            ).length,
    );

    readonly closedTrades = computed(
        () =>
            this.trades().filter(
                trade => trade.state === 'EXIT',
            ).length,
    );

    readonly totalPnl = computed(
        () =>
            this.trades().reduce(
                (
                    total,
                    trade,
                ) => total + trade.pnl,
                0,
            ),
    );

    ngOnInit(): void {

        this.refresh();

    }

    refresh(): void {

        this.store.load();

    }

    signalClass(
        trade: Trade,
    ): string {

        switch (trade.signal) {

            case 'BUY':
                return 'buy';

            case 'SELL':
                return 'sell';

            default:
                return 'hold';

        }

    }

    stateClass(
        trade: Trade,
    ): string {

        switch (trade.state) {

            case 'BUY_ACTIVE':
                return 'buy-active';

            case 'SELL_ACTIVE':
                return 'sell-active';

            case 'ENTRY_READY':
                return 'entry-ready';

            case 'EXIT':
                return 'exit';

            default:
                return 'wait';

        }

    }

    pnlClass(
        trade: Trade,
    ): string {

        if (trade.pnl > 0) {

            return 'profit';

        }

        if (trade.pnl < 0) {

            return 'loss';

        }

        return 'neutral';

    }

}