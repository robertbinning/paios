import { AuthProvider } from 'react-admin';
import { startAuthentication } from '@simplewebauthn/browser';

export const authProvider: AuthProvider = {
  login: async ({ username }) => {
    try {
      const response = await fetch('https://localhost:3080/api/v1/webauthn/generate-authentication-options', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: username }),
      });

      const data = await response.json();
      const options = data.publicKey; // Ensure the publicKey object is used correctly
      const authResp = await startAuthentication(options);

      const verifyResponse = await fetch('https://localhost:3080/api/v1/webauthn/verify-authentication', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: username, auth_resp: authResp }),
      });

      const { verified } = await verifyResponse.json();

      if (verified) {
        localStorage.setItem('username', username);
        return Promise.resolve();
      } else {
        return Promise.reject(new Error('Authentication failed'));
      }
    } catch (error) {
      return Promise.reject(error);
    }
  },
  logout: () => {
    localStorage.removeItem('username');
    return Promise.resolve();
  },
  checkError: ({ status }: { status: number }) => {
    if (status === 401 || status === 403) {
      localStorage.removeItem('username');
      return Promise.reject();
    }
    return Promise.resolve();
  },
  checkAuth: () => {
    return localStorage.getItem('username')
      ? Promise.resolve()
      : Promise.reject();
  },
  getPermissions: () => Promise.resolve(),
};
