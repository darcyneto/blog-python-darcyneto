# app.py

from flask import Flask
from flask_migrate import Migrate
from models import db  # Importa o db do __init__.py
from models.user import User
from models.post import Post
from routes import register_routes  # Aqui as rotas são importadas

app = Flask(__name__)
app.config.from_object('config.Config')

# Inicializa o banco de dados
db.init_app(app)

# Inicializa o Flask-Migrate
migrate = Migrate(app, db)

# Registra as rotas
register_routes(app)

# Inicializa o banco de dados e cria o admin, caso não exista
def setup_database():
    with app.app_context():
        db.create_all()  # Cria as tabelas
        if not User.query.filter_by(username="admin").first():
            admin_user = User(username="admin", email="admin@fodao", password="You are not allowed.", phone="666666")
            db.session.add(admin_user)
            db.session.commit()

# Chamando o setup_database explicitamente
setup_database()

if __name__ == '__main__':
    app.run(debug=True)
