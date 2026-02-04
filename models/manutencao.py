from models.database import db
from datetime import datetime
from sqlalchemy import event

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
    
    # Da Branch: Quem registrou a manutenção
    autor_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=False)
    
    # Relacionamento para acessar o nome do autor
    autor_rel = db.relationship('Funcionario', backref='manutencoes_registradas', lazy=True)
    
    data_registro = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Manutencao {self.id} - {self.tipo} - Equipamento {self.equipamento_id}>'
    
    def to_dict(self):
        """
        Converte o objeto para dicionário (União Main + Branch)
        """
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'equipamento_nome': self.equipamento.nome if self.equipamento else None,
            'equipamento_codigo': self.equipamento.codigo if self.equipamento else None,
            'tipo': self.tipo,
            'tipo_label': self.get_tipo_label(),
            'data_manutencao': self.data_manutencao.strftime('%Y-%m-%d') if self.data_manutencao else None,
            'descricao': self.descricao,
            'custo': self.custo,
            'autor': self.autor_rel.nome if hasattr(self, 'autor_rel') and self.autor_rel else "N/A",
            'data_registro': self.data_registro.strftime('%Y-%m-%d %H:%M:%S') if self.data_registro else None
        }
    
    def get_tipo_label(self):
        """
        Retorna o label formatado do tipo
        """
        labels = {
            'preventiva': 'Preventiva',
            'corretiva': 'Corretiva'
        }
        return labels.get(self.tipo, self.tipo)
    
    def get_tipo_color(self):
        """
        Retorna a cor associada ao tipo de manutenção
        """
        cores = {
            'preventiva': 'info',  # Azul
            'corretiva': 'warning'  # Amarelo
        }
        return cores.get(self.tipo, 'secondary')
    
    @staticmethod
    def get_all():
        """
        Retorna todas as manutenções
        """
        return Manutencao.query.order_by(Manutencao.data_manutencao.desc()).all()
    
    @staticmethod
    def get_by_id(manutencao_id):
        """
        Busca manutenção por ID
        """
        return Manutencao.query.get(manutencao_id)
    
    @staticmethod
    def get_by_equipamento(equipamento_id):
        """
        Retorna manutenções de um equipamento específico
        """
        return Manutencao.query.filter_by(equipamento_id=equipamento_id).order_by(Manutencao.data_manutencao.desc()).all()
    
    @staticmethod
    def get_by_tipo(tipo):
        """
        Retorna manutenções por tipo
        """
        return Manutencao.query.filter_by(tipo=tipo).order_by(Manutencao.data_manutencao.desc()).all()
    
    @staticmethod
    def get_filtered(data_inicio=None, data_fim=None):
        """
        Retorna manutenções filtradas por período (Da Main)
        """
        query = Manutencao.query
        
        if data_inicio:
            query = query.filter(Manutencao.data_manutencao >= data_inicio)
        
        if data_fim:
            query = query.filter(Manutencao.data_manutencao <= data_fim)
            
        return query.order_by(Manutencao.data_manutencao.desc()).all()

    @staticmethod
    def get_custo_total():
        """
        Retorna o custo total de todas as manutenções
        """
        resultado = db.session.query(db.func.sum(Manutencao.custo)).scalar()
        return resultado if resultado else 0.0
    
    @staticmethod
    def get_custo_por_equipamento(equipamento_id):
        """
        Retorna o custo total de manutenções de um equipamento
        """
        resultado = db.session.query(db.func.sum(Manutencao.custo)).filter_by(equipamento_id=equipamento_id).scalar()
        return resultado if resultado else 0.0
    
    def save(self):
        """
        Salva a manutenção no banco de dados
        """
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """
        Remove a manutenção do banco de dados
        """
        db.session.delete(self)
        db.session.commit()

# Gatilho Automático para Histórico de Manutenção
@event.listens_for(Manutencao, 'after_insert')
def registrar_historico_manutencao(mapper, connection, target):
    from models.historico_equipamento import HistoricoEquipamento
    novo_h = HistoricoEquipamento(
        equipamento_id=target.equipamento_id,
        evento='MANUTENÇÃO INICIADA',
        descricao=f"Manutenção {target.get_tipo_label()} registrada. Descrição: {target.descricao[:100]}..."
    )
    db.session.add(novo_h)