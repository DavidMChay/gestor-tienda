#ACTIVAR ENTORNO VIRTUAL - TODOS LOS COMANDOS SE EJECUTAN EN LA TERMINAL
#1. Set-ExecutionPolicy Unrestricted -Scope Process
#2. .\env\Scripts\activate
#ACTIVAR SERVDOR DE PYTHON
#1. flask run --port 8000
#Nota: Esto se hace dentro de la carpeta donde se encuentra el archivo app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
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
    categoria = db.Column(db.String)

class Cliente(db.Model):
    __tablename__ = 'Clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    telefono = db.Column(db.String)
    direccion = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    
class Pedido(db.Model):
    __tablename__ = 'Pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('Clientes.id'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=db.func.current_timestamp())
    total = db.Column(db.Float, nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('pedidos', lazy=True))
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)
    
class DetallePedido(db.Model):
    __tablename__ = 'DetallesPedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('Pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('Productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    producto = db.relationship('Producto', backref=db.backref('detalles', lazy=True))

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
    productos_recientes = Producto.query.order_by(Producto.fecha_agregado.desc()).limit(4).all()
    return render_template('main.html', productos_recientes=productos_recientes)

@app.route('/home')
def home():
    return redirect(url_for('index'))

@app.route('/productos')
def productos():
    productos = Producto.query.all() 
    return render_template('products.html', productos=productos)

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

@app.route('/perfil')
def user_perfil():
    if 'cliente_id' not in session:
        return redirect(url_for('user_login'))
    return render_template('miperfil.html')

@app.route('/agregar_al_carrito/<int:producto_id>')
def agregar_al_carrito(producto_id):
    if 'cliente_id' not in session:
        flash('Por favor inicia sesión para agregar productos al carrito.')
        return redirect(url_for('user_login'))

    cliente_id = session['cliente_id']
    producto = Producto.query.get_or_404(producto_id)
    pedido = Pedido.query.filter_by(cliente_id=cliente_id, total=0).first()

    if not pedido:
        pedido = Pedido(cliente_id=cliente_id, total=0)
        db.session.add(pedido)
        db.session.commit()

    detalle = DetallePedido.query.filter_by(pedido_id=pedido.id, producto_id=producto_id).first()
    if detalle:
        detalle.cantidad += 1
    else:
        detalle = DetallePedido(pedido_id=pedido.id, producto_id=producto_id, cantidad=1, precio_unitario=producto.precio)
        db.session.add(detalle)

    db.session.commit()
    flash('Producto agregado al carrito.')
    return redirect(url_for('productos'))


@app.route('/mi-carrito')
def user_carrito():
    if 'cliente_id' not in session:
        return redirect(url_for('user_login'))

    cliente_id = session['cliente_id']
    pedido = Pedido.query.filter_by(cliente_id=cliente_id, total=0).first()
    detalles_pedido = []

    if pedido:
        detalles_pedido = DetallePedido.query.filter_by(pedido_id=pedido.id).all()

    return render_template('orders.html', detalles_pedido=detalles_pedido)

@app.route('/eliminar_del_carrito/<int:detalle_id>')
def eliminar_del_carrito(detalle_id):
    if 'cliente_id' not in session:
        flash('Por favor inicia sesión para eliminar productos del carrito.')
        return redirect(url_for('user_login'))

    detalle = DetallePedido.query.get_or_404(detalle_id)
    db.session.delete(detalle)
    db.session.commit()
    flash('Producto eliminado del carrito.')
    return redirect(url_for('user_carrito'))


@app.route('/admin/panel/gestionar_productos')
def admin_listar_productos():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    productos = Producto.query.all()
    return render_template('adminlspd.html', productos=productos)

@app.route('/admin/panel/editar/<int:producto_id>', methods=['GET', 'POST'])
def admin_editar_producto(producto_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    producto = Producto.query.get_or_404(producto_id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio = request.form['precio']
        producto.stock = request.form['stock']
        producto.categoria = request.form['categoria']

        imagen = request.files['imagen']
        if imagen:
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            producto.imagen = 'uploads/' + filename
        
        db.session.commit()
        flash('Producto actualizado correctamente.')
        return redirect(url_for('admin_listar_productos'))
    return render_template('admin_edit_product.html', producto=producto)

@app.route('/admin/panel/eliminar/<int:producto_id>', methods=['POST'])
def admin_eliminar_producto(producto_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente.')
    return redirect(url_for('admin_listar_productos'))

# SOLICITUDES
@app.route('/registro', methods=['GET', 'POST'])
def user_registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        password = request.form['password']
        
        # Verificar si el email ya está registrado
        cliente_existente = Cliente.query.filter_by(email=email).first()
        if cliente_existente:
            flash('El email ya está registrado.')
            return redirect(url_for('user_registro'))
        
        # Crear nuevo cliente
        nuevo_cliente = Cliente(
            nombre=nombre, 
            email=email, 
            telefono=telefono, 
            direccion=direccion, 
            password=generate_password_hash(password)
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('user_login'))
    
    return render_template('userregistro.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cliente = Cliente.query.filter_by(email=email).first()
        if cliente and check_password_hash(cliente.password, password):
            session['cliente_id'] = cliente.id
            return redirect(url_for('user_perfil'))
        else:
            flash('Correo o contraseña incorrectos')
    return render_template('userlogin.html')


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
        categoria = request.form['categoria']

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
        nuevo_producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, stock=stock, imagen=imagen_path, categoria=categoria)
        db.session.add(nuevo_producto)
        db.session.commit()
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