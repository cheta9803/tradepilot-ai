import { Routes } from '@angular/router';

import { Shell } from './layout/shell/shell';

import { Dashboard } from './features/dashboard/pages/dashboard/dashboard';
import { Market } from './features/market/pages/market/market';
import { Watchlist } from './features/watchlist/pages/watchlist/watchlist';
import { Orders } from './features/orders/pages/orders/orders';
import { Trades } from './features/trades/pages/trades/trades';
import { Portfolio } from './features/portfolio/pages/portfolio/portfolio';
import { Account } from './features/account/pages/account/account';
import { Settings } from './features/settings/pages/settings/settings';

export const routes: Routes = [
    {
        path: '',
        component: Shell,
        children: [
            {
                path: '',
                redirectTo: 'dashboard',
                pathMatch: 'full',
            },
            {
                path: 'dashboard',
                loadComponent: () =>
                    import('./features/dashboard/pages/dashboard/dashboard').then(
                        (m) => m.Dashboard
                    ),
            },
            {
                path: 'market',
                component: Market,
            },
            {
                path: 'watchlist',
                component: Watchlist,
            },
            {
                path: 'orders',
                component: Orders,
            },
            {
                path: 'trades',
                component: Trades,
            },
            {
                path: 'portfolio',
                component: Portfolio,
            },
            {
                path: 'account',
                component: Account,
            },
            {
                path: 'settings',
                component: Settings,
            },
        ],
    },
    {
        path: '**',
        redirectTo: '',
    },
];