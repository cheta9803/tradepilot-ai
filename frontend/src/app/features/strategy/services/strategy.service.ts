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
    StrategyResponse,
} from '../models/strategy.model';

@Injectable({
    providedIn: 'root',
})
export class StrategyService {

    private readonly http = inject(
        HttpClient,
    );

    private readonly apiUrl =
        `${environment.apiUrl}/strategy`;

    analyze(
        symbol: string,
        timeframe = '1m',
    ): Observable<StrategyResponse> {

        return this.http.get<StrategyResponse>(
            `${this.apiUrl}/intraday/${symbol}`,
            {
                params: {
                    timeframe,
                },
            },
        );

    }

}