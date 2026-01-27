from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instância do SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Inicializa o banco de dados com a aplicação Flask
    """
    db.init_app(app)
    
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        print("Banco de dados inicializado com sucesso!")

def get_db():
    """
    Retorna a instância do banco de dados
    """
    return db
