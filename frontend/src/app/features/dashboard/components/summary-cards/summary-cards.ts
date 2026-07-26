import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { StatCard } from '../../../../shared/ui/stat-card/stat-card';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-summary-cards',
  imports: [StatCard],
  templateUrl: './summary-cards.html',
  styleUrl: './summary-cards.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SummaryCards {
  readonly dashboard = inject(DashboardService);
}