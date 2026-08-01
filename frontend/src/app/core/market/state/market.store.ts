import {
  Injectable,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';

import {
  MarketPrice,
} from '../models/market-price.model';

import {
  WebSocketService,
} from '../../realtime/services/websocket.service';

@Injectable({
  providedIn: 'root',
})
export class MarketStore {

  private readonly websocket = inject(
    WebSocketService,
  );

  private readonly prices = signal(
    new Map<string, MarketPrice>(),
  );

  readonly connected = computed(
    () => this.websocket.connected(),
  );

  constructor() {

    effect(() => {

      const tick = this.websocket.lastTick();

      if (!tick) {

        return;

      }

      this.prices.update(
        current => {

          const next = new Map(
            current,
          );

          next.set(
            tick.token,
            tick,
          );

          return next;

        },
      );

    });

  }

  getByToken(
    token: string,
  ): MarketPrice | undefined {

    return this.prices().get(
      token,
    );

  }

  hasToken(
    token: string,
  ): boolean {

    return this.prices().has(
      token,
    );

  }

}