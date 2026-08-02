import {
    ChangeDetectionStrategy,
    Component,
    inject,
} from '@angular/core';

import {
    FormBuilder,
    ReactiveFormsModule,
    Validators,
} from '@angular/forms';

import {
    Router,
    RouterLink,
} from '@angular/router';

import {
    MatButtonModule,
} from '@angular/material/button';

import {
    MatCardModule,
} from '@angular/material/card';

import {
    MatFormFieldModule,
} from '@angular/material/form-field';

import {
    MatInputModule,
} from '@angular/material/input';

import {
    AuthStore,
} from '../../state/auth.store';

@Component({
    selector: 'app-login',

    standalone: true,

    imports: [

        ReactiveFormsModule,

        RouterLink,

        MatCardModule,

        MatFormFieldModule,

        MatInputModule,

        MatButtonModule,

    ],

    templateUrl: './login.html',

    styleUrl: './login.scss',

    changeDetection:
        ChangeDetectionStrategy.OnPush,

})
export class Login {

    private readonly fb = inject(
        FormBuilder,
    );

    private readonly router = inject(
        Router,
    );

    readonly store = inject(
        AuthStore,
    );

    readonly form = this.fb.nonNullable.group({

        email: [

            '',

            [

                Validators.required,

                Validators.email,

            ],

        ],

        password: [

            '',

            Validators.required,

        ],

    });

    submit(): void {

        if (
            this.form.invalid
        ) {

            this.form.markAllAsTouched();

            return;

        }

        this.store
            .login(
                this.form.getRawValue(),
            )
            .subscribe({

                next: () => {

                    this.router.navigate([
                        '/dashboard',
                    ]);

                },

                error: (
                    error,
                ) => {

                    console.error(
                        error,
                    );

                },

            });

    }

}