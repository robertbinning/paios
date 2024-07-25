import React, { useState } from 'react';
import { startAuthentication, startRegistration } from '@simplewebauthn/browser';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);

  const handleLogin = async () => {
    try {
      const response = await fetch('https://localhost:3080/webauthn/generate-authentication-options', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      const options = data.publicKey;
      const authResp = await startAuthentication(options);

      const verifyResponse = await fetch('https://localhost:3080/webauthn/verify-authentication', {
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

  const handleRegister = async () => {
    try {
      const response = await fetch('https://localhost:3080/webauthn/generate-registration-options', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.status !== 200) {
        throw new Error('Failed to generate registration options');
      }

      const options = await response.json();
      const attResp = await startRegistration(options);

      const verifyResponse = await fetch('https://localhost:3080/webauthn/verify-registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, att_resp: attResp }),
      });

      const { verified } = await verifyResponse.json();
      setMessage(verified ? 'Registration successful' : 'Registration failed');
    } catch (error) {
      console.error(error);
      setMessage('An error occurred during registration');
    }
  };

  return (
    <div>
      <h2>{isRegistering ? 'Register' : 'Login'}</h2>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <button onClick={isRegistering ? handleRegister : handleLogin}>
        {isRegistering ? 'Register' : 'Login'}
      </button>
      <button onClick={() => setIsRegistering(!isRegistering)}>
        {isRegistering ? 'Switch to Login' : 'Switch to Register'}
      </button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Login;