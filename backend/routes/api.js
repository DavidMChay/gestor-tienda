// backend/routes/api.js
const express = require('express');
const router = express.Router();
const db = require('../server');

// Endpoint para obtener todos los productos
router.get('/products', (req, res) => {
  const sql = 'SELECT * FROM products';
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
  const { name, price, stock } = req.body;
  const sql = 'INSERT INTO products (name, price, stock) VALUES (?, ?, ?)';
  const params = [name, price, stock];
  db.run(sql, params, function (err) {
    if (err) {
      res.status(400).json({ "error": err.message });
      return;
    }
    res.json({
      "message": "success",
      "data": { id: this.lastID, name, price, stock }
    });
  });
});

// Otros endpoints según sea necesario...

module.exports = router;
