import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MarketIndices } from './market-indices';

describe('MarketIndices', () => {
  let component: MarketIndices;
  let fixture: ComponentFixture<MarketIndices>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MarketIndices]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MarketIndices);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
