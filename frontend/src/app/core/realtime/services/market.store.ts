import {
    Injectable,
    computed,
    effect,
    inject,
    signal,
} from '@angular/core';

import { MarketTick } from '../models/market-tick.model';
import { WebSocketService } from './websocket.service';

@Injectable({
    providedIn: 'root',
})
export class MarketStore {

    private readonly websocket = inject(
        WebSocketService,
    );

    private readonly ticks = signal(
        new Map<string, MarketTick>(),
    );

    readonly market = computed(
        () => this.ticks(),
    );

    constructor() {

        console.log(
            'MarketStore instance created',
        );

        effect(() => {

            const tick = this.websocket.lastTick();

            if (!tick) {
                return;
            }

            console.log(
                'MarketStore received:',
                tick,
            );

            this.ticks.update(current => {

                const next = new Map(current);

                next.set(
                    tick.symbol,
                    tick,
                );

                return next;

            });

        });

    }

    getTick(
        symbol: string,
    ): MarketTick | undefined {

        return this.market().get(
            symbol,
        );

    }

}