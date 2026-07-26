import { TestBed } from '@angular/core/testing';

import { DashboardApi } from './dashboard-api';

describe('DashboardApi', () => {
  let service: DashboardApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DashboardApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
