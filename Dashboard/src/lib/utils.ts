// src/lib/utils.ts
import { goto } from '$app/navigation';
import { writable } from 'svelte/store';
// === Platforms (data only, single responsibility) ===
export const platforms = [
    { name: 'amazon', img: "/images/amazon.svg", color: "#ca6b6bff" },
    { name: 'flipkart', img: "/images/flipkart.svg", color: "#c7b72bff" },
    { name: 'myntra', img: "/images/myntra.svg", color: "#9e1a58ff" },
    { name: 'swiggy', img: "/images/swiggy.svg", color: "#ca9025ff" },
    { name: 'zepto', img: "/images/zepto.svg", color: "#471874ff" },
];

// === Internet Connectivity Check ===
export async function checkInternet(): Promise<boolean> {
    try {
        const res = await fetch("https://jsonplaceholder.typicode.com/posts/1", { cache: "no-cache" });
        return res.ok;
    } catch {
        return false;
    }
}

// === Token Service (single responsibility: manage JWT tokens) ===
export class TokenService {
    static getAccessToken(): string | null {
        return localStorage.getItem("access");
    }

    static getRefreshToken(): string | null {
        return localStorage.getItem("refresh");
    }

    static setAccessToken(token: string) {
        localStorage.setItem("access", token);
    }

    static clearTokens() {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
    }

    static async refreshAccessToken(): Promise<string | null> {
        const refresh = this.getRefreshToken();
        if (!refresh) return null;

        try {
            const res = await fetch("http://127.0.0.1:8000/api/token/refresh/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh }),
            });

            if (!res.ok) return null;

            const data = await res.json();
            this.setAccessToken(data.access);
            return data.access;
        } catch {
            return null;
        }
    }
}

// === API Service (single responsibility: API requests with automatic token refresh) ===
export class ApiService {
    private static async fetchWithToken(url: string, options: RequestInit): Promise<Response> {
        let accessToken = TokenService.getAccessToken();
        options.headers = {
            ...options.headers,
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
        };

        let res = await fetch(url, options);

        // Retry once if token expired
        if (res.status === 401) {
            accessToken = await TokenService.refreshAccessToken();
            if (!accessToken) throw new Error("Could not refresh token");

            options.headers = { ...options.headers, Authorization: `Bearer ${accessToken}` };
            res = await fetch(url, options);
        }

        return res;
    }

    static async get(url: string) {
        const res = await this.fetchWithToken(url, { method: "GET" });
        if (!res.ok) throw new Error(JSON.stringify(await res.json()));
        return res.json();
    }

    static async post(url: string, body: any) {
        const res = await this.fetchWithToken(url, {
            method: "POST",
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(JSON.stringify(await res.json()));
        return res.json();
    }
}

// === Auth Utilities (login/logout) ===
export async function loginUser(username: string, password: string) {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) return { error: 'Invalid username or password' };

        const data = await res.json();
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);
        goto('/'); // redirect after login

        return { success: true };
    } catch {
        return { error: 'Something went wrong. Please try again.' };
    }
}



export async function handleLogout() {
    const refreshToken = TokenService.getRefreshToken();

    if (!refreshToken) {
        console.error("No refresh token found");
        TokenService.clearTokens();
        goto('/login', { replaceState: true });
        return;
    }

    try {
        const res = await fetch('http://127.0.0.1:8000/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${TokenService.getAccessToken()}`
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });


        if (!res.ok) {
            console.warn('Logout request failed', await res.json());
        } else {
            console.log(await res.json());
        }
    } catch (err) {
        console.error('Logout request failed:', err);
    } finally {
        TokenService.clearTokens();
        goto('/login', { replaceState: true });
    }
}


// === Example: Fetch current user lists ===
export async function getAllLists() {
    const accessToken = TokenService.getAccessToken();
    if (!accessToken) throw new Error("No access token available. Please log in again.");

    const res = await fetch("http://api/get_all_product_lists/", {
        method: "GET",
        headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
    });

    if (!res.ok) throw new Error(JSON.stringify(await res.json()));
    return res.json();
}


// === Current User Info ===

export async function me() {
    let res = await fetch("http://localhost:8000/api/me/", {
        headers: {
            Authorization: `Bearer ${localStorage.getItem('access')}`
        }
    })
    let response = await res.json()
    localStorage.setItem("userFullName", response.full_name)
    return response
}