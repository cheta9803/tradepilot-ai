import { ChangeDetectionStrategy, Component } from '@angular/core';

import { PageHeader } from '../../../../shared/ui/page-header/page-header';
import { SummaryCards } from '../../components/summary-cards/summary-cards';
import { MarketIndices } from '../../components/market-indices/market-indices';
import { OpenPositions } from '../../components/open-positions/open-positions';
import { RecentOrders } from '../../components/recent-orders/recent-orders';
import { Watchlist } from '../../components/watchlist/watchlist';

@Component({
  selector: 'app-dashboard',
  imports: [
    PageHeader,
    SummaryCards,
    MarketIndices,
    OpenPositions,
    RecentOrders,
    Watchlist,
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Dashboard {}