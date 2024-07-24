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
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'El_ZorrogayC0m3hombres!')

# Información de conexión proporcionada por Supabase
user = "postgres.tidxgrbtrrqbuxnkmwji"
password = "ZorroPuto69!"  # Reemplaza con la contraseña correcta
host = "aws-0-us-west-1.pooler.supabase.com"
port = "6543"
dbname = "postgres"

# Crear la URL de conexión
DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
db = SQLAlchemy(app)

# Configuración de la sesión
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Solo para HTTPS, puedes cambiar a False si estás desarrollando localmente
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# --MODELOS DE LAS TABLAS DE LA BASE DE DATOS--
class Producto(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    details = db.Column(db.String)
    unit_price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    added_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    picture = db.Column(db.String)
    category = db.Column(db.String, nullable=False)
    objects = db.relationship('DetallePedido', backref='products', lazy=True)

class Cliente(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String)
    address = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    
class Pedido(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    total = db.Column(db.Float, nullable=False)
    customer = db.relationship('Cliente', backref=db.backref('orders', lazy=True))
    
class DetallePedido(db.Model):
    __tablename__ = 'ordersdetails'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    product = db.relationship('Producto', backref=db.backref('ordersDetails', lazy=True))

class Auditoria(db.Model):
    __tablename__ = 'auditory'
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String, nullable=False)
    operation = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    details = db.Column(db.String)

class Administrador(db.Model):
    __tablename__ = 'administradores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

class MyCar(db.Model):
    __tablename__ = 'mycar'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    product = db.relationship('Producto', backref=db.backref('mycar', lazy=True))

if __name__ == '__main__':
    app.run(debug=True)
# --DEFINICION DE LAS RUTAS
# ENDPOINTS PAGINAS
@app.route('/')
def index():
    productos_recientes = Producto.query.order_by(Producto.added_date.desc()).limit(4).all()
    return render_template('main.html', productos_recientes=productos_recientes)

@app.route('/home')
def home():
    return redirect(url_for('index'))

@app.route('/productos')
def productos():
    productos = Producto.query.all() 
    return render_template('products.html', productos=productos)

@app.route('/admin')
def admin_panel():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('paneladmin.html')

@app.route('/admin/agregar')
def admin_agregar():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('adminagregarprod.html')

@app.route('/perfil')
def user_perfil():
    if 'customer_id' not in session:
        return redirect(url_for('user_login'))
    
    customer_id = session['customer_id']
    customer = Cliente.query.get(customer_id)
    
    if not customer:
        flash('Usuario no encontrado.')
        return redirect(url_for('home'))
    
    return render_template('miperfil.html', customer=customer)


@app.route('/agregar_al_carrito/<int:producto_id>')
def agregar_al_carrito(producto_id):
    if 'customer_id' not in session:
        flash('Por favor inicia sesión para agregar productos al carrito.')
        return redirect(url_for('user_login'))

    cliente_id = session['customer_id']
    producto = Producto.query.get_or_404(producto_id)

    detalle = MyCar.query.filter_by(customer_id=cliente_id, product_id=producto_id).first()
    if detalle:
        detalle.amount += 1
    else:
        detalle = MyCar(customer_id=cliente_id, product_id=producto_id, amount=1, unit_price=producto.unit_price)
        db.session.add(detalle)

    db.session.commit()
    flash('Producto agregado al carrito.')
    return redirect(url_for('productos'))


@app.route('/micarrito')
def user_carrito():
    if 'customer_id' not in session:
        return redirect(url_for('user_login'))

    customer_id = session['customer_id']
    detalles_pedido = MyCar.query.filter_by(customer_id=customer_id).all()

    return render_template('orders.html', detalles_pedido=detalles_pedido)

@app.route('/eliminar_del_carrito/<int:detalle_id>')
def eliminar_del_carrito(detalle_id):
    if 'customer_id' not in session:
        flash('Por favor inicia sesión para eliminar productos del carrito.')
        return redirect(url_for('user_login'))

    detalle = MyCar.query.get_or_404(detalle_id)
    db.session.delete(detalle)
    db.session.commit()
    flash('Producto eliminado del carrito.')
    return redirect(url_for('user_carrito'))

@app.route('/actualizar_cantidad/<int:detalle_id>', methods=['POST'])
def actualizar_cantidad(detalle_id):
    if 'customer_id' not in session:
        flash('Por favor inicia sesión para actualizar la cantidad del producto.')
        return redirect(url_for('user_login'))

    cantidad = int(request.form['cantidad'])
    if cantidad < 1:
        flash('La cantidad debe ser al menos 1.')
        return redirect(url_for('user_carrito'))

    detalle = MyCar.query.get_or_404(detalle_id)
    detalle.amount = cantidad
    db.session.commit()
    flash('Cantidad actualizada correctamente.')
    return redirect(url_for('user_carrito'))

@app.route('/admin/gestionar_productos')
def admin_listar_productos():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    productos = Producto.query.all()
    return render_template('adminlspd.html', productos=productos)

@app.route('/admin/editar/<int:producto_id>', methods=['GET', 'POST'])
def admin_editar_producto(producto_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    producto = Producto.query.get_or_404(producto_id)
    if request.method == 'POST':
        producto.name = request.form['name']
        producto.details = request.form['details']
        producto.unit_price = request.form['unit_price']
        producto.stock = request.form['stock']
        producto.category = request.form['category']

        picture = request.files['picture']
        if picture:
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            producto.picture = 'uploads/' + filename
        
        db.session.commit()
        flash('Producto actualizado correctamente.')
        return redirect(url_for('admin_listar_productos'))
    return render_template('admin_edit_product.html', producto=producto)

@app.route('/admin/eliminar/<int:producto_id>', methods=['POST'])
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
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        
        # Verificar si el email ya está registrado
        cliente_existente = Cliente.query.filter_by(email=email).first()
        if cliente_existente:
            flash('El email ya está registrado.')
            return redirect(url_for('user_registro'))
        
        # Crear nuevo cliente
        nuevo_cliente = Cliente(
            name=name, 
            email=email, 
            phone=phone, 
            address=address, 
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
            session['customer_id'] = cliente.id
            return redirect(url_for('user_perfil'))
        else:
            flash('Correo o contraseña incorrectos')
    return render_template('userlogin.html')


@app.route('/admin/agregar', methods=['GET', 'POST'])
def admin_agregar_producto():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            details = request.form['details']
            unit_price = request.form['unit_price']
            stock = request.form['stock']
            picture = request.files['picture']
            category = request.form['category']

            # Verificar si el producto ya existe
            producto_existente = Producto.query.filter_by(name=name).first()
            if producto_existente:
                flash('El producto ya existe.')
                return redirect(url_for('admin_agregar_producto'))

            # Guardar la imagen en el servidor
            if picture and picture.filename != '':
                filename = secure_filename(picture.filename)
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagen_path = 'uploads/' + filename
            else:
                imagen_path = None

            # Agregar nuevo producto a la base de datos
            nuevo_producto = Producto(name=name, details=details, unit_price=unit_price, stock=stock, picture=imagen_path, category=category)
            db.session.add(nuevo_producto)
            db.session.commit()

            flash('Producto agregado exitosamente.')
            return redirect(url_for('admin_agregar_producto'))
        
        except Exception as e:
            # Manejar el error y proporcionar información de depuración
            db.session.rollback()
            flash(f'Error al agregar producto: {e}')
            return redirect(url_for('admin_agregar_producto'))
    
    return render_template('adminagregarprod.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Administrador.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            return redirect(url_for('admin_panel'))
        else:
            flash('Correo o contraseña incorrectos')
    return render_template('admin.html')

@app.route('/admin_logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('index'))

@app.route('/borrar_cuenta', methods=['POST'])
def borrar_cuenta():
    if 'customer_id' not in session:
        return redirect(url_for('user_login'))
    
    customer_id = session['customer_id']
    customer = Cliente.query.get(customer_id)
    
    if customer:
        db.session.delete(customer)
        db.session.commit()
        session.pop('customer_id', None)
        flash('Tu cuenta ha sido eliminada correctamente.')
    else:
        flash('Error al intentar eliminar la cuenta.')
    
    return redirect(url_for('home'))

@app.route('/logout')
def user_logout():
    session.pop('customer_id', None)
    return redirect(url_for('index'))

@app.route('/editar_perfil')
def editar_perfil():
    if 'customer_id' not in session:
        return redirect(url_for('user_login'))
    
    customer_id = session['customer_id']
    customer = Cliente.query.get(customer_id)
    
    if not customer:
        flash('Usuario no encontrado.')
        return redirect(url_for('home'))
    
    return render_template('useredit.html', customer=customer)

@app.route('/actualizar_perfil', methods=['POST'])
def actualizar_perfil():
    if 'customer_id' not in session:
        return redirect(url_for('user_login'))

    customer_id = session['customer_id']
    customer = Cliente.query.get(customer_id)

    if not customer:
        flash('Usuario no encontrado.')
        return redirect(url_for('home'))

    customer.name = request.form['name']
    customer.email = request.form['email']
    customer.phone = request.form['phone']
    customer.address = request.form['address']

    db.session.commit()
    flash('Perfil actualizado correctamente.')
    return redirect(url_for('user_perfil'))

@app.route('/admin/listar_clientes')
def admin_listar_clientes():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    clientes = Cliente.query.all()
    return render_template('adminlsuser.html', clientes=clientes)

@app.route('/admin/eliminar_cliente/<int:cliente_id>', methods=['POST'])
def admin_eliminar_cliente(cliente_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado correctamente.')
    return redirect(url_for('admin_listar_clientes'))

@app.route('/admin/listar_auditorias')
def admin_listar_auditorias():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    auditorias = Auditoria.query.all()
    return render_template('adminlsaud.html', auditorias=auditorias)

@app.route('/confirmar_compra')
def confirmar_compra():
    if 'customer_id' not in session:
        flash('Por favor inicia sesión para confirmar tu compra.')
        return redirect(url_for('user_login'))

    customer_id = session['customer_id']
    detalles_pedido = MyCar.query.filter_by(customer_id=customer_id).all()

    return render_template('usercompra.html', detalles_pedido=detalles_pedido)

@app.route('/procesar_compra', methods=['POST'])
def procesar_compra():
    if 'customer_id' not in session:
        flash('Por favor inicia sesión para confirmar tu compra.')
        return redirect(url_for('user_login'))

    customer_id = session['customer_id']
    detalles_pedido = MyCar.query.filter_by(customer_id=customer_id).all()

    if not detalles_pedido:
        flash('Tu carrito está vacío.')
        return redirect(url_for('productos'))

    # Verificar el stock antes de procesar la compra
    for detalle in detalles_pedido:
        producto = Producto.query.get(detalle.product_id)
        if producto.stock < detalle.amount:
            flash(f'No hay suficiente stock para {producto.name}. Solo hay {producto.stock} en inventario.')
            return redirect(url_for('confirmar_compra'))

    # Procesar la compra y mover los datos a las tablas definitivas Orders y OrdersDetails
    nuevo_pedido = Pedido(customer_id=customer_id, total=sum(detalle.unit_price * detalle.amount for detalle in detalles_pedido))
    db.session.add(nuevo_pedido)
    db.session.commit()

    for detalle in detalles_pedido:
        producto = Producto.query.get(detalle.product_id)
        producto.stock -= detalle.amount  # Reducir el stock del producto
        nuevo_detalle = DetallePedido(
            order_id=nuevo_pedido.id,
            product_id=detalle.product_id,
            amount=detalle.amount,
            unit_price=detalle.unit_price
        )
        db.session.add(nuevo_detalle)
        db.session.delete(detalle)

    db.session.commit()
    
    flash('Pago realizado con éxito.')
    return redirect(url_for('productos'))

@app.route('/cancelar_compra')
def cancelar_compra():
    if 'customer_id' not in session:
        flash('Por favor inicia sesión para cancelar tu compra.')
        return redirect(url_for('user_login'))

    customer_id = session['customer_id']
    detalles_pedido = MyCar.query.filter_by(customer_id=customer_id).all()

    for detalle in detalles_pedido:
        db.session.delete(detalle)

    db.session.commit()
    
    flash('Compra cancelada y carrito vacío.')
    return redirect(url_for('productos'))

@app.route('/admin/listar_pedidos')
def admin_listar_pedidos():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    pedidos = Pedido.query.all()

    for pedido in pedidos:
        pedido.detalles = DetallePedido.query.filter_by(order_id=pedido.id).all()
        pedido.cliente = Cliente.query.get(pedido.customer_id)

    return render_template('adminlspdd.html', pedidos=pedidos)



if __name__ == '__main__':
    app.run(debug=True, port=8000)