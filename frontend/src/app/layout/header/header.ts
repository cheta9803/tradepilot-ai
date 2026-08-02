import {
  Component,
  inject,
} from '@angular/core';

import {
  Router,
} from '@angular/router';

import {
  MatToolbarModule,
} from '@angular/material/toolbar';

import {
  MatButtonModule,
} from '@angular/material/button';

import {
  MatIconModule,
} from '@angular/material/icon';

import {
  MatMenuModule,
} from '@angular/material/menu';

import {
  AuthStore,
} from '../../features/auth/state/auth.store';

import {
  LayoutService,
} from '../services/layout.service';

import {
  MatDividerModule,
} from '@angular/material/divider';

@Component({
  selector: 'app-header',
  imports: [
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatDividerModule,
  ],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {

  readonly layout = inject(
    LayoutService,
  );

  readonly authStore = inject(
    AuthStore,
  );

  private readonly router = inject(
    Router,
  );

  toggleSidebar(): void {

    this.layout.toggleSidebar();

  }

  logout(): void {

    this.authStore.logout();

    this.router.navigate([
      '/login',
    ]);

  }

}