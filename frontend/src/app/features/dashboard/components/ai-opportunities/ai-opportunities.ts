import {
    ChangeDetectionStrategy,
    Component,
    inject,
} from '@angular/core';

import { DecimalPipe } from '@angular/common';

import { DashboardService } from '../../services/dashboard.service';

import { SectionCard } from '../../../../shared/ui/section-card/section-card';

@Component({
    selector: 'app-ai-opportunities',
    imports: [
        DecimalPipe,
        SectionCard,
    ],
    templateUrl: './ai-opportunities.html',
    styleUrl: './ai-opportunities.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AiOpportunities {

    readonly dashboard = inject(
        DashboardService,
    );

}