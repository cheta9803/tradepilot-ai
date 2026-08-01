import {
    Injectable,
    signal,
} from '@angular/core';

import {
    MarketTick,
} from '../models/market-tick.model';

@Injectable({
    providedIn: 'root',
})
export class WebSocketService {

    private socket?: WebSocket;

    readonly connected = signal(
        false,
    );

    readonly lastTick = signal<MarketTick | null>(
        null,
    );

    connect(): void {

        if (this.socket) {
            return;
        }

        console.log(
            'Creating websocket...',
        );

        this.socket = new WebSocket(
            'ws://127.0.0.1:8000/ws/market',
        );

        this.socket.onopen = () => {

            console.log(
                'WS OPEN',
            );

            this.connected.set(
                true,
            );

        };

        this.socket.onmessage = (
            event,
        ) => {

            const tick = JSON.parse(
                event.data,
            ) as MarketTick;

            this.lastTick.set(
                tick,
            );

        };

        this.socket.onclose = (
            event,
        ) => {

            console.warn(
                'WS CLOSED',
                {
                    code: event.code,
                    reason: event.reason,
                    wasClean: event.wasClean,
                },
            );

            this.connected.set(
                false,
            );

            this.socket = undefined;

            setTimeout(() => {

                console.log(
                    'Reconnecting...',
                );

                this.connect();

            }, 2000);

        };

        this.socket.onerror = (
            event,
        ) => {

            console.error(
                'WS ERROR',
                event,
            );

        };

    }

}