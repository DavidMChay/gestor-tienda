// src/pages/Admin.js
import React, { useState } from 'react';
import axios from 'axios';
import styles from './Admin.module.css';

const Admin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); // Reset error message
    try {
      const response = await axios.post('http://localhost:5000/api/admin/login', { email, contrasena: password });
      if (response.data.message === 'success') {
        setIsLoggedIn(true);
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Panel de Administradores</h1>
      {isLoggedIn ? (
        <div>
          <h2>Welcome, Admin!</h2>
          {/* Aquí puedes añadir las opciones del panel de administradores */}
        </div>
      ) : (
        <form onSubmit={handleLogin}>
          <div>
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit">Login</button>
        </form>
      )}
    </div>
  );
};

export default Admin;
