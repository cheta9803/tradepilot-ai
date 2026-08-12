import {
    ComponentFixture,
    TestBed,
} from '@angular/core/testing';

import {
    PnlHistory,
} from './pnl-history';

describe('PnlHistory', () => {

    let component: PnlHistory;

    let fixture: ComponentFixture<PnlHistory>;

    beforeEach(async () => {

        await TestBed.configureTestingModule({
            imports: [
                PnlHistory,
            ],
        }).compileComponents();

        fixture =
            TestBed.createComponent(
                PnlHistory,
            );

        component =
            fixture.componentInstance;

        fixture.detectChanges();

    });

    it('should create', () => {

        expect(component).toBeTruthy();

    });

});