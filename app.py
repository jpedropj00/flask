from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
loginManager = LoginManager()  # corrigido
loginManager.init_app(app)
loginManager.login_view = 'login'
CORS(app)

# -------------------------
# MODELS
# -------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    cart = db.relationship('CartItem', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    cart_items = db.Relationship('CartItem', backref='product', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# -------------------------
# LOGIN MANAGER
# -------------------------
@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------------
# LOGIN
# -------------------------
@app.route('/api/login', methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get('username')).first()

    if not user:
        return jsonify({'message': 'Usuário não encontrado!'}), 404

    if data.get('password') == user.password:
        login_user(user)
        return jsonify({'message': 'Login realizado com sucesso!'}), 200

    return jsonify({'message': 'Senha inválida'}), 401

# -------------------------
# CRUD PRODUCTS
# -------------------------
@app.route('/api/products/add', methods=['POST'])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(
            name=data['name'], 
            price=data['price'], 
            description=data.get("description", "")
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Produto cadastrado com sucesso"}), 201

    return jsonify({"message": "Dados do produto inválido"}), 400


@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Produto deletado com sucesso!'}), 200

    return jsonify({'message': 'Produto não encontrado'}), 404


@app.route('/api/products/<int:product_id>', methods=["GET"])
@login_required
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description
        })
    return jsonify({"message": "Produto não encontrado"}), 404


@app.route('/api/products/update/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Produto não encontrado!'}), 404

    data = request.json
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']

    db.session.commit()
    return jsonify({'message': 'Produto atualizado com sucesso'})


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()

    if not products:
        return jsonify({'message': 'Nenhum produto encontrado'}), 404
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description
        })

    return jsonify(products_list), 200
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_Cart(product_id):
    user = User.query.get(int(current_user.id))
    product = Product.query.get(product_id)
    if not user or not product:
        return jsonify({'message': 'Usuario ou produto não encontrado'}), 400
    cart_item = CartItem(user_id=user.id, product_id=product_id, quantity=product.quantity)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({'message': 'Produto adicionado ao carrinho com sucesso'})

@app.route('/api/cart/remove/<int:product_id>', methods=[DELETE])
@login_required
def remove_from_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Produto removido do carrinho com sucesso!'})
    return jsonify({'message': 'Produto não encontrado no carrinho'}), 404

@app.route('/api/cart', methods=['GET'])
@login_required
def view_caet():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_content = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        cart_content.append({
            'id':cart_item.id,
            'user_id': cart_item.user.id,
            'product_id': cart_item.product_id,
            'quantity': cart_item.quantity,
            'product_name': product.name,
            'product_price': product.price,
        })
    if cart_content:
        return jsonify(cart_content), 200
    return jsonify({'message': 'Carrinho vazio'}), 404

@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    if not user: 
        return jsonify({'message': 'Usuário não encontrado'})
    cart_items = user.cart
    if not cart_items:
        return jsonify({'message': 'Carrinho vazio'})
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Checkout realizado com sucesso!'}), 200 
# -------------------------
# RUN
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
