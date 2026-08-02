const ACCESS_TOKEN_KEY =
    'access_token';

export class AuthStorage {

    static saveToken(
        token: string,
    ): void {

        localStorage.setItem(
            ACCESS_TOKEN_KEY,
            token,
        );

    }

    static getToken():
        string | null {

        return localStorage.getItem(
            ACCESS_TOKEN_KEY,
        );

    }

    static hasToken():
        boolean {

        return !!localStorage.getItem(
            ACCESS_TOKEN_KEY,
        );

    }

    static removeToken(): void {

        localStorage.removeItem(
            ACCESS_TOKEN_KEY,
        );

    }

    static clear(): void {

        localStorage.removeItem(
            ACCESS_TOKEN_KEY,
        );

    }

}