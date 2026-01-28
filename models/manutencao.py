from models.database import db
from datetime import datetime

class Manutencao(db.Model):
    """
    Model para representar uma manutenção
    """
    __tablename__ = 'manutencoes'
    
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    # Tipos possíveis: 'preventiva', 'corretiva'
    
    data_manutencao = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    custo = db.Column(db.Float, default=0.0)
    
    # NOVO: Quem registrou a manutenção
    autor_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=False)
    
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Manutencao {self.id} - {self.tipo} - Equipamento {self.equipamento_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'equipamento_nome': self.equipamento.nome if self.equipamento else None,
            'tipo': self.tipo,
            'data_manutencao': self.data_manutencao.strftime('%Y-%m-%d') if self.data_manutencao else None,
            'descricao': self.descricao,
            'custo': self.custo,
            'autor': self.autor_rel.nome if hasattr(self, 'autor_rel') and self.autor_rel else "N/A"
        }
    
    def get_tipo_label(self):
        labels = {'preventiva': 'Preventiva', 'corretiva': 'Corretiva'}
        return labels.get(self.tipo, self.tipo)
    
    def get_tipo_color(self):
        cores = {'preventiva': 'info', 'corretiva': 'warning'}
        return cores.get(self.tipo, 'secondary')
    
    @staticmethod
    def get_all():
        return Manutencao.query.order_by(Manutencao.data_manutencao.desc()).all()
    
    @staticmethod
    def get_by_id(manutencao_id):
        return Manutencao.query.get(manutencao_id)
    
    @staticmethod
    def get_by_equipamento(equipamento_id):
        return Manutencao.query.filter_by(equipamento_id=equipamento_id).order_by(Manutencao.data_manutencao.desc()).all()
    
    @staticmethod
    def get_custo_total():
        resultado = db.session.query(db.func.sum(Manutencao.custo)).scalar()
        return resultado if resultado else 0.0
    
    @staticmethod
    def get_custo_por_equipamento(equipamento_id):
        resultado = db.session.query(db.func.sum(Manutencao.custo)).filter_by(equipamento_id=equipamento_id).scalar()
        return resultado if resultado else 0.0
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
