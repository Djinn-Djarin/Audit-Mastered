// src/lib/utils.ts
import { goto } from '$app/navigation';



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


// === Token Service (cookie-based, no localStorage) ===
export class TokenService {
  
    static async refreshAccessToken(): Promise<boolean> {
        try {
            const res = await fetch(`/api/token/refresh/`, {
                method: "POST",
                credentials: "include", // send cookies
            });

            return res.ok; // Django updates cookies if refresh works
        } catch {
            return false;
        }
    }

    /**
     * Clear tokens by calling logout endpoint (which deletes cookies).
     */
    static async clearTokens(): Promise<void> {
        try {
            await fetch(`/api/logout/`, {
                method: "POST",
                credentials: "include",
            });
        } catch {
            // ignore errors
        }
    }
     
}


// === API Service (single responsibility: API requests with automatic token refresh) ===
// === API Service (always send cookies) ===
export class ApiService {
    private static async fetchWithAuth(endpoint: string, options: RequestInit): Promise<Response> {
        const url = `${endpoint}`;

        const res = await fetch(url, {
            ...options,
            credentials: "include", // important: send Django cookies
        });

        // If 401 Unauthorized, try refresh then retry
        if (res.status === 401) {
            const refreshed = await TokenService.refreshAccessToken();
            if (refreshed) {
                return fetch(url, {
                    ...options,
                    credentials: "include",
                });
            }
        }

        return res;
    }

    static async get(endpoint: string) {
        const res = await this.fetchWithAuth(endpoint, { method: "GET" });
        if (!res.ok) throw new Error(JSON.stringify(await res.json()));
        return res.json();
    }

    static async post(endpoint: string, body: any, isFormData = false) {
        const headers: Record<string, string> = {};
        if (!isFormData) headers["Content-Type"] = "application/json";

        const res = await this.fetchWithAuth(endpoint, {
            method: "POST",
            headers: isFormData ? undefined : headers,
            body: isFormData ? body : JSON.stringify(body),
        });
        if (!res.ok) throw new Error(JSON.stringify(await res.json()));
        return res.json();
    }

    static async downloadExcel(endpoint: string, body: any = null, isPost = false) {
        const options: RequestInit = {
            method: isPost ? "POST" : "GET",
            credentials: "include",
        };

        if (isPost) {
            options.body = JSON.stringify(body);
            options.headers = { "Content-Type": "application/json" };
        }

        const res = await this.fetchWithAuth(endpoint, options);
        if (!res.ok) throw new Error("Failed to download Excel");

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


// === Auth Utilities (login) ===
export async function loginUser(username: string, password: string) {
    try {
        const res = await fetch(`/api/token/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
            credentials: "include", // send & receive cookies
        });

        if (!res.ok) {
            return { error: "Invalid username or password" };
        }

        // At this point, Django has already set the cookies
        // Optionally you can fetch the current user
        try {
            await me(); // assuming `me()` calls /api/me/ with credentials: 'include'
        } catch {
            // ignore for now, or handle if you want to show user profile immediately
        }

        // Redirect to home after successful login
        goto("/");

        return { success: true };
    } catch (err) {
        return { error: "Something went wrong. Please try again." };
    }
}



// === Logout ===
export async function handleLogout() {
    try {
        // Django will read the refresh token from HttpOnly cookie
           await TokenService.clearTokens();
    } catch (err) {
        console.error("Logout request failed:", err);
    } finally {
    
        goto("/login", { replaceState: true });
    }
}



// === Current User Info ===
export async function me() {
    try {
        const response = await ApiService.get("/api/me/");
        // If you need the name in memory, return it
        localStorage.setItem("userFullName",response.full_name)
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

export async function addItemsToList(list_id: string, file: File) {
    try {
        const formData = new FormData();
        formData.append("list_id", list_id);
        formData.append("file", file);

        // ApiService.post already handles auth & JSON parsing
        const res = await ApiService.post("/api/add_items_to_product_list/", formData, true);

        return res; // parsed JSON response
    } catch (err) {
        // ApiService throws an Error with message = JSON.stringify(errorResponse)
        try {
            const parsed = JSON.parse(err.message);
            console.error(parsed);
            return parsed;
        } catch {
            console.error("Unexpected error:", err);
            return { error: "Unexpected error" };
        }
    }
}





export async function runAudit(product_list_id: string, reAudit: boolean) {
    try {
        console.log(`reAudit is ${reAudit}`)
        const response = await ApiService.post("/api/run_audit/", { product_list_id, reAudit });
        console.log("%c Start Audit:", "background: green; color: white; font-weight: bold; padding: 4px; border-radius: 4px;");
        console.log(response);

        return response;

    } catch (err) {
        console.error("Error in creating new list:", err);
        throw err;
    }
}

export async function stopAudit(task_id: string) {
    try {
        const response = await ApiService.post("/api/stop_audit/", { task_id });
        console.log("%c Stop Audit:", "background: red; color: white; font-weight: bold; padding: 4px; border-radius: 4px;");
        console.log(response);

        return response;

    } catch (err) {
        console.error("Error in creating new list:", err);
        throw err;
    }
}

export function auditSSE(task_id: string, onProgress: (data: any) => void) {
    return new Promise((resolve, reject) => {
        try {
            console.log(task_id, "in sse")
            const url = `/api/tasks_sse/${task_id}/`;
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
    }
}


