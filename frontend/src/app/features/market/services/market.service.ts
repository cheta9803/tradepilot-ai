import {
    inject,
    Injectable,
} from '@angular/core';

import {
    HttpClient,
    HttpParams,
} from '@angular/common/http';

import {
    Observable,
} from 'rxjs';

import {
    environment,
} from '../../../../environments/environment';

import {
    Instrument,
} from '../models/instrument.model';

import {
    Candle,
} from '../models/candle.model';


export interface LtpResponse {

    symbol: string;

    exchange: string;

    token: string;

    ltp: number;

}


@Injectable({
    providedIn: 'root',
})
export class MarketService {

    private readonly http = inject(
        HttpClient,
    );

    private readonly apiUrl =
        environment.apiUrl;

    search(
        query: string,
        limit = 20,
    ): Observable<Instrument[]> {

        return this.http.get<
            Instrument[]
        >(
            `${this.apiUrl}/instruments/search`,
            {
                params: new HttpParams()
                    .set(
                        'q',
                        query,
                    )
                    .set(
                        'limit',
                        limit,
                    ),
            },
        );

    }

    history(
        symbol: string,
        timeframe = '1m',
        limit = 200,
    ): Observable<Candle[]> {

        return this.http.get<
            Candle[]
        >(
            `${this.apiUrl}/market/history/${symbol}`,
            {
                params: new HttpParams()
                    .set(
                        'timeframe',
                        timeframe,
                    )
                    .set(
                        'limit',
                        limit,
                    ),
            },
        );

    }

    ltp(
        exchange: string,
        symbol: string,
        token: string,
    ): Observable<LtpResponse> {

        return this.http.get<
            LtpResponse
        >(
            `${this.apiUrl}/market/ltp`,
            {
                params: new HttpParams()
                    .set(
                        'exchange',
                        exchange,
                    )
                    .set(
                        'symbol',
                        symbol,
                    )
                    .set(
                        'token',
                        token,
                    ),
            },
        );

    }

}