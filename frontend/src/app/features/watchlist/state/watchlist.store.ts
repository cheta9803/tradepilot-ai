import {
  Injectable,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';

import {
  WatchlistLive,
} from '../models/watchlist.model';

import {
  CreateWatchlistRequest,
} from '../models/watchlist-request.model';

import {
  WatchlistService,
} from '../services/watchlist.service';

import {
  WebSocketService,
} from '../../../core/realtime/services/websocket.service';

@Injectable({
  providedIn: 'root',
})
export class WatchlistStore {

  private readonly service = inject(
    WatchlistService,
  );

  private readonly websocket = inject(
    WebSocketService,
  );

  private readonly watchlistSignal = signal<WatchlistLive[]>(
    [],
  );

  readonly watchlist = computed(
    () => this.watchlistSignal(),
  );

  readonly loading = signal(
    false,
  );

  constructor() {

    effect(() => {

      const tick = this.websocket.lastTick();

      if (!tick) {
        return;
      }

      this.watchlistSignal.update(
        (items) =>
          items.map((item) => {

            if (item.token !== tick.token) {
              return item;
            }

            const change = tick.ltp - tick.close;

            const changePercent =
              tick.close === 0
                ? 0
                : (change / tick.close) * 100;

            return {

              ...item,

              ltp: tick.ltp,

              open: tick.open,

              high: tick.high,

              low: tick.low,

              close: tick.close,

              volume: tick.volume,

              timestamp: tick.timestamp,

              change,

              change_percent: changePercent,

            };

          }),
      );

    });

  }

  load(): void {

    this.loading.set(
      true,
    );

    this.service
      .getLiveWatchlist()
      .subscribe({

        next: (response) => {

          this.watchlistSignal.set(
            response,
          );

          this.loading.set(
            false,
          );

        },

        error: () => {

          this.loading.set(
            false,
          );

        },

      });

  }

  add(
    request: CreateWatchlistRequest,
  ): void {

    this.service
      .create(request)
      .subscribe({

        next: () => {

          this.load();

        },

      });

  }

  remove(
    id: number,
  ): void {

    this.service
      .delete(id)
      .subscribe({

        next: () => {

          this.load();

        },

      });

  }

}