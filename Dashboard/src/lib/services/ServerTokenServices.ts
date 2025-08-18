// src/services/ServerTokenService.ts
import type { Cookies } from '@sveltejs/kit';

export class ServerTokenService {
    cookies: Cookies;

    constructor(cookies: Cookies) {
        this.cookies = cookies;
    }

    getAccessToken(): string | null {
        return this.cookies.get('access') ?? null;
    }

    getRefreshToken(): string | null {
        return this.cookies.get('refresh') ?? null;
    }

    setAccessToken(token: string) {
        this.cookies.set('access', token, {
            httpOnly: true,
            path: '/',
            secure: false, // set true in production
            sameSite: 'strict',
            maxAge: 60 * 15
        });
    }

    async refreshAccessToken(): Promise<string | null> {
        const refresh = this.getRefreshToken();
        if (!refresh) return null;

        const res = await fetch('http://127.0.0.1:8000/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });

        if (!res.ok) return null;

        const data = await res.json();
        this.setAccessToken(data.access);
        return data.access;
    }
}
