// src/components/Header.js
import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header>
      <nav>
        <ul>
          <li><Link to="/">Inicio</Link></li>
          <li><Link to="/products">Productos</Link></li>
          <li><Link to="/orders">Pedidos</Link></li>
          <li><Link to="/admin">Panel Admin.</Link></li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
