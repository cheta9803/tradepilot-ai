import { inject, Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import {
  Watchlist,
  WatchlistLive,
} from '../models/watchlist.model';

import {
  CreateWatchlistRequest,
} from '../models/watchlist-request.model';
import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class WatchlistService {

  private readonly http = inject(
    HttpClient,
  );

  private readonly apiUrl =
  `${environment.apiUrl}/watchlist`;

  getWatchlist() {

    return this.http.get<Watchlist[]>(
      this.apiUrl,
    );

  }

  getLiveWatchlist() {

    return this.http.get<WatchlistLive[]>(
      `${this.apiUrl}/live`,
    );

  }

  create(
    request: CreateWatchlistRequest,
  ) {

    return this.http.post<Watchlist>(
      this.apiUrl,
      request,
    );

  }

  delete(
    watchlistId: number,
  ) {

    return this.http.delete<void>(
      `${this.apiUrl}/${watchlistId}`,
    );

  }

}