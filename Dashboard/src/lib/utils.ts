// src/lib/utils.ts
import { goto } from '$app/navigation';
import { writable } from 'svelte/store';
// === Platforms (data only, single responsibility) ===
export const platforms = [
    { name: 'amazon', img: "/images/amazon.svg", color: "#db4747cc" },
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
    static setRefreshToken(token: string) {
        localStorage.setItem("refresh", token);
    }

    static clearTokens() {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
    }

    static async refreshAccessToken(): Promise<string | null> {
        const refresh = this.getRefreshToken();
        // console.log("Refresh token in storage:", refresh);

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
            TokenService.setRefreshToken(data.refresh);
            return data.access;
        } catch {
            return null;
        }
    }
}

// === API Service (single responsibility: API requests with automatic token refresh) ===
export class ApiService {
    private static BASE_URL = "http://127.0.0.1:8000";

    private static async fetchWithToken(endpoint: string, options: RequestInit): Promise<Response> {
        const url = `${this.BASE_URL}${endpoint}`;
        let accessToken = TokenService.getAccessToken();

        options.headers = {
            ...options.headers,
            Authorization: `Bearer ${accessToken}`,
        };

        const res = await fetch(url, options);
        return res;
    }

    static async get(endpoint: string) {
        const res = await this.fetchWithToken(endpoint, { method: "GET" });
        if (!res.ok) throw new Error(JSON.stringify(await res.json()));
        return res.json();
    }

    static async post(endpoint: string, body: any, isFormData = false) {
        const headers: Record<string, string> = {};
        if (!isFormData) headers["Content-Type"] = "application/json";

        const res = await this.fetchWithToken(endpoint, {
            method: "POST",
            headers: isFormData ? undefined : headers,
            body: isFormData ? body : JSON.stringify(body),
        });
        if (!res.ok) throw new Error(JSON.stringify(await res.json()));
        return res.json();
    }

    // New method for downloading Excel
    static async downloadExcel(endpoint: string, body: any = null, isPost = false) {
        const options: RequestInit = {
            method: isPost ? "POST" : "GET",
            headers: {
                Authorization: `Bearer ${TokenService.getAccessToken()}`,
            },
        };

        if (isPost) {
            options.body = JSON.stringify(body);
            options.headers = {
                ...options.headers,
                "Content-Type": "application/json",
            };
        }

        const res = await fetch(`${this.BASE_URL}${endpoint}`, options);
        if (!res.ok) throw new Error("Failed to download Excel");

        // Get the blob once
        const blob = await res.blob();

        // Extract filename from Content-Disposition header
        let filename = "file.xlsx";
        const disposition = res.headers.get("Content-Disposition");
        if (disposition) {
            const match = disposition.match(/filename="?(.+?)"?$/);
            if (match?.[1]) filename = decodeURIComponent(match[1]);
        }
        // Trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
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


// === Logout ===
export async function handleLogout() {
    const refreshToken = TokenService.getRefreshToken();

    try {
        if (refreshToken) {

            await ApiService.post('/api/logout', { refresh: refreshToken });
        }

        else {
            console.warn("No refresh token found, clearing tokens anyway");
        }
    } catch (err) {
        console.error('Logout request failed:', err);
    } finally {
        TokenService.clearTokens();
        goto('/login', { replaceState: true });
    }
}


// === Current User Info ===
export async function me() {
    try {
        const response = await ApiService.get("/api/me/");
        localStorage.setItem("userFullName", response.full_name);
        return response;
    } catch (err) {
        console.error("Failed to fetch user info:", err);
        return null;
    }
}


// === Example: Fetch current user lists ===
export async function getAllLists() {
    try {
        const response = await ApiService.get("/api/get_all_lists/");
        return response;
    } catch (err) {
        console.error("Failed to fetch product lists:", err);

        throw err;
    }
}

// === delete a list
export async function deleteList(list_id) {
    try {
        const response = await ApiService.get(`/api/delete_list/${list_id}`);
        return response;
    } catch (err) {
        console.error("Failed to delete list:", err);

        throw err;
    }
}

// === Add new list ===
export async function addListName(list_name: string, platform: string) {
    try {
        const response = await ApiService.post("/api/create_product_list/", {
            list_name,
            platform
        });

        console.log("New list created:", response);
        return response;
    } catch (err) {
        console.error("Error in creating new list:", err);
        throw err;
    }
}


export async function addItemsToList(list_id, file) {
    const accessToken = TokenService.getAccessToken();
    if (!accessToken) throw new Error("No access token available. Please log in again.");

    try {
        const formData = new FormData()
        formData.append("list_id", list_id)
        formData.append("file", file)

        const res = await ApiService.post("/api/add_items_to_product_list/", formData, true);

        if (!res.ok) {
            console.warn('Logout request failed', await res.json());
        } else {
            console.log(await res.json());
        }
    } catch (err) {
        console.error('Error in creating new list :', err);
    }

}


export async function runAudit(product_list_id: string, reAudit: boolean) {
    try {
        console.log(`reAudit is ${reAudit}`)
        const response = await ApiService.post("/api/run_audit/", { product_list_id, reAudit });
        console.log("Run Audit:", response);
        return response;

    } catch (err) {
        console.error("Error in creating new list:", err);
        throw err;
    }
}

export async function stopAudit(task_id: string) {
    try {
        const response = await ApiService.post("/api/stop_audit/", { task_id });
        console.log("Stop Audit:", response);
        return response;

    } catch (err) {
        console.error("Error in creating new list:", err);
        throw err;
    }
}

export function auditSSE(task_id: string, onProgress: (data: any) => void) {
    return new Promise((resolve, reject) => {
        try {
            const url = `http://127.0.0.1:8000/api/tasks_sse/${task_id}/`;
            const eventSource = new EventSource(url);

            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                onProgress(data); // 👈 send updates to caller

                if (data.status === "completed" || data.status === "error") {
                    eventSource.close();
                    resolve(data);
                }
            };

            eventSource.addEventListener("complete", (event) => {
                const data = JSON.parse((event as MessageEvent).data);
                onProgress(data);
                eventSource.close();
                resolve(data);
            });

            eventSource.onerror = (err) => {
                console.error("SSE error:", err);
                eventSource.close();
                reject(err);
            };
        } catch (err) {
            reject(err);
        }
    });
}

// === get all running audits tasks ids ===
export async function auditTaskIDs(task_id: string) {
    try {
        const response = await ApiService.get("/api/all_task_ids/");
        console.log("task ids:", response);
        return response;

    } catch (err) {
        console.error("Error in creating new list:", err);
        throw err;
    }
}

// === Export Audit ===
export async function exportAudit(list_id) {
    try {
        const response = await ApiService.downloadExcel(`/api/export-audit/?product_list_id=${list_id}`);
        console.log("Export Audit:", response);
        return response;

    } catch (err) {
        console.error(`Error in List : ${list_id}`, err);
        throw err;
    }
}
// =======================================================================
export async function getClientIP() {
    try {
        const res = await fetch("https://api.ipify.org?format=json");
        const data = await res.json();
        const publicIP = data.ip;
        return publicIP
    } catch (err) {
        console.error("Failed to get IP:", err);
    }
}


export async function getBackendIP() {
    try {
        const response = await ApiService.get("/api/backend_ip/");
        // console.log("Backend IP:", response);
        return response.public_ip;

    } catch (err) {
        console.error("Error in creating new list:", err);
        throw err;
    }
}
export async function checkCelery() {
    try {
        const response = await ApiService.get("/api/check_celery_service/");
        // console.log("celery:", response);
        return response.status;

    } catch (err) {
        console.error("Error in creating new list:", err);
        throw err;
    }
}


