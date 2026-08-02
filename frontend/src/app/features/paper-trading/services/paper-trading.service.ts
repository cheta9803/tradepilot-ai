import {
  Injectable,
  inject,
} from '@angular/core';

import {
  HttpClient,
} from '@angular/common/http';

import {
  Observable,
} from 'rxjs';

import {
  environment,
} from '../../../../environments/environment';

import {
  CreatePaperTradeRequest,
} from '../models/paper-trade.model';

@Injectable({
  providedIn: 'root',
})
export class PaperTradingService {

  private readonly http = inject(
    HttpClient,
  );

  private readonly apiUrl =
    `${environment.apiUrl}/paper-trading`;

  create(
    request: CreatePaperTradeRequest,
  ): Observable<{ message: string }> {

    return this.http.post<{ message: string }>(
      this.apiUrl,
      request,
    );

  }

}