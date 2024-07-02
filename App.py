#ACTIVAR ENTORNO VIRTUAL - TODOS LOS COMANDOS SE EJECUTAN EN LA TERMINAL
#1. Set-ExecutionPolicy Unrestricted -Scope Process
#2. .\env\Scripts\activate
#ACTIVAR SERVDOR DE PYTHON
#1. flask run --port 8000
#Nota: Esto se hace dentro de la carpeta donde se encuentra el archivo app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

basedir = os.path.abspath(os.path.dirname(__file__))

# Crear la carpeta si no existe
if not os.path.exists(os.path.join(basedir, 'database')):
    os.makedirs(os.path.join(basedir, 'database'))

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'storage.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
db = SQLAlchemy(app)

# --MODELOS DE LAS TABLAS DE LA BASE DE DATOS--
class Producto(db.Model):
    __tablename__ = 'Productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    descripcion = db.Column(db.String)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    fecha_agregado = db.Column(db.DateTime, default=db.func.current_timestamp())
    imagen = db.Column(db.String) 

class Cliente(db.Model):
    __tablename__ = 'Clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    telefono = db.Column(db.String)
    direccion = db.Column(db.String)

class Pedido(db.Model):
    __tablename__ = 'Pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('Clientes.id'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=db.func.current_timestamp())
    total = db.Column(db.Float, nullable=False)

class DetallePedido(db.Model):
    __tablename__ = 'DetallesPedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('Pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('Productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

class Auditoria(db.Model):
    __tablename__ = 'Auditoria'
    id = db.Column(db.Integer, primary_key=True)
    entidad = db.Column(db.String, nullable=False)
    operacion = db.Column(db.String, nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    descripcion = db.Column(db.String)

class Administrador(db.Model):
    __tablename__ = 'Administradores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    contrasena = db.Column(db.String, nullable=False)

# --DEFINICION DE LAS RUTAS
# ENDPOINTS PAGINAS
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/home')
def home():
    return render_template('main.html')

@app.route('/productos')
def productos():
    return render_template('products.html')

@app.route('/pedidos')
def pedidos():
    return render_template('orders.html')

@app.route('/admin/panel')
def admin_panel():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('paneladmin.html')

@app.route('/admin/panel/agregar')
def admin_agregar():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('adminagregarprod.html')


# SOLICITUDES

@app.route('/admin/panel/agregar', methods=['GET', 'POST'])
def admin_agregar_producto():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stock']
        imagen = request.files['imagen']

        # Verificar si el producto ya existe
        producto_existente = Producto.query.filter_by(nombre=nombre).first()
        if producto_existente:
            flash('El producto ya existe.')
            return redirect(url_for('admin_agregar_producto'))

        # Guardar la imagen en el servidor
        if imagen:
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen_path = 'uploads/' + filename
        else:
            imagen_path = None

        # Agregar nuevo producto a la base de datos
        nuevo_producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, stock=stock, imagen=imagen_path)
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado exitosamente.')
        return redirect(url_for('admin_panel'))
    return render_template('adminagregarprod.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Administrador.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.contrasena, password):
            session['admin_id'] = admin.id
            return redirect(url_for('admin_panel'))
        else:
            flash('Correo o contraseña incorrectos')
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)