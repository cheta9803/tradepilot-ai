import { TestBed } from '@angular/core/testing';

import { BaseApi } from './base-api';

describe('BaseApi', () => {
  let service: BaseApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BaseApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
