import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_CONFIG } from '../../../core/http/config/api.config';
import {
  DashboardSummary,
  MarketIndex,
  Order,
  Position,
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

}