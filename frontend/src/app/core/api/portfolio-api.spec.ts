import { TestBed } from '@angular/core/testing';

import { PortfolioApi } from './portfolio-api';

describe('PortfolioApi', () => {
  let service: PortfolioApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PortfolioApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
