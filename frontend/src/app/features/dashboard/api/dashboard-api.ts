import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_CONFIG } from '../../../core/http/config/api.config';

import {
  AiOpportunity,
  DashboardSummary,
  MarketIndex,
  Order,
  Position,
  ScannerOpportunity,
} from '../models/dashboard.model';

export interface DashboardResponse {
  summary: DashboardSummary;
  indices: MarketIndex[];
  positions: Position[];
  orders: Order[];
}

@Injectable({
  providedIn: 'root',
})
export class DashboardApi {
  private readonly http = inject(HttpClient);

  getDashboard(): Observable<DashboardResponse> {
    return this.http.get<DashboardResponse>(
      `${API_CONFIG.baseUrl}/dashboard`,
    );
  }

  getTopScanner(limit = 5): Observable<ScannerOpportunity[]> {
    const params = new HttpParams().set(
      'limit',
      limit,
    );

    return this.http.get<ScannerOpportunity[]>(
      `${API_CONFIG.baseUrl}/scanner/top`,
      { params },
    );
  }

  getTopAi(limit = 5): Observable<AiOpportunity[]> {
    const params = new HttpParams().set(
      'limit',
      limit,
    );

    return this.http.get<AiOpportunity[]>(
      `${API_CONFIG.baseUrl}/ai/top`,
      { params },
    );
  }
}