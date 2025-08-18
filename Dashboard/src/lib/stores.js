import { writable } from 'svelte/store';
import jwtDecode from 'jwt-decode';

export const token = writable(null);
export const user = writable(null);

export function login(jwt) {
    token.set(jwt);
    try {
        user.set(jwtDecode(jwt)); // decode user info from token
    } catch (err) {
        console.error("Invalid token", err);
        logout();
    }
    localStorage.setItem("jwt", jwt);
}

export function logout() {
    token.set(null);
    user.set(null);
    localStorage.removeItem("jwt");
}

export function restoreSession() {
    const saved = localStorage.getItem("jwt");
    if (saved) login(saved);
}
