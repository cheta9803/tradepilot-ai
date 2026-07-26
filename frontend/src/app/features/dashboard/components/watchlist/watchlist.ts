import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';

import { SectionCard } from '../../../../shared/ui/section-card/section-card';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-watchlist',
  imports: [
    SectionCard,
    DecimalPipe,
  ],
  templateUrl: './watchlist.html',
  styleUrl: './watchlist.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Watchlist {

  readonly dashboard = inject(DashboardService);

  readonly stocks = computed(() => [
    {
      symbol: 'RELIANCE',
      price: 2725.15,
      change: 18.25,
    },
    {
      symbol: 'TCS',
      price: 3605.20,
      change: -24.50,
    },
    {
      symbol: 'INFY',
      price: 1608.70,
      change: 12.40,
    },
    {
      symbol: 'HDFCBANK',
      price: 1987.80,
      change: 8.35,
    },
  ]);

}