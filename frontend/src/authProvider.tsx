import { AuthProvider } from "react-admin";
import { apiBase, httpClient } from "./apiBackend";

export const authProvider: AuthProvider = {
    login: async ({ username }) => {
        console.debug("Login called");
        // The actual login is handled by the WebAuthn process
        // This method is called after successful WebAuthn authentication
        // The token should be stored in localStorage after successful authentication
        return Promise.resolve();
    },
    logout: () => {
        console.debug("Logout called");
        localStorage.removeItem('auth_token');
        return Promise.resolve();
    },
    checkError: ({ status }) => {
        console.debug(`checkError called with status: ${status}`);
        if (status === 401 || status === 403) {
            localStorage.removeItem('auth_token');
            return Promise.reject();
        }
        return Promise.resolve();
    },
    checkAuth: async () => {
        console.debug("checkAuth called");
        const token = localStorage.getItem('auth_token');
        if (!token) {
            console.warn("No token found in localStorage");
            return Promise.reject();
        }
        try {
            const response = await fetch(`${apiBase}/auth/check`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });
            console.debug(`Auth check response status: ${response.status}`);
            if (response.status === 200) {
                return Promise.resolve();
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('auth_token');
            return Promise.reject();
        }
    },
    getPermissions: () => Promise.resolve(),
};