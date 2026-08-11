import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { DashboardService } from '../../services/dashboard.service';
import { AiOpportunity } from '../../models/dashboard.model';
import { SectionCard } from '../../../../shared/ui/section-card/section-card';

@Component({
    selector: 'app-ai-opportunities',
    imports: [SectionCard],
    templateUrl: './ai-opportunities.html',
    styleUrl: './ai-opportunities.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AiOpportunities {
    private readonly router = inject(Router);
    readonly dashboard = inject(DashboardService);

    timeframe(o: AiOpportunity, tf: string): string {
        const timeframes = o.timeframes ?? {};
        const aliases: Record<string, string[]> = {
            '15m': ['15m', 'fifteen_minutes'],
            '5m': ['5m', 'five_minutes'],
            '1m': ['1m', 'one_minute'],
        };

        for (const key of aliases[tf] ?? [tf]) {
            const value = timeframes[key];
            if (typeof value === 'string') {
                return value;
            }
        }

        return 'UNKNOWN';
    }

    setup(o: AiOpportunity): string {
        const a = this.timeframe(o, '15m');
        const b = this.timeframe(o, '5m');
        const c = this.timeframe(o, '1m');
        const signals = [a, b, c];
        if (signals.includes('BUY') && signals.includes('SELL')) return 'Conflict';
        if ((a === 'BUY' || a === 'SELL') && a === b && b === c) return 'Strong';
        if ((a === 'BUY' || a === 'SELL') && a === b) return 'Good';
        if ((b === 'BUY' || b === 'SELL') && b === c) return 'Medium';
        return 'Weak';
    }

    decision(o: AiOpportunity): string {
        return o.trade_ready ? 'TRADE' : 'WAIT';
    }

    openDetails(o: AiOpportunity): void {
        if (!o.symbol) return;
        this.router.navigate(['/strategy'], {
            queryParams: { symbol: o.symbol, timeframe: '1m' },
        });
    }
}
