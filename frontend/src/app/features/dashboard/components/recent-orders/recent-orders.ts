import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';

import { SectionCard } from '../../../../shared/ui/section-card/section-card';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-recent-orders',
  imports: [
    SectionCard,
    MatTableModule,
    MatChipsModule,
  ],
  templateUrl: './recent-orders.html',
  styleUrl: './recent-orders.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecentOrders {

  readonly dashboard = inject(DashboardService);

  readonly displayedColumns = [
    'symbol',
    'type',
    'quantity',
    'status',
  ];

  readonly dataSource = computed(() => this.dashboard.orders());

}