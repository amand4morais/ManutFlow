from models.database import db
from datetime import datetime

class HistoricoEquipamento(db.Model):
    """
    Model para representar o histórico automático de um equipamento (Timeline)
    """
    __tablename__ = 'historico_equipamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    evento = db.Column(db.String(100), nullable=False)
    # Eventos: 'AQUISIÇÃO', 'MANUTENÇÃO INICIADA', 'MANUTENÇÃO CONCLUÍDA', 'TROCA DE SETOR', 'TROCA DE RESPONSÁVEL'
    
    descricao = db.Column(db.Text, nullable=True)
    data_evento = db.Column(db.DateTime, default=datetime.now)
    
    # Informações extras para rastreabilidade
    valor_anterior = db.Column(db.String(200), nullable=True)
    valor_novo = db.Column(db.String(200), nullable=True)
    
    # Relacionamento com o equipamento
    equipamento_rel = db.relationship('Equipamento', backref=db.backref('historico', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<HistoricoEquipamento {self.evento} - Equipamento {self.equipamento_id}>'
    
    @staticmethod
    def registrar(equipamento_id, evento, descricao=None, valor_anterior=None, valor_novo=None):
        """Método auxiliar para registrar um evento no histórico"""
        novo_registro = HistoricoEquipamento(
            equipamento_id=equipamento_id,
            evento=evento,
            descricao=descricao,
            valor_anterior=valor_anterior,
            valor_novo=valor_novo
        )
        db.session.add(novo_registro)
        # Removido db.session.commit() para evitar conflitos em gatilhos (events)
        return novo_registro
