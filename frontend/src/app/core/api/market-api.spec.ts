import { TestBed } from '@angular/core/testing';

import { MarketApi } from './market-api';

describe('MarketApi', () => {
  let service: MarketApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MarketApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
