export interface NavigationItem {
  label: string;
  icon: string;
  route: string;
}

export const NAVIGATION: NavigationItem[] = [
  {
    label: 'Dashboard',
    icon: 'dashboard',
    route: '/dashboard',
  },
  {
    label: 'Market',
    icon: 'monitoring',
    route: '/market',
  },
  {
    label: 'Watchlist',
    icon: 'visibility',
    route: '/watchlist',
  },
  {
    label: 'Orders',
    icon: 'receipt_long',
    route: '/orders',
  },
  {
    label: 'Trades',
    icon: 'swap_horiz',
    route: '/trades',
  },
  {
    label: 'P&L History',
    icon: 'analytics',
    route: '/pnl-history',
  },
  {
    label: 'Portfolio',
    icon: 'account_balance_wallet',
    route: '/portfolio',
  },
  {
    label: 'Account',
    icon: 'person',
    route: '/account',
  },
  {
    label: 'Settings',
    icon: 'settings',
    route: '/settings',
  },
];