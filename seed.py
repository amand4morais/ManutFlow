from app import app
from models.database import db
from models.funcionario import Funcionario
from models.setor import Setor

def seed():
    with app.app_context():
        # 1. Criar Setor Padrão se não existir
        if not Setor.query.filter_by(nome="Administração").first():
            setor = Setor(nome="Administração")
            setor.save()
            print("Setor 'Administração' criado.")

        # 2. Criar Admin Padrão se não existir
        if not Funcionario.query.filter_by(email="admin123@aguia.com").first():
            admin = Funcionario(
                nome="Administrador Geral",
                email="admin123@aguia.com",
                senha="admin123", # Em produção, use hash!
                is_admin=True
            )
            admin.save()
            print("Usuário Admin criado: admin123@aguia.com / admin123")
        else:
            print("Admin já existe.")

if __name__ == "__main__":
    seed()
