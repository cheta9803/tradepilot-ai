import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatCard } from './stat-card';

describe('StatCard', () => {
  let component: StatCard;
  let fixture: ComponentFixture<StatCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StatCard]
    })
      .compileComponents();

    fixture = TestBed.createComponent(StatCard);

    fixture.componentRef.setInput(
      'title',
      'Test',
    );

    fixture.componentRef.setInput(
      'value',
      100,
    );

    fixture.componentRef.setInput(
      'icon',
      'trending_up',
    );

    component = fixture.componentInstance;

    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
