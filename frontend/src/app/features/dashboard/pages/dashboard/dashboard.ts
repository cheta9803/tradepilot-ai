import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { PageHeader } from '../../../../shared/ui/page-header/page-header';
import { SectionCard } from '../../../../shared/ui/section-card/section-card';
import { SummaryCards } from '../../components/summary-cards/summary-cards';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  imports: [
    PageHeader,
    SummaryCards,
    SectionCard,
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Dashboard {
  readonly dashboard = inject(DashboardService);
}