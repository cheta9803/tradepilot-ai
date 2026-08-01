import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
} from '@angular/core';

import {
  DecimalPipe,
} from '@angular/common';

import {
  FormsModule,
} from '@angular/forms';

import {
  MatTableModule,
} from '@angular/material/table';

import {
  MatIconModule,
} from '@angular/material/icon';

import {
  MatButtonModule,
} from '@angular/material/button';

import {
  MatFormFieldModule,
} from '@angular/material/form-field';

import {
  MatInputModule,
} from '@angular/material/input';

import {
  MatSelectModule,
} from '@angular/material/select';

import { PageHeader } from '../../../../shared/ui/page-header/page-header';
import { SectionCard } from '../../../../shared/ui/section-card/section-card';

import { WatchlistStore } from '../../state/watchlist.store';

@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [
    PageHeader,
    SectionCard,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    DecimalPipe,
  ],
  templateUrl: './watchlist.html',
  styleUrl: './watchlist.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Watchlist implements OnInit {

  readonly store = inject(
    WatchlistStore,
  );

  exchange = 'NSE';

  symbol = '';

  readonly displayedColumns = [
    'symbol',
    'ltp',
    'change',
    'changePercent',
    'volume',
    'actions',
  ];

  ngOnInit(): void {

    this.store.load();

  }

  add(): void {

    const symbol = this.symbol
      .trim()
      .toUpperCase();

    if (!symbol) {

      return;

    }

    this.store.add({

      exchange: this.exchange,

      symbol,

    });

    this.symbol = '';

  }

  delete(
    id: number,
  ): void {

    this.store.remove(
      id,
    );

  }

}