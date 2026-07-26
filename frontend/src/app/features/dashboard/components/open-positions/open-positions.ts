import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { SectionCard } from '../../../../shared/ui/section-card/section-card';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-open-positions',
  imports: [SectionCard],
  templateUrl: './open-positions.html',
  styleUrl: './open-positions.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OpenPositions {
  readonly dashboard = inject(DashboardService);
}