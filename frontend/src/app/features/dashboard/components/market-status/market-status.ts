import {
    ChangeDetectionStrategy,
    Component,
    computed,
    inject,
} from '@angular/core';

import { DashboardService } from '../../services/dashboard.service';

@Component({
    selector: 'app-market-status',
    templateUrl: './market-status.html',
    styleUrl: './market-status.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MarketStatus {

    private readonly dashboardService = inject(
        DashboardService,
    );

    readonly status = computed(() => {

        const opportunity =
            this.dashboardService
                .scannerOpportunities()[0];

        if (!opportunity) {

            return {
                marketStatus: 'UNKNOWN',
                dataStatus: 'UNKNOWN',
                recommendationsAvailable: false,
                ageSeconds: null as number | null,
                marketLabel: 'Market status unavailable',
                dataLabel: 'Waiting for scanner data',
                message:
                    'Scanner data is not available yet.',
            };

        }

        const marketStatus =
            (
                opportunity.market_status ??
                'UNKNOWN'
            ).toUpperCase();

        const dataStatus =
            (
                opportunity.data_status ??
                'UNKNOWN'
            ).toUpperCase();

        const recommendationsAvailable =
            opportunity
                .recommendations_available ??
            false;

        const ageSeconds =
            opportunity.data_age_seconds ??
            null;

        let message =
            'Market data is available.';

        if (
            marketStatus === 'CLOSED' &&
            dataStatus === 'STALE'
        ) {

            message =
                'Market is closed and the displayed data is stale. Trading recommendations are unavailable.';

        } else if (
            marketStatus === 'CLOSED'
        ) {

            message =
                'Market is currently closed. Trading recommendations are unavailable.';

        } else if (
            !recommendationsAvailable
        ) {

            message =
                'Trading recommendations are currently unavailable.';

        }

        return {
            marketStatus,
            dataStatus,
            recommendationsAvailable,
            ageSeconds,

            marketLabel:
                marketStatus === 'OPEN'
                    ? 'Market Open'
                    : marketStatus === 'CLOSED'
                        ? 'Market Closed'
                        : 'Market Status Unknown',

            dataLabel:
                dataStatus === 'LIVE'
                    ? 'Live Data'
                    : dataStatus === 'STALE'
                        ? 'Stale Data'
                        : 'Data Status Unknown',

            message,
        };

    });

    formatAge(
        seconds: number | null,
    ): string {

        if (
            seconds === null ||
            !Number.isFinite(seconds)
        ) {
            return '';
        }

        const roundedSeconds =
            Math.max(
                0,
                Math.round(seconds),
            );

        if (roundedSeconds < 60) {

            return `${roundedSeconds}s old`;

        }

        const minutes =
            Math.floor(
                roundedSeconds / 60,
            );

        if (minutes < 60) {

            return `${minutes}m old`;

        }

        const hours =
            Math.floor(
                minutes / 60,
            );

        const remainingMinutes =
            minutes % 60;

        if (remainingMinutes === 0) {

            return `${hours}h old`;

        }

        return `${hours}h ${remainingMinutes}m old`;

    }

}