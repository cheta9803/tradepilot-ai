import {
  Component,
  inject,
} from '@angular/core';

import {
  RouterOutlet,
} from '@angular/router';

import {
  AuthStore,
} from './features/auth/state/auth.store';

import {
  WebSocketService,
} from './core/realtime/services/websocket.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {

  private readonly authStore = inject(
    AuthStore,
  );

  private readonly websocket = inject(
    WebSocketService,
  );

  constructor() {

    this.authStore.restoreSession();

    this.websocket.connect();

  }

}