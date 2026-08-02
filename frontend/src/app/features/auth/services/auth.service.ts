import {
    inject,
    Injectable,
} from '@angular/core';

import {
    HttpClient,
} from '@angular/common/http';

import {
    Observable,
} from 'rxjs';

import {
    environment,
} from '../../../../environments/environment';

import {
    LoginRequest,
} from '../models/login-request.model';

import {
    RegisterRequest,
} from '../models/register-request.model';

import {
    Token,
} from '../models/token.model';

import {
    User,
} from '../models/user.model';

@Injectable({
    providedIn: 'root',
})
export class AuthService {

    private readonly http = inject(
        HttpClient,
    );

    private readonly apiUrl =
        `${environment.apiUrl}/auth`;

    login(
        request: LoginRequest,
    ): Observable<Token> {

        return this.http.post<Token>(
            `${this.apiUrl}/login`,
            request,
        );

    }

    register(
        request: RegisterRequest,
    ): Observable<User> {

        return this.http.post<User>(
            `${this.apiUrl}/register`,
            request,
        );

    }

    me(): Observable<User> {

        return this.http.get<User>(
            `${this.apiUrl}/me`,
        );

    }

}