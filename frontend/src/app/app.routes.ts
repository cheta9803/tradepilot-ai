import {
    Routes,
} from '@angular/router';

import {
    Shell,
} from './layout/shell/shell';

import {
    Login,
} from './features/auth/pages/login/login';

import {
    Register,
} from './features/auth/pages/register/register';

export const routes: Routes = [

    {
        path: 'login',
        component: Login,
    },
    {
        path: 'register',
        component: Register,
    },
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
                    import(
                        './features/dashboard/pages/dashboard/dashboard'
                    ).then(
                        (m) => m.Dashboard,
                    ),

            },

            {
                path: 'market',

                loadComponent: () =>
                    import(
                        './features/market/pages/market/market'
                    ).then(
                        (m) => m.Market,
                    ),

            },

            {
                path: 'watchlist',

                loadComponent: () =>
                    import(
                        './features/watchlist/pages/watchlist/watchlist'
                    ).then(
                        (m) => m.Watchlist,
                    ),

            },

            {
                path: 'orders',

                loadComponent: () =>
                    import(
                        './features/orders/pages/orders/orders'
                    ).then(
                        (m) => m.Orders,
                    ),

            },

            {
                path: 'trades',

                loadComponent: () =>
                    import(
                        './features/trades/pages/trades/trades'
                    ).then(
                        (m) => m.Trades,
                    ),

            },

            {
                path: 'portfolio',

                loadComponent: () =>
                    import(
                        './features/portfolio/pages/portfolio/portfolio'
                    ).then(
                        (m) => m.Portfolio,
                    ),

            },

            {
                path: 'account',

                loadComponent: () =>
                    import(
                        './features/account/pages/account/account'
                    ).then(
                        (m) => m.Account,
                    ),

            },

            {
                path: 'settings',

                loadComponent: () =>
                    import(
                        './features/settings/pages/settings/settings'
                    ).then(
                        (m) => m.Settings,
                    ),

            },

        ],

    },

    {
        path: '**',
        redirectTo: '',
    },

];