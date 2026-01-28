from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from models.database import db, init_db

# IMPORTE TODOS OS MODELOS AQUI PARA O SQLALCHEMY CRIAR AS TABELAS
from models.equipamento import Equipamento
from models.manutencao import Manutencao
from models.setor import Setor
from models.funcionario import Funcionario

from controllers.equipamento_controller import equipamento_bp
from controllers.manutencao_controller import manutencao_bp
from controllers.ia_controller import ia_bp
from controllers.setor_controller import setor_bp

import config
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Cria a aplicação Flask
app = Flask(__name__, 
            template_folder='views/templates',
            static_folder='views/static')

# Carrega configurações
app.config.from_object(config)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # Rota de login futura

@login_manager.user_loader
def load_user(user_id):
    return Funcionario.query.get(int(user_id))

# Inicializa o banco de dados
init_db(app)

# Registra blueprints (controllers)
app.register_blueprint(equipamento_bp)
app.register_blueprint(manutencao_bp)
app.register_blueprint(ia_bp)
app.register_blueprint(setor_bp)

# Rota principal (Dashboard)
@app.route('/')
def index():
    """
    Página inicial - Dashboard
    """
    equipamentos = Equipamento.get_all()
    manutencoes = Manutencao.get_all()
    
    # Estatísticas
    total_equipamentos = len(equipamentos)
    equipamentos_ativos = len([e for e in equipamentos if e.status == 'ativo'])
    equipamentos_em_manutencao = len([e for e in equipamentos if e.status == 'em_manutencao'])
    total_manutencoes = len(manutencoes)
    
    return render_template('index.html',
                         equipamentos=equipamentos,
                         total_equipamentos=total_equipamentos,
                         equipamentos_ativos=equipamentos_ativos,
                         equipamentos_em_manutencao=equipamentos_em_manutencao,
                         total_manutencoes=total_manutencoes)

# Tratamento de erros
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('base.html'), 500

# Contexto do template
@app.context_processor
def utility_processor():
    def format_currency(value):
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return dict(format_currency=format_currency)

if __name__ == '__main__':
    print("=" * 60)
    print("Sistema ManutFlow - Atualizado com Controle de Acesso")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
