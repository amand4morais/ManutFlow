from models.database import db
from datetime import datetime

class Equipamento(db.Model):
    """
    Model para representar um equipamento
    """
    __tablename__ = 'equipamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    
    # NOVAS CHAVES ESTRANGEIRAS
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=False)
    
    status = db.Column(db.String(20), nullable=False, default='ativo')
    # Status possíveis: 'ativo', 'em_manutencao', 'sucateado'
    
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamento com manutenções
    manutencoes = db.relationship('Manutencao', backref='equipamento', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Equipamento {self.codigo} - {self.nome}>'
    
    def to_dict(self):
        """
        Converte o objeto para dicionário
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'setor': self.setor_rel.nome if self.setor_rel else "N/A",
            'responsavel': self.responsavel_rel.nome if self.responsavel_rel else "N/A",
            'status': self.status,
            'data_cadastro': self.data_cadastro.strftime('%Y-%m-%d %H:%M:%S') if self.data_cadastro else None,
            'data_atualizacao': self.data_atualizacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_atualizacao else None,
            'total_manutencoes': len(self.manutencoes)
        }
    
    def get_status_color(self):
        """
        Retorna a cor associada ao status do equipamento
        """
        cores = {
            'ativo': 'success',  # Verde
            'em_manutencao': 'danger',  # Vermelho
            'sucateado': 'secondary'  # Cinza
        }
        return cores.get(self.status, 'secondary')
    
    def get_status_label(self):
        """
        Retorna o label formatado do status
        """
        labels = {
            'ativo': 'Ativo',
            'em_manutencao': 'Em Manutenção',
            'sucateado': 'Sucateado'
        }
        return labels.get(self.status, self.status)
    
    @staticmethod
    def get_all():
        """
        Retorna todos os equipamentos
        """
        return Equipamento.query.all()
    
    @staticmethod
    def get_by_id(equipamento_id):
        """
        Busca equipamento por ID
        """
        return Equipamento.query.get(equipamento_id)
    
    @staticmethod
    def get_by_codigo(codigo):
        """
        Busca equipamento por código
        """
        return Equipamento.query.filter_by(codigo=codigo).first()
    
    @staticmethod
    def get_by_status(status):
        """
        Retorna equipamentos por status
        """
        return Equipamento.query.filter_by(status=status).all()
    
    def save(self):
        """
        Salva o equipamento no banco de dados
        """
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """
        Remove o equipamento do banco de dados
        """
        db.session.delete(self)
        db.session.commit()