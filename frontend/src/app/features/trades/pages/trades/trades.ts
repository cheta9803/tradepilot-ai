import {
    ChangeDetectionStrategy,
    Component,
    OnInit,
    inject,
} from '@angular/core';

import {
    DecimalPipe
} from '@angular/common';

import {
    MatCardModule,
} from '@angular/material/card';

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

@Component({
    selector: 'app-trades',
    standalone: true,
    imports: [
        DecimalPipe,
        MatCardModule,
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

    ngOnInit(): void {

        this.store.load();

    }

}