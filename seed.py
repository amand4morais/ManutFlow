from app import app
from models.database import db
from models.funcionario import Funcionario
from models.setor import Setor
from datetime import datetime

def seed():
    with app.app_context():
        # IMPORTANTE: Como a estrutura da tabela mudou (adicionamos setor_id), 
        # o SQLite precisa que a tabela seja recriada para reconhecer a nova coluna.
        # Se você já tem dados, pode ser necessário deletar o arquivo .db na pasta /data
        # ou rodar db.create_all() para garantir que as tabelas estejam atualizadas.
        db.create_all()

        # 1. Criar Setor Padrão se não existir
        setor_admin = Setor.query.filter_by(nome="Administração").first()
        if not setor_admin:
            setor_admin = Setor(nome="Administração")
            setor_admin.save()
            print("Setor 'Administração' criado.")

        # 2. Criar Admin Padrão se não existir
        if not Funcionario.query.filter_by(email="admin123@aguia.com").first():
            admin = Funcionario(
                nome="Administrador Geral",
                email="admin123@aguia.com",
                senha="admin123", # Em produção, use hash!
                is_admin=True,
                data_criacao=datetime.strptime("02/02/2026", "%d/%m/%Y"),
                setor_id=setor_admin.id # Associando o admin ao setor criado
            )
            admin.save()
            print("Usuário Admin criado: admin123@aguia.com / admin123")
        else:
            print("Admin já existe.")

if __name__ == "__main__":
    seed()