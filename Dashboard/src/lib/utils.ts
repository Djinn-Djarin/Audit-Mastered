export let platform = [
       { name: 'amazon', img: "/images/amazon.svg", color: "#ca6b6bff" },
       { name: 'flipkart', img: "/images/flipkart.svg", color: "#c7b72bff" },
       { name: 'myntra', img: "/images/myntra.svg", color: "#9e1a58ff" },
       { name: 'swiggy', img: "/images/swiggy.svg", color: "#ca9025ff" },
       { name: 'zepto', img: "/images/zepto.svg", color: "#471874ff" },

]


export async function checkInternet() {
       try {
              const response = await fetch("https://jsonplaceholder.typicode.com/posts/1", {
                     method: "GET",
                     cache: "no-cache",
              });
              return response.ok;
       } catch (error) {
              return false;
       }
}

async function refreshToken() {
    const refresh = localStorage.getItem("refresh");

    if (!refresh) {
        console.error("No refresh token available. Please log in again.");
        return null;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/api/token/refresh/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh }),
        });

        if (!res.ok) {
            console.error("Failed to refresh token");
            return null;
        }

        const data = await res.json();
        localStorage.setItem("access", data.access); // save new access token
        return data.access;
    } catch (err) {
        console.error("Error refreshing token:", err);
        return null;
    }
}


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

    static async refreshAccessToken(): Promise<string | null> {
        const refresh = this.getRefreshToken();
        if (!refresh) {
            console.error("No refresh token available. Please log in again.");
            return null;
        }

        try {
            const res = await fetch("http://127.0.0.1:8000/api/token/refresh/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh }),
            });

            if (!res.ok) {
                console.error("Failed to refresh token");
                return null;
            }

            const data = await res.json();
            this.setAccessToken(data.access);
            return data.access;
        } catch (err) {
            console.error("Error refreshing token:", err);
            return null;
        }
    }
}

export class ApiService {
    private static async fetchWithToken(
        url: string,
        options: RequestInit
    ): Promise<Response> {
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

            options.headers = {
                ...options.headers,
                Authorization: `Bearer ${accessToken}`,
            };
            res = await fetch(url, options);
        }

        return res;
    }

    static async post(url: string, body: any) {
        const res = await this.fetchWithToken(url, {
            method: "POST",
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(JSON.stringify(errorData));
        }

        return res.json();
    }

    static async get(url: string) {
        const res = await this.fetchWithToken(url, { method: "GET" });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(JSON.stringify(errorData));
        }

        return res.json();
    }
}



// === login user ===
import { goto } from '$app/navigation';

export async function loginUser(username, password) {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            return { error: 'Invalid username or password' };
        }

        const data = await res.json();

        // Save tokens in localStorage
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);

        // Redirect to dashboard or protected page
        goto('/');

        return { success: true };
    } catch (err) {
        return { error: 'Something went wrong. Please try again.' };
    }
}
export async function handleLogout() {
        // Clear tokens
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");

        await fetch('http://127.0.0.1:8000/api/logout', { method: 'POST' });
        // Redirect to login page
        goto("/login", { replaceState: true });
    }

// === get all lists of current user ===
export async function getAllLists() {
    const accessToken = TokenService.getAccessToken();
    if (!accessToken) {
        throw new Error("No access token available. Please log in again.");
    }

    const res = await fetch("http://api/get_all_product_lists/", {
        method: "GET",
        headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
        },
    });     

    if (!res.ok) {
        const errorData = await res.json();
        throw new Error(JSON.stringify(errorData));
    }
    return res.json();
}