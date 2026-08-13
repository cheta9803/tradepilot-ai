import {
    ComponentFixture,
    TestBed,
} from '@angular/core/testing';

import {
    of,
} from 'rxjs';

import {
    PnlHistory,
} from './pnl-history';

import {
    PnlHistoryService,
} from '../../services/pnl-history.service';


describe('PnlHistory', () => {

    let component: PnlHistory;

    let fixture: ComponentFixture<PnlHistory>;

    beforeEach(async () => {

        await TestBed.configureTestingModule({
            imports: [
                PnlHistory,
            ],
            providers: [
                {
                    provide: PnlHistoryService,
                    useValue: {
                        getDailyPnl: () => of([]),
                        getDayTrades: () => of([]),
                    },
                },
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

    it('should render gross loss with the loss class', () => {

        expect(component.grossLossClass()).toBe('loss');

    });

    it('should display exit reasons clearly', () => {

        expect(
            component.reasonLabel('STOPLOSS'),
        ).toBe('STOP LOSS');

        expect(
            component.reasonLabel('TRAILING_STOP'),
        ).toBe('TRAILING STOP');

        expect(
            component.reasonLabel('BREAKEVEN_STOP'),
        ).toBe('BREAKEVEN STOP');

        expect(
            component.reasonLabel('EOD'),
        ).toBe('END OF DAY');

        expect(
            component.reasonLabel(null),
        ).toBe('—');

    });

});
