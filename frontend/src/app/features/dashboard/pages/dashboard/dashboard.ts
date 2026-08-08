import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
} from '@angular/core';

import { DashboardService } from '../../services/dashboard.service';

import { PageHeader } from '../../../../shared/ui/page-header/page-header';

import { SummaryCards } from '../../components/summary-cards/summary-cards';

import { MarketStatus } from '../../components/market-status/market-status';

import { TopOpportunities } from '../../components/top-opportunities/top-opportunities';

import { AiOpportunities } from '../../components/ai-opportunities/ai-opportunities';

import { MarketIndices } from '../../components/market-indices/market-indices';

import { OpenPositions } from '../../components/open-positions/open-positions';

import { RecentOrders } from '../../components/recent-orders/recent-orders';

import { Watchlist } from '../../components/watchlist/watchlist';

@Component({
  selector: 'app-dashboard',

  imports: [
    PageHeader,
    SummaryCards,
    MarketStatus,
    TopOpportunities,
    AiOpportunities,
    MarketIndices,
    OpenPositions,
    RecentOrders,
    Watchlist,
  ],

  templateUrl: './dashboard.html',

  styleUrl: './dashboard.scss',

  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class Dashboard implements OnInit {

  private readonly dashboardService =
    inject(DashboardService);

  constructor() {

    console.log(
      'Dashboard component created',
    );

  }

  ngOnInit(): void {

    this.dashboardService.load();

  }

}