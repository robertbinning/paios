import React, { useState } from 'react';
import { startAuthentication, startRegistration } from '@simplewebauthn/browser';
import { authProvider } from './authProvider';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);

  const handleLogin = async () => {
    try {
        console.debug("Generating authentication options");
        const response = await fetch('http://localhost:3080/api/v1/webauthn/generate-authentication-options', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        });

        const res = await response.json();
        const options = JSON.parse(res?.options)
        console.debug("Starting authentication");
        const authResp = await startAuthentication(options);

        console.debug("Verifying authentication response");
        const token = localStorage.getItem('auth_token');
        console.log(localStorage.getItem('auth_token')); // Added this line to log the token
        const verifyResponse = await fetch('http://localhost:3080/api/v1/webauthn/verify-authentication', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ email, auth_resp: authResp, challenge: options.challenge }),
        });

        const { message, token: newToken } = await verifyResponse.json();
        if (message === "Success" && newToken) {
            console.debug("Login successful, storing token");
            setMessage('Login successful');
            localStorage.setItem('auth_token', newToken); // Updated to use newToken
            // Trigger authProvider login
            await authProvider.login({ username: email });
            // Redirect to the admin dashboard
            window.location.href = '/';
        } else {
            console.warn("Login failed"); // Changed from console.warning to console.warn
            setMessage('Login failed');
        }
    } catch (error) {
        console.error("An error occurred during login:", error);
        setMessage('An error occurred during login');
    }
  };

  const handleRegister = async () => {
    try {
      const response = await fetch('http://localhost:3080/api/v1/webauthn/generate-registration-options', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.status !== 200) {
        throw new Error('Failed to generate registration options');
      }

      const res = await response.json();
      const options = JSON.parse(res?.options)
    
      const attResp = await startRegistration(options);

    
      const verifyResponse = await fetch('http://localhost:3080/api/v1/webauthn/verify-registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            email, 
            att_resp: attResp,
            challenge: options.challenge,
            user_id: options.user.id
         }),
      });

      const { message } = await verifyResponse.json();
      setMessage(message === "Success" ? 'Registration successful' : 'Registration failed');
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