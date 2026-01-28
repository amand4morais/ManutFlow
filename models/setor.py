from models.database import db

class Setor(db.Model):
    __tablename__ = 'setores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relacionamento: Um setor tem muitos equipamentos
    equipamentos = db.relationship('Equipamento', backref='setor_rel', lazy=True)

    def __repr__(self):
        return f'<Setor {self.nome}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Setor.query.all()
