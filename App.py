#ACTIVAR ENTORNO VIRTUAL - TODOS LOS COMANDOS SE EJECUTAN EN LA TERMINAL
#1. Set-ExecutionPolicy Unrestricted -Scope Process
#2. .\env\Scripts\activate
#ACTIVAR SERVDOR DE PYTHON
#1. flask run --port 8000
#Nota: Esto se hace dentro de la carpeta donde se encuentra el archivo app.py

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/storage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

@app.route('/admin_panel')
def admin_panel():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)