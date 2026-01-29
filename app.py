from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from models.database import db, init_db
import os
from pathlib import Path

# IMPORTE TODOS OS MODELOS AQUI
from models.equipamento import Equipamento
from models.manutencao import Manutencao
from models.setor import Setor
from models.funcionario import Funcionario

from controllers.equipamento_controller import equipamento_bp
from controllers.manutencao_controller import manutencao_bp
from controllers.ia_controller import ia_bp
from controllers.setor_controller import setor_bp
from controllers.auth_controller import auth_bp # NOVO IMPORT

import config
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.absolute()
TEMPLATE_DIR = str(BASE_DIR / 'views' / 'templates')
STATIC_DIR = str(BASE_DIR / 'views' / 'static')

app = Flask(__name__, 
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)

app.config.from_object(config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # Define a rota de login padrão

@login_manager.unauthorized_handler
def unauthorized():
    from flask import flash, redirect, url_for
    flash('Atenção: Você precisa estar logado para acessar as funcionalidades do sistema.', 'warning')
    return redirect(url_for('auth.login')) # Redireciona para o login real agora

@login_manager.user_loader
def load_user(user_id):
    return Funcionario.query.get(int(user_id))

init_db(app)

# Registra blueprints
app.register_blueprint(equipamento_bp)
app.register_blueprint(manutencao_bp)
app.register_blueprint(ia_bp)
app.register_blueprint(setor_bp)
app.register_blueprint(auth_bp) # NOVO REGISTRO

@app.route('/')
def index():
    """Página inicial - Dashboard"""
    try:
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
    except Exception as e:
        print(f"Erro ao carregar index: {str(e)}")
        return f"Erro interno: {str(e)}", 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    from flask import flash, redirect, url_for
    flash('Ocorreu um erro interno.', 'danger')
    return redirect(url_for('index'))

@app.errorhandler(Exception)
def handle_exception(e):
    from flask import flash, redirect, url_for
    if "401" in str(e): # Ignora erro de auth que já é tratado
        return redirect(url_for('auth.login'))
    flash(f'Ocorreu um erro: {str(e)}', 'warning')
    return redirect(url_for('index'))

@app.context_processor
def utility_processor():
    def format_currency(value):
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return dict(format_currency=format_currency)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)