import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';

import { SectionCard } from '../../../../shared/ui/section-card/section-card';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-market-indices',
  imports: [
    SectionCard,
    DecimalPipe,
  ],
  templateUrl: './market-indices.html',
  styleUrl: './market-indices.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MarketIndices {
  readonly dashboard = inject(DashboardService);
}