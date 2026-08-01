import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { MatTableModule } from '@angular/material/table';

import { SectionCard } from '../../../../shared/ui/section-card/section-card';
import { DashboardService } from '../../services/dashboard.service';

import { effect } from '@angular/core';

@Component({
  selector: 'app-open-positions',
  imports: [
    SectionCard,
    MatTableModule,
    DecimalPipe,
  ],
  templateUrl: './open-positions.html',
  styleUrl: './open-positions.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OpenPositions {

  readonly dashboard = inject(DashboardService);

  readonly displayedColumns = [
    'symbol',
    'quantity',
    'averagePrice',
    'ltp',
    'pnl',
  ];

  readonly dataSource = computed(() => this.dashboard.positions());

  constructor() {

    effect(() => {

      console.log(
        'OpenPositions Component:',
        this.dataSource(),
      );

    });

  }

}