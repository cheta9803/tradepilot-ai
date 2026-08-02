import {
    Injectable,
    computed,
    inject,
    signal,
} from '@angular/core';

import {
    finalize,
    switchMap,
    tap,
} from 'rxjs';

import {
    AuthService,
} from '../services/auth.service';

import {
    LoginRequest,
} from '../models/login-request.model';

import {
    RegisterRequest,
} from '../models/register-request.model';

import {
    User,
} from '../models/user.model';

import {
    AuthStorage,
} from '../utils/auth-storage';

@Injectable({
    providedIn: 'root',
})
export class AuthStore {

    private readonly authService = inject(
        AuthService,
    );

    private readonly currentUserSignal =
        signal<User | null>(
            null,
        );

    readonly currentUser = computed(
        () => this.currentUserSignal(),
    );

    readonly isAuthenticated = computed(
        () => this.currentUserSignal() !== null,
    );

    readonly loading = signal(
        false,
    );

    login(
        request: LoginRequest,
    ) {

        this.loading.set(
            true,
        );

        return this.authService
            .login(
                request,
            )
            .pipe(

                tap(
                    (token) => {

                        AuthStorage.saveToken(
                            token.access_token,
                        );

                    },
                ),

                switchMap(
                    () => this.authService.me(),
                ),

                tap(
                    (user) => {

                        this.currentUserSignal.set(
                            user,
                        );

                    },
                ),

                finalize(
                    () => {

                        this.loading.set(
                            false,
                        );

                    },
                ),

            );

    }

    register(
        request: RegisterRequest,
    ) {

        this.loading.set(
            true,
        );

        return this.authService
            .register(
                request,
            )
            .pipe(

                finalize(
                    () => {

                        this.loading.set(
                            false,
                        );

                    },
                ),

            );

    }

    restoreSession() {

        const token =
            AuthStorage.getToken();

        if (!token) {

            console.log(
                'No token found.',
            );

            return;

        }

        console.log(
            'Restoring session...',
        );

        this.authService
            .me()
            .subscribe({

                next: (user) => {

                    console.log(
                        'Session restored',
                        user,
                    );

                    this.currentUserSignal.set(
                        user,
                    );

                },

                error: () => {

                    console.log(
                        'Session restore failed.',
                    );

                    this.logout();

                },

            });

    }

    logout(): void {

        AuthStorage.clear();

        this.currentUserSignal.set(
            null,
        );

    }

}