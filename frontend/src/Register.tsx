import React, { useState } from 'react';
import { startRegistration } from '@simplewebauthn/browser';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

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
      <h2>Register</h2>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <button onClick={handleRegister}>Register</button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Register;
