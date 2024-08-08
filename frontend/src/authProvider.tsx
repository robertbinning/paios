import { AuthProvider } from "react-admin";
import { apiBase, httpClient } from "./apiBackend";

export const authProvider: AuthProvider = {
    login: async ({ username }) => {
        // The actual login is handled by the WebAuthn process
        // This method is called after successful WebAuthn authentication
        return Promise.resolve();
    },
    logout: async () => {
        const response = await httpClient(`${apiBase}/auth/logout`, {
            method: 'POST',
            credentials: 'include',
        });
        if (response.status < 200 || response.status >= 300) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return Promise.resolve();
    },
    checkError: ({ status }) => {
        if (status === 401 || status === 403) {
            return Promise.reject();
        }
        return Promise.resolve();
    },
    checkAuth: async () => {
        const response = await httpClient(`${apiBase}/auth/check`, {
            method: 'GET',
            credentials: 'include', // This is important for sending cookies
        });
        if (response.status < 200 || response.status >= 300) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return Promise.resolve();
    },
    getPermissions: () => Promise.resolve(),
};