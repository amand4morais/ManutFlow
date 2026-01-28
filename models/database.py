from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instância do SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Inicializa o banco de dados com a aplicação Flask
    """
    import os
    from pathlib import Path
    
    # Garante que a pasta 'data' existe para o SQLite
    data_dir = Path(app.root_path) / 'data'
    if not data_dir.exists():
        os.makedirs(data_dir)
        print(f"Pasta de dados criada em: {data_dir}")

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
