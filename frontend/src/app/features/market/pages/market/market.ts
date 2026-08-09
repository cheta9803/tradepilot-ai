import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  DatePipe,
  DecimalPipe,
} from '@angular/common';

import {
  catchError,
  finalize,
  of,
} from 'rxjs';

import {
  Router,
} from '@angular/router';

import {
  MatAutocompleteModule,
} from '@angular/material/autocomplete';

import {
  MatButtonModule,
} from '@angular/material/button';

import {
  MatCardModule,
} from '@angular/material/card';

import {
  MatFormFieldModule,
} from '@angular/material/form-field';

import {
  MatInputModule,
} from '@angular/material/input';

import {
  PageHeader,
} from '../../../../shared/ui/page-header/page-header';

import {
  SectionCard,
} from '../../../../shared/ui/section-card/section-card';

import {
  Instrument,
} from '../../models/instrument.model';

import {
  Candle,
} from '../../models/candle.model';

import {
  MarketService,
  LtpResponse,
} from '../../services/market.service';

import {
  MarketStore,
} from '../../../../core/market/state/market.store';

import {
  WatchlistStore,
} from '../../../watchlist/state/watchlist.store';


@Component({
  selector: 'app-market',

  standalone: true,

  imports: [
    FormsModule,
    DatePipe,
    DecimalPipe,
    MatAutocompleteModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    PageHeader,
    SectionCard,
  ],

  templateUrl: './market.html',

  styleUrl: './market.scss',

  changeDetection:
    ChangeDetectionStrategy.OnPush,
})
export class Market {

  private readonly router =
    inject(Router);

  private readonly marketService =
    inject(MarketService);

  private readonly realtime =
    inject(MarketStore);

  readonly watchlist =
    inject(WatchlistStore);


  // --------------------------------------------------
  // UI STATE
  // --------------------------------------------------

  readonly loading =
    signal(false);

  readonly ltpLoading =
    signal(false);

  readonly search =
    signal('');

  readonly instruments =
    signal<Instrument[]>([]);

  readonly selected =
    signal<Instrument | null>(null);

  readonly candles =
    signal<Candle[]>([]);

  readonly ltp =
    signal<number | null>(null);

  readonly selectedTimeframe =
    signal('5m');


  readonly timeframes = [
    '1m',
    '5m',
    '15m',
    '1h',
  ];


  // --------------------------------------------------
  // LIVE / LAST AVAILABLE PRICE
  // --------------------------------------------------

  readonly livePrice =
    computed(() => {

      const instrument =
        this.selected();

      if (!instrument) {
        return null;
      }

      const realtimePrice =
        this.realtime.getByToken(
          instrument.token,
        );

      if (
        realtimePrice?.ltp != null
      ) {

        return realtimePrice.ltp;

      }

      if (this.ltp() != null) {

        return this.ltp();

      }

      const candles =
        this.candles();

      if (!candles.length) {

        return null;

      }

      return (
        candles[candles.length - 1]
          ?.close ?? null
      );

    });


  readonly latestCandle =
    computed(() => {

      const candles =
        this.candles();

      if (!candles.length) {

        return null;

      }

      return candles[
        candles.length - 1
      ];

    });


  readonly previousCandle =
    computed(() => {

      const candles =
        this.candles();

      if (candles.length < 2) {

        return null;

      }

      return candles[
        candles.length - 2
      ];

    });


  // --------------------------------------------------
  // LATEST CANDLE CHANGE
  // --------------------------------------------------

  readonly change =
    computed(() => {

      const latest =
        this.latestCandle();

      const previous =
        this.previousCandle();

      if (
        !latest ||
        !previous
      ) {

        return 0;

      }

      return (
        latest.close -
        previous.close
      );

    });


  readonly changePercent =
    computed(() => {

      const latest =
        this.latestCandle();

      const previous =
        this.previousCandle();

      if (
        !latest ||
        !previous ||
        previous.close === 0
      ) {

        return 0;

      }

      return (
        (
          latest.close -
          previous.close
        ) /
        previous.close
      ) * 100;

    });


  // --------------------------------------------------
  // MARKET DATA
  // --------------------------------------------------

  readonly high =
    computed(() =>
      this.latestCandle()?.high ?? null
    );

  readonly low =
    computed(() =>
      this.latestCandle()?.low ?? null
    );

  readonly open =
    computed(() =>
      this.latestCandle()?.open ?? null
    );

  readonly close =
    computed(() =>
      this.latestCandle()?.close ?? null
    );

  readonly volume =
    computed(() =>
      this.latestCandle()?.volume ?? null
    );


  // --------------------------------------------------
  // DATA FRESHNESS
  // --------------------------------------------------

  readonly lastUpdated =
    computed(() => {

      const candle =
        this.latestCandle();

      if (!candle) {

        return null;

      }

      return new Date(
        candle.timestamp,
      );

    });


  readonly dataAgeMinutes =
    computed(() => {

      const updated =
        this.lastUpdated();

      if (!updated) {

        return null;

      }

      const difference =
        Date.now() -
        updated.getTime();

      return Math.max(
        0,
        Math.round(
          difference /
          60000,
        ),
      );

    });


  readonly dataStatus =
    computed(() => {

      const age =
        this.dataAgeMinutes();

      if (age == null) {

        return 'NO DATA';

      }

      if (age <= 5) {

        return 'LIVE';

      }

      if (age <= 60) {

        return 'RECENT';

      }

      return 'STALE';

    });


  // --------------------------------------------------
  // SIMPLE SVG PRICE CHART
  // --------------------------------------------------

  readonly chartPath =
    computed(() => {

      const candles =
        this.candles();

      if (candles.length < 2) {

        return '';

      }

      const values =
        candles.map(
          candle => candle.close,
        );

      const width = 900;
      const height = 280;
      const padding = 16;

      const min =
        Math.min(...values);

      const max =
        Math.max(...values);

      const range =
        max - min || 1;

      const step =
        (
          width -
          padding * 2
        ) /
        (
          values.length - 1
        );

      return values
        .map(
          (
            value,
            index,
          ) => {

            const x =
              padding +
              index * step;

            const y =
              height -
              padding -
              (
                (
                  value - min
                ) /
                range
              ) *
              (
                height -
                padding * 2
              );

            return `${
              index === 0
                ? 'M'
                : 'L'
            } ${x.toFixed(2)} ${y.toFixed(2)}`;

          },
        )
        .join(' ');

    });


  // --------------------------------------------------
  // SEARCH
  // --------------------------------------------------

  searchInstrument(): void {

    const query =
      this.search().trim();

    if (
      query.length < 2
    ) {

      this.instruments.set([]);

      return;

    }

    this.marketService
      .search(query)
      .subscribe({

        next: response => {

          this.instruments.set(
            response,
          );

        },

        error: () => {

          this.instruments.set([]);

        },

      });

  }


  // --------------------------------------------------
  // SELECT INSTRUMENT
  // --------------------------------------------------

  selectInstrument(
    instrument: Instrument,
  ): void {

    this.selected.set(
      instrument,
    );

    this.search.set(
      instrument.symbol,
    );

    this.instruments.set([]);

    this.candles.set([]);

    this.ltp.set(null);

    this.loadHistory();

    this.loadLtp();

  }


  // --------------------------------------------------
  // TIMEFRAME
  // --------------------------------------------------

  selectTimeframe(
    timeframe: string,
  ): void {

    if (
      this.selectedTimeframe() ===
      timeframe
    ) {

      return;

    }

    this.selectedTimeframe.set(
      timeframe,
    );

    if (this.selected()) {

      this.loadHistory();

    }

  }


  // --------------------------------------------------
  // HISTORY
  // --------------------------------------------------

  private loadHistory(): void {

    const instrument =
      this.selected();

    if (!instrument) {

      return;

    }

    this.loading.set(
      true,
    );

    this.marketService
      .history(
        instrument.symbol,
        this.selectedTimeframe(),
        100,
      )
      .pipe(

        finalize(() => {

          this.loading.set(
            false,
          );

        }),

        catchError(() => {

          this.candles.set([]);

          return of(
            [] as Candle[],
          );

        }),

      )
      .subscribe({

        next: response => {

          this.candles.set(
            response,
          );

        },

      });

  }


  // --------------------------------------------------
  // LTP
  // --------------------------------------------------

  private loadLtp(): void {

    const instrument =
      this.selected();

    if (!instrument) {

      return;

    }

    this.ltpLoading.set(
      true,
    );

    this.marketService
      .ltp(
        instrument.exchange,
        instrument.symbol,
        instrument.token,
      )
      .pipe(

        finalize(() => {

          this.ltpLoading.set(
            false,
          );

        }),

        catchError(() => {

          this.ltp.set(
            null,
          );

          return of(
            null as LtpResponse | null,
          );

        }),

      )
      .subscribe({

        next: response => {

          if (!response) {

            return;

          }

          this.ltp.set(
            response.ltp,
          );

        },

      });

  }


  // --------------------------------------------------
  // WATCHLIST
  // --------------------------------------------------

  addToWatchlist(): void {

    const instrument =
      this.selected();

    if (!instrument) {

      return;

    }

    this.watchlist.add({

      exchange:
        instrument.exchange,

      symbol:
        instrument.symbol,

    });

  }


  // --------------------------------------------------
  // AI STRATEGY
  // --------------------------------------------------

  openStrategy(): void {

    const instrument =
      this.selected();

    if (!instrument) {

      return;

    }

    this.router.navigate(
      [
        '/strategy',
      ],
      {
        queryParams: {
          symbol:
            instrument.symbol,
        },
      },
    );

  }

}