import React, { useState } from 'react';
import { startAuthentication } from '@simplewebauthn/browser';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  const handleLogin = async () => {
    try {
      const response = await fetch('https://localhost:8000/webauthn/generate-authentication-options', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      const options = data.publicKey; // Ensure the publicKey object is used correctly
      const authResp = await startAuthentication(options);

      const verifyResponse = await fetch('https://localhost:8000/webauthn/verify-authentication', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, auth_resp: authResp }),
      });

      const { verified } = await verifyResponse.json();
      setMessage(verified ? 'Login successful' : 'Login failed');
    } catch (error) {
      console.error(error);
      setMessage('An error occurred during login');
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <button onClick={handleLogin}>Login</button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Login;
