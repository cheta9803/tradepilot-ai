import {
    ChangeDetectionStrategy,
    Component,
    OnInit,
    computed,
    inject,
} from '@angular/core';

import {
    DecimalPipe,
    NgClass,
} from '@angular/common';

import {
    ActivatedRoute,
} from '@angular/router';

import {
    FormsModule,
} from '@angular/forms';

import {
    MatButtonModule,
} from '@angular/material/button';

import {
    MatFormFieldModule,
} from '@angular/material/form-field';

import {
    MatInputModule,
} from '@angular/material/input';

import {
    MatSelectModule,
} from '@angular/material/select';

import {
    PageHeader,
} from '../../../../shared/ui/page-header/page-header';

import {
    SectionCard,
} from '../../../../shared/ui/section-card/section-card';

import {
    StrategyStore,
} from '../../state/strategy.store';

@Component({
    selector: 'app-strategy',
    standalone: true,
    imports: [
        FormsModule,
        DecimalPipe,
        NgClass,
        MatButtonModule,
        MatFormFieldModule,
        MatInputModule,
        MatSelectModule,
        PageHeader,
        SectionCard,
    ],
    templateUrl: './strategy.html',
    styleUrl: './strategy.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Strategy implements OnInit {

    private readonly route = inject(
        ActivatedRoute,
    );

    readonly store = inject(
        StrategyStore,
    );

    symbol = 'RELIANCE';

    timeframe = '1m';

    readonly timeframes = [
        '1m',
        '5m',
        '15m',
    ];

    readonly strategy = this.store.strategy;

    readonly loading = this.store.loading;

    readonly statusLabel = computed(() => {

        const analysis = this.strategy();

        if (!analysis) {
            return '';
        }

        if (analysis.tradable) {
            return 'TRADABLE';
        }

        const marketClosed = analysis.reasons.some(
            reason =>
                reason.toLowerCase().includes('market closed'),
        );

        if (marketClosed) {
            return 'WAIT — MARKET CLOSED';
        }

        return 'WAIT';

    });

    readonly decisionTitle = computed(() => {

        const analysis = this.strategy();

        if (!analysis) {
            return '';
        }

        if (analysis.signal === 'BUY') {
            return analysis.tradable
                ? 'Buy conditions are confirmed.'
                : 'Buy conditions are confirmed historically.';
        }

        if (analysis.signal === 'SELL') {
            return analysis.tradable
                ? 'Sell conditions are confirmed.'
                : 'Sell conditions are confirmed historically.';
        }

        return 'The indicators do not provide enough confirmation for a trade.';

    });

    readonly marketClosed = computed(() => {

        const analysis = this.strategy();

        return !!analysis && analysis.reasons.some(
            reason =>
                reason.toLowerCase().includes('market closed'),
        );

    });

    ngOnInit(): void {

        this.route.queryParamMap.subscribe(
            params => {

                this.symbol =
                    params.get('symbol')
                    ?? 'RELIANCE';

                this.timeframe =
                    params.get('timeframe')
                    ?? '1m';

                this.load();

            },
        );

    }

    load(): void {

        this.store.load(
            this.symbol
                .trim()
                .toUpperCase(),
            this.timeframe,
        );

    }

}
