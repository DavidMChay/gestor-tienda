// backend/routes/api.js
const express = require('express');
const router = express.Router();
const db = require('../server');
const bcrypt = require('bcrypt');

// Endpoint para obtener todos los productos
router.get('/products', (req, res) => {
  const sql = 'SELECT * FROM Productos';
  db.all(sql, [], (err, rows) => {
    if (err) {
      res.status(400).json({ "error": err.message });
      return;
    }
    res.json({
      "message": "success",
      "data": rows
    });
  });
});

// Endpoint para agregar un nuevo producto
router.post('/products', (req, res) => {
  const { nombre, descripcion, precio, stock } = req.body;
  const sql = 'INSERT INTO Productos (nombre, descripcion, precio, stock) VALUES (?, ?, ?, ?)';
  const params = [nombre, descripcion, precio, stock];
  db.run(sql, params, function (err) {
    if (err) {
      res.status(400).json({ "error": err.message });
      return;
    }
    res.json({
      "message": "success",
      "data": { id: this.lastID, nombre, descripcion, precio, stock }
    });
  });
});

// Endpoint para verificar administrador
router.post('/admin/login', (req, res) => {
  const { email, contrasena } = req.body;
  const sql = 'SELECT * FROM Administradores WHERE email = ?';
  const params = [email];
  db.get(sql, params, (err, row) => {
    if (err) {
      res.status(400).json({ "error": err.message });
      return;
    }
    if (row) {
      console.log('Usuario encontrado:', row);
      // Comprobar la contraseña
      bcrypt.compare(contrasena, row.contrasena, (err, result) => {
        if (err) {
          console.error('Error comparing passwords:', err);
          res.status(500).json({ "message": "Server error" });
          return;
        }
        if (result) {
          console.log('Contraseña correcta');
          res.json({
            "message": "success",
            "data": row
          });
        } else {
          console.log('Contraseña incorrecta');
          res.status(401).json({ "message": "Invalid credentials" });
        }
      });
    } else {
      console.log('Usuario no encontrado');
      res.status(401).json({ "message": "Invalid credentials" });
    }
  });
});


// Otros endpoints según sea necesario...

module.exports = router;
