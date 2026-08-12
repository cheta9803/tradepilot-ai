import {
    ChangeDetectionStrategy,
    Component,
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

    private readonly service = inject(
        PnlHistoryService,
    );

    readonly history = signal<DailyPnl[]>([]);

    readonly selectedDate = signal<string | null>(
        null,
    );

    readonly dayTrades = signal<DailyPnlTrade[]>([]);

    readonly loading = signal(false);

    readonly detailsLoading = signal(false);

    ngOnInit(): void {

        this.refresh();

    }

    refresh(): void {

        this.loading.set(true);

        this.service.getDailyPnl().subscribe({

            next: (data) => {

                this.history.set(data);

                this.loading.set(false);

            },

            error: () => {

                this.history.set([]);

                this.loading.set(false);

            },

        });

    }

    selectDay(
        date: string,
    ): void {

        this.selectedDate.set(date);

        this.dayTrades.set([]);

        this.detailsLoading.set(true);

        this.service.getDayTrades(date).subscribe({

            next: (data) => {

                this.dayTrades.set(data);

                this.detailsLoading.set(false);

            },

            error: () => {

                this.dayTrades.set([]);

                this.detailsLoading.set(false);

            },

        });

    }

    closeDetails(): void {

        this.selectedDate.set(null);

        this.dayTrades.set([]);

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