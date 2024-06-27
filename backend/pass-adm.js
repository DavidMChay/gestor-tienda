// script para cifrar una contraseña
const bcrypt = require('bcrypt');

const saltRounds = 10;
const plainTextPassword = '69Opichen!';

bcrypt.hash(plainTextPassword, saltRounds, function(err, hash) {
  if (err) {
    console.error('Error hashing password:', err);
  } else {
    console.log('Hashed password:', hash);
    // Aquí puedes copiar el hash generado y usarlo para insertar en la base de datos
  }
});
