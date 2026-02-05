from models.database import db
from flask_login import UserMixin

class Funcionario(db.Model, UserMixin):
    __tablename__ = 'funcionarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(100), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=True)
    
    # Relacionamento: Um funcionário é responsável por muitos equipamentos
    equipamentos_responsaveis = db.relationship('Equipamento', backref='responsavel_rel', lazy=True)

    def __repr__(self):
        return f'<Funcionario {self.nome}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Funcionario.query.all()