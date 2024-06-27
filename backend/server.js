// backend/server.js
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const apiRoutes = require('./routes/api');

const app = express();
const PORT = process.env.PORT || 5000;

// Configuración de CORS
app.use(cors({
  origin: 'http://localhost:3000',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Middleware
app.use(bodyParser.json());
app.use('/api', apiRoutes);

// Iniciar el servidor
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

// Conexión a la base de datos
const db = new sqlite3.Database('./db/storage.db', (err) => {
  if (err) {
    console.error('Error opening database', err.message);
  } else {
    console.log('Connected to the SQLite database.');
  }
});

module.exports = db;
