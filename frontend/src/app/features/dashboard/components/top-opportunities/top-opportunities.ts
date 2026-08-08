import {
    ChangeDetectionStrategy,
    Component,
    inject,
} from '@angular/core';

import { DecimalPipe } from '@angular/common';

import { DashboardService } from '../../services/dashboard.service';

import { SectionCard } from '../../../../shared/ui/section-card/section-card';

@Component({
    selector: 'app-top-opportunities',
    imports: [
        DecimalPipe,
        SectionCard,
    ],
    templateUrl: './top-opportunities.html',
    styleUrl: './top-opportunities.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TopOpportunities {

    readonly dashboard = inject(
        DashboardService,
    );

}