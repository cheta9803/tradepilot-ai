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
    Trade,
} from '../models/trade.model';

@Injectable({
    providedIn: 'root',
})
export class TradesService {

    private readonly http = inject(
        HttpClient,
    );

    private readonly apiUrl =
        `${environment.apiUrl}/trades`;

    getAll(): Observable<Trade[]> {

        return this.http.get<Trade[]>(
            this.apiUrl,
        );

    }

    getOpen(): Observable<Trade[]> {

        return this.http.get<Trade[]>(
            `${this.apiUrl}/open`,
        );

    }

    getClosed(): Observable<Trade[]> {

        return this.http.get<Trade[]>(
            `${this.apiUrl}/closed`,
        );

    }

}