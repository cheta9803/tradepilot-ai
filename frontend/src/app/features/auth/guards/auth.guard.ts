import {
    inject,
} from '@angular/core';

import {
    CanActivateFn,
    Router,
} from '@angular/router';

import {
    AuthStorage,
} from '../utils/auth-storage';

export const authGuard: CanActivateFn = () => {

    const router = inject(
        Router,
    );

    if (AuthStorage.hasToken()) {

        return true;

    }

    return router.createUrlTree([
        '/login',
    ]);

};