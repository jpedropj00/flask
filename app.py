from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
loginManager = loginManager()
loginManager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

class Product(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable = False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
@app.route('/api/products/add', methods=['POST'])
def add_product():
        data = request.json
        if 'name' in data and 'price' in data: 
            product = Product(name=data['name'], price=data['price'], description= data.get("description", ""))
            db.session.add(product)
            db.session.commit()
            return jsonify({"message" : "Produto cadastrado com sucesso"}), 201
        return jsonify({"message" : "Dados do produto inválido"}), 400
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Produto deletado com sucesso!'}), 200
    return jsonify({'message': 'Produto não encontrado'}), 404
@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product=Product.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description
        })
    return jsonify({"message": "Produto não encontrado"}), 404
@app.route('/api/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product=Product.query.get(product_id)
    if not product:
        return jsonify({'message' : 'Produto não encontrado!'}), 404
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
    products_list = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description
        }
        products_list.append(product_data)
    if not products_list:
        return jsonify({'message': 'Nenhum produto encontrado'}), 404 
    return jsonify(products_list), 200
@app.route('/api/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if not user:
        return jsonify({'message' : 'Usuário não encontrado!'}), 404
    else:
        if data.get('password') == user.password:
            return jsonify({'message': 'Login realizado com sucesso!'})
        else:
            return jsonify({'message': 'Senha inválida'}), 401
if __name__ == '__main__':
    app.run(debug=True)