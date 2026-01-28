from flask import Flask, render_template
from models.database import db, init_db
from models.equipamento import Equipamento
from models.manutencao import Manutencao
from controllers.equipamento_controller import equipamento_bp
from controllers.manutencao_controller import manutencao_bp
from controllers.ia_controller import ia_bp
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

# Inicializa o banco de dados
init_db(app)

# Registra blueprints (controllers)
app.register_blueprint(equipamento_bp)
app.register_blueprint(manutencao_bp)
app.register_blueprint(ia_bp)

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

# Rota de teste
@app.route('/teste')
def teste():
    """
    Rota de teste para verificar se o sistema está funcionando
    """
    return {
        'status': 'ok',
        'mensagem': 'Sistema de Manutenção funcionando corretamente!',
        'versao': '1.0.0'
    }

# Tratamento de erros
@app.errorhandler(404)
def page_not_found(e):
    """
    Página de erro 404
    """
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """
    Página de erro 500
    """
    return render_template('base.html'), 500

# Contexto do template - variáveis globais disponíveis em todos os templates
@app.context_processor
def utility_processor():
    """
    Adiciona funções utilitárias aos templates
    """
    def format_currency(value):
        """Formata valor como moeda brasileira"""
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return dict(format_currency=format_currency)

# Ponto de entrada da aplicação
if __name__ == '__main__':
    print("=" * 60)
    print("Sistema de Controle de Manutenção de Equipamentos")
    print("=" * 60)
    print("Iniciando servidor...")
    print("Acesse: http://localhost:5000")
    print("=" * 60)
    
    # Executa a aplicação
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
