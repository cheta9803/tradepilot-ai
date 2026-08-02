import {
    Pipe,
    PipeTransform,
} from '@angular/core';

@Pipe({
    name: 'compactNumber',
    standalone: true,
})
export class CompactNumberPipe
    implements PipeTransform {

    transform(
        value: number | null | undefined,
    ): string {

        if (
            value == null
        ) {

            return '-';

        }

        const abs =
            Math.abs(value);

        if (
            abs >= 1_000_000_000
        ) {

            return (
                value / 1_000_000_000
            ).toFixed(1) + 'B';

        }

        if (
            abs >= 1_000_000
        ) {

            return (
                value / 1_000_000
            ).toFixed(1) + 'M';

        }

        if (
            abs >= 1_000
        ) {

            return (
                value / 1_000
            ).toFixed(1) + 'K';

        }

        return value.toLocaleString(
            'en-IN',
        );

    }

}