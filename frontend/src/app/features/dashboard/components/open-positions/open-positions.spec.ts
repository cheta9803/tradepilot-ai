import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OpenPositions } from './open-positions';

describe('OpenPositions', () => {
  let component: OpenPositions;
  let fixture: ComponentFixture<OpenPositions>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OpenPositions]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OpenPositions);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
