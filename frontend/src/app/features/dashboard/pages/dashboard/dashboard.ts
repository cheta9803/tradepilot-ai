import { ChangeDetectionStrategy, Component } from '@angular/core';

import { PageHeader } from '../../../../shared/ui/page-header/page-header';
import { StatCard } from '../../../../shared/ui/stat-card/stat-card';

@Component({
  selector: 'app-dashboard',
  imports: [PageHeader, StatCard],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Dashboard {}