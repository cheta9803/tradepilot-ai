import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SectionCard } from './section-card';

describe('SectionCard', () => {
  let component: SectionCard;
  let fixture: ComponentFixture<SectionCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SectionCard]
    })
      .compileComponents();

    fixture = TestBed.createComponent(SectionCard);
    fixture.componentRef.setInput(
      'title',
      'Test Section',
    );
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
