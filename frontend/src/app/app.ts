import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { WebSocketService } from './core/realtime/services/websocket.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {

  private readonly websocket = inject(
    WebSocketService,
  );

  constructor() {

    this.websocket.connect();

  }

}