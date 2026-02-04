from models.database import db
from datetime import datetime

class Notificacao(db.Model):
    """
    Model para representar notificações e alertas do sistema
    """
    __tablename__ = 'notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), default='info') # info, warning, success, danger
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    link = db.Column(db.String(200), nullable=True) # Link opcional para redirecionamento
    
    # Relacionamento com o funcionário
    usuario = db.relationship('Funcionario', backref=db.backref('notificacoes', lazy=True))
    
    def __repr__(self):
        return f'<Notificacao {self.id} - {self.titulo} para Usuario {self.usuario_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'mensagem': self.mensagem,
            'tipo': self.tipo,
            'lida': self.lida,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'link': self.link
        }
    
    @staticmethod
    def criar(usuario_id, titulo, mensagem, tipo='info', link=None):
        """Método auxiliar para criar uma notificação"""
        nova = Notificacao(
            usuario_id=usuario_id,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            link=link
        )
        db.session.add(nova)
        db.session.commit()
        return nova

    @staticmethod
    def get_nao_lidas(usuario_id):
        """Retorna notificações não lidas de um usuário"""
        return Notificacao.query.filter_by(usuario_id=usuario_id, lida=False).order_by(Notificacao.data_criacao.desc()).all()
    
    @staticmethod
    def marcar_como_lida(notificacao_id):
        """Marca uma notificação específica como lida"""
        notif = Notificacao.query.get(notificacao_id)
        if notif:
            notif.lida = True
            db.session.commit()
            return True
        return False