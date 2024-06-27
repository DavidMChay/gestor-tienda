// backend/server.js
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const apiRoutes = require('./routes/api');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use('/api', apiRoutes);

// Iniciar el servidor
app.listen(PORT, () => {
  console.log(`Servidor corriendo en el puerto: ${PORT}`);
});

// Conexión a la base de datos
const db = new sqlite3.Database('./db/storage.db', (err) => {
  if (err) {
    console.error('Error al abrir la base de datos.', err.message);
  } else {
    console.log('Conectado a la base de datos correctamente.');
  }
});

module.exports = db;
