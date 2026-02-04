from models.database import db
from datetime import datetime

class Agendamento(db.Model):
    """
    Model para representar agendamentos de manutenções preventivas
    """
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    data_prevista = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pendente') # pendente, concluido, cancelado
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamento com o equipamento
    equipamento = db.relationship('Equipamento', backref=db.backref('agendamentos', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<Agendamento {self.id} - Equipamento {self.equipamento_id} em {self.data_prevista}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'equipamento_nome': self.equipamento.nome if self.equipamento else "N/A",
            'data_prevista': self.data_prevista.strftime('%Y-%m-%d'),
            'descricao': self.descricao,
            'status': self.status
        }
    
    @staticmethod
    def get_pendentes():
        """Retorna todos os agendamentos pendentes"""
        return Agendamento.query.filter_by(status='pendente').order_by(Agendamento.data_prevista.asc()).all()
    
    @staticmethod
    def get_por_equipamento(equipamento_id):
        """Retorna agendamentos de um equipamento específico"""
        return Agendamento.query.filter_by(equipamento_id=equipamento_id).order_by(Agendamento.data_prevista.desc()).all()

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()