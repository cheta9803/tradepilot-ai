import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';

import { FormsModule } from '@angular/forms';
import { DecimalPipe } from '@angular/common';

import { finalize } from 'rxjs';

import {
  Router,
} from '@angular/router';

import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { PageHeader } from '../../../../shared/ui/page-header/page-header';
import { SectionCard } from '../../../../shared/ui/section-card/section-card';

import { Instrument } from '../../models/instrument.model';
import { Candle } from '../../models/candle.model';

import { MarketService } from '../../services/market.service';
import { MarketStore } from '../../../../core/market/state/market.store';
import { WatchlistStore } from '../../../watchlist/state/watchlist.store';

@Component({
  selector: 'app-market',
  standalone: true,
  imports: [
    FormsModule,
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
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Market {

  private readonly router = inject(
    Router,
  );

  private readonly marketService = inject(
    MarketService,
  );

  private readonly realtime = inject(
    MarketStore,
  );

  readonly watchlist = inject(
    WatchlistStore,
  );

  readonly loading = signal(
    false,
  );

  readonly search = signal(
    '',
  );

  readonly instruments = signal<Instrument[]>(
    [],
  );

  readonly selected = signal<Instrument | null>(
    null,
  );

  readonly candles = signal<Candle[]>(
    [],
  );

  readonly livePrice = computed(() => {

    const instrument = this.selected();

    if (!instrument) {

      return null;

    }

    return this.realtime.getByToken(
      instrument.token,
    );

  });

  readonly change = computed(() => {

    const price = this.livePrice();

    if (!price) {

      return 0;

    }

    return price.ltp - price.close;

  });

  readonly changePercent = computed(() => {

    const price = this.livePrice();

    if (!price) {

      return 0;

    }

    if (price.close === 0) {

      return 0;

    }

    return (
      (price.ltp - price.close)
      / price.close
    ) * 100;

  });

  searchInstrument(): void {

    const query = this.search().trim();

    if (query.length < 2) {

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

      });

  }

  selectInstrument(
    instrument: Instrument,
  ): void {

    this.selected.set(
      instrument,
    );

    this.search.set(
      instrument.symbol,
    );

    this.loading.set(
      true,
    );

    this.marketService
      .history(
        instrument.symbol,
      )
      .pipe(
        finalize(() =>
          this.loading.set(
            false,
          ),
        ),
      )
      .subscribe({

        next: response => {

          this.candles.set(
            response,
          );

        },

      });

  }

  addToWatchlist(): void {

    const instrument = this.selected();

    if (!instrument) {

      return;

    }

    this.watchlist.add({

      exchange: instrument.exchange,

      symbol: instrument.symbol,

    });

  }

  openStrategy(): void {

    const instrument = this.selected();

    if (!instrument) {

      return;

    }

    this.router.navigate(
      [
        '/strategy',
      ],
      {
        queryParams: {
          symbol: instrument.symbol,
        },
      },
    );

  }

}