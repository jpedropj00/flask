from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ''

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable = False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
# Definindo rota(página principal) a requisição
@app.route('/teste')
def hello_world():
    return 'hello world';

if __name__ == '__main__':
    app.run(debug=True)