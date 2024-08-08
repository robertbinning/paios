import { fetchUtils } from 'react-admin';

export const apiBase = import.meta.env.VITE_JSON_SERVER_URL || 'http://localhost:3080/api/v1';

export const httpClient = (url: string, options: any = {}) => {
    if (!options.headers) {
      options.headers = new Headers({ Accept: 'application/json' });
    }
    
    options.credentials = 'include'; // This is important for sending cookies
    return fetchUtils.fetchJson(url, options);
  }