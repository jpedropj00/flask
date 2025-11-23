from flask import Flask

app = Flask(__name__)
# Definindo rota(página principal) a requisição
@app.route('/teste')
def hello_world():
    return 'hello world';

if __name__ == '__main__':
    app.run(debug=True)