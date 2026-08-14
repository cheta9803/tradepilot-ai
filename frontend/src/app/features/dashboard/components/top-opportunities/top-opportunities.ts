import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { DashboardService } from '../../services/dashboard.service';
import { ScannerOpportunity } from '../../models/dashboard.model';
import { SectionCard } from '../../../../shared/ui/section-card/section-card';

@Component({
    selector: 'app-top-opportunities',
    imports: [SectionCard],
    templateUrl: './top-opportunities.html',
    styleUrl: './top-opportunities.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TopOpportunities {
    private readonly router = inject(Router);
    readonly dashboard = inject(DashboardService);

    timeframe(o: ScannerOpportunity, tf: string): string {
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

    setup(o: ScannerOpportunity): string {
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

    decision(o: ScannerOpportunity): string {
        return o.execution_ready ? 'TRADE' : 'WAIT';
    }

    openDetails(o: ScannerOpportunity): void {
        this.router.navigate(['/strategy'], {
            queryParams: { symbol: o.symbol, timeframe: '1m' },
        });
    }
}
