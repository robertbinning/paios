import { fetchUtils } from 'react-admin';

export const apiBase = import.meta.env.VITE_JSON_SERVER_URL || 'http://localhost:3080/api/v1';

export const httpClient = (url: string, options: any = {}) => {
    if (!options.headers) {
        options.headers = new Headers({ Accept: 'application/json' });
    }
    const token = localStorage.getItem('auth_token');
    if (token) {
        options.headers.set('Authorization', `Bearer ${token}`);
    }
    return fetchUtils.fetchJson(url, options).catch(error => {
        if (error.status === 401) {
            localStorage.removeItem('auth_token');
        }
        throw error;
    });
}