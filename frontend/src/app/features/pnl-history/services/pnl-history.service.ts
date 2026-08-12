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
    DailyPnl,
    DailyPnlTrade,
} from '../models/pnl-history.model';

@Injectable({
    providedIn: 'root',
})
export class PnlHistoryService {

    private readonly http = inject(
        HttpClient,
    );

    private readonly apiUrl =
        `${environment.apiUrl}/trades/history/daily`;

    getDailyPnl(): Observable<DailyPnl[]> {

        return this.http.get<DailyPnl[]>(
            this.apiUrl,
        );

    }

    getDayTrades(
        date: string,
    ): Observable<DailyPnlTrade[]> {

        return this.http.get<DailyPnlTrade[]>(
            `${this.apiUrl}/${date}`,
        );

    }
}