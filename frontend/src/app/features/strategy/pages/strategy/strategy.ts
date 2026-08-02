import {
    ChangeDetectionStrategy,
    Component,
    OnInit,
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

    private readonly store = inject(
        StrategyStore,
    );

    symbol = 'RELIANCE';

    readonly strategy = this.store.strategy;

    readonly loading = this.store.loading;

    ngOnInit(): void {

        this.route.queryParamMap.subscribe(
            params => {

                this.symbol =
                    params.get('symbol')
                    ?? 'RELIANCE';

                this.load();

            },
        );

    }

    load(): void {

        this.store.load(
            this.symbol
                .trim()
                .toUpperCase(),
        );

    }

}