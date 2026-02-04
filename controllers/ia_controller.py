from flask import Blueprint, render_template, jsonify, current_app, redirect, url_for, flash, request
from flask_login import current_user, login_required
from models.equipamento import Equipamento
from models.manutencao import Manutencao
from models.database import db
from groq import Groq
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Blueprint para rotas de IA
ia_bp = Blueprint('ia', __name__)

# Cliente Groq (será inicializado quando necessário)
client = None

def get_groq_client():
    """Retorna cliente Groq configurado"""
    global client
    if client is None:
        api_key = current_app.config.get('GROQ_API_KEY')
        if not api_key:
            # Tenta pegar do ambiente se não estiver no config
            api_key = os.environ.get('GROQ_API_KEY')
        
        if api_key:
            client = Groq(api_key=api_key)
    return client

def preparar_dados_para_ia(data_inicio=None, data_fim=None):
    """
    Prepara os dados de equipamentos e manutenções para análise da IA
    Com suporte a filtragem por período (União Main + Branch)
    """
    equipamentos = Equipamento.get_all()
    
    # Busca manutenções filtradas ou totais (Da Main)
    if data_inicio or data_fim:
        manutencoes = Manutencao.get_filtered(data_inicio, data_fim)
    else:
        manutencoes = Manutencao.get_all()
    
    # Estatísticas gerais baseadas na lista filtrada
    total_equipamentos = len(equipamentos)
    equipamentos_ativos = len([e for e in equipamentos if e.status == 'ativo'])
    equipamentos_em_manutencao = len([e for e in equipamentos if e.status == 'em_manutencao'])
    equipamentos_sucateados = len([e for e in equipamentos if e.status == 'sucateado'])
    
    total_manutencoes = len(manutencoes)
    manutencoes_preventivas = len([m for m in manutencoes if m.tipo == 'preventiva'])
    manutencoes_corretivas = len([m for m in manutencoes if m.tipo == 'corretiva'])
    
    # Custo total baseado na lista filtrada
    custo_total = sum(m.custo for m in manutencoes)
    
    # Análise detalhada (precisa filtrar por equipamento respeitando as datas)
    equipamentos_detalhes = []
    setores_stats = defaultdict(lambda: {'total_equipamentos': 0, 'custo_total': 0, 'total_manutencoes': 0})
    
    for eq in equipamentos:
        # Busca manutenções do equipamento
        manutencoes_eq_total = Manutencao.get_by_equipamento(eq.id)
        
        # Aplica o filtro de data em memória para este equipamento (Da Main)
        manutencoes_eq = manutencoes_eq_total
        if data_inicio:
            manutencoes_eq = [m for m in manutencoes_eq if m.data_manutencao >= data_inicio]
        if data_fim:
            manutencoes_eq = [m for m in manutencoes_eq if m.data_manutencao <= data_fim]
            
        custo_eq = sum(m.custo for m in manutencoes_eq)
        
        # Dados para análise individual (União Main + Branch)
        equipamentos_detalhes.append({
            'codigo': eq.codigo,
            'nome': eq.nome,
            'setor': eq.setor_rel.nome if hasattr(eq, 'setor_rel') and eq.setor_rel else "N/A",
            'status': eq.status,
            'total_manutencoes': len(manutencoes_eq),
            'manutencoes_preventivas': len([m for m in manutencoes_eq if m.tipo == 'preventiva']),
            'manutencoes_corretivas': len([m for m in manutencoes_eq if m.tipo == 'corretiva']),
            'custo_total': custo_eq
        })
        
        # Dados para análise de setor
        setor_nome = eq.setor_rel.nome if hasattr(eq, 'setor_rel') and eq.setor_rel else "N/A"
        setores_stats[setor_nome]['total_equipamentos'] += 1
        setores_stats[setor_nome]['custo_total'] += custo_eq
        setores_stats[setor_nome]['total_manutencoes'] += len(manutencoes_eq)
    
    # Manutenções recentes (interseção entre filtro e últimos 30 dias)
    data_limite = datetime.now().date() - timedelta(days=30)
    manutencoes_recentes = [m for m in manutencoes if m.data_manutencao >= data_limite]
    
    dados = {
        'estatisticas_gerais': {
            'total_equipamentos': total_equipamentos,
            'equipamentos_ativos': equipamentos_ativos,
            'equipamentos_em_manutencao': equipamentos_em_manutencao,
            'equipamentos_sucateados': equipamentos_sucateados,
            'total_manutencoes': total_manutencoes,
            'manutencoes_preventivas': manutencoes_preventivas,
            'manutencoes_corretivas': manutencoes_corretivas,
            'custo_total': custo_total,
            'manutencoes_ultimos_30_dias': len(manutencoes_recentes)
        },
        'equipamentos': equipamentos_detalhes,
        'setores': dict(setores_stats),
        'periodo': {
            'inicio': data_inicio.strftime('%d/%m/%Y') if data_inicio else 'Início',
            'fim': data_fim.strftime('%d/%m/%Y') if data_fim else 'Hoje'
        }
    }
    
    return dados

def gerar_analise_ia(dados):
    """
    Usa a IA do Groq para gerar análise e sugestões baseadas nos dados
    """
    # 1. VALIDAÇÃO DE DADOS VAZIOS (CORREÇÃO SOLICITADA)
    # Se não houver manutenções no período filtrado, não chamamos a IA.
    # Isso evita "alucinações" ou dicas genéricas quando o período está vazio.
    if dados['estatisticas_gerais']['total_manutencoes'] == 0:
        return {
            'resumo_saude': None, # Retorna None para indicar que não houve análise
            'equipamentos_criticos': [],
            'analise_setores': [],
            'recomendacoes': []
        }

    groq_client = get_groq_client()
    
    if not groq_client:
        return {
            'resumo_saude': 'A chave da API do Groq não foi configurada. Por favor, configure a variável de ambiente GROQ_API_KEY.',
            'equipamentos_criticos': [],
            'analise_setores': [],
            'recomendacoes': ['Configure a chave da API para receber recomendações inteligentes.']
        }

    try:
        # Prepara o prompt para a IA (agora com contexto de período da Main)
        periodo_texto = f"Período de análise: de {dados['periodo']['inicio']} até {dados['periodo']['fim']}."
        
        prompt = f"""
Você é um especialista em gestão de manutenção industrial de alto nível. Analise os seguintes dados de equipamentos e manutenções e forneça uma análise estratégica profunda.

CONTEXTO:
{periodo_texto}

DADOS DO SISTEMA:
{json.dumps(dados, indent=2, ensure_ascii=False)}

Sua tarefa é gerar um relatório técnico em formato JSON com os seguintes pontos:

1. RESUMO DA SAÚDE GERAL: Avaliação qualitativa e quantitativa do parque de máquinas neste período.
2. EQUIPAMENTOS CRÍTICOS: Identifique os equipamentos que apresentam maior risco operacional ou financeiro.
3. ANÁLISE POR SETOR: Compare o desempenho e custos entre os diferentes setores.
4. RECOMENDAÇÕES ESTRATÉGICAS: Sugira ações concretas para reduzir custos e aumentar a disponibilidade.

IMPORTANTE: Responda EXCLUSIVAMENTE em formato JSON puro, sem explicações fora do JSON. Use a seguinte estrutura:
{{
    "resumo_saude": "texto detalhado",
    "equipamentos_criticos": [
        {{"codigo": "código", "nome": "nome", "prioridade": "alta/média/baixa", "justificativa": "texto explicativo"}}
    ],
    "analise_setores": [
        {{"setor": "nome", "custo_total": valor, "recomendacao": "ação sugerida"}}
    ],
    "recomendacoes": ["recomendação 1", "recomendação 2", "recomendação 3", "recomendação 4"]
}}
"""
        
        # Chama a API Groq
        completion = groq_client.chat.completions.create(
            model=current_app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[
                {"role": "system", "content": "Você é um engenheiro de manutenção sênior que fornece análises em JSON puro."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2, # Baixa temperatura para maior consistência no JSON
            response_format={"type": "json_object"} # Força o retorno em JSON se o modelo suportar
        )
        
        # Extrai e limpa a resposta
        resposta_texto = completion.choices[0].message.content.strip()
        
        # Converte para JSON
        analise = json.loads(resposta_texto)
        return analise
        
    except Exception as e:
        print(f"Erro ao gerar análise do Groq: {str(e)}")
        return {
            'resumo_saude': f'Ocorreu um erro ao processar a análise: {str(e)}',
            'equipamentos_criticos': [],
            'analise_setores': [],
            'recomendacoes': ['Verifique sua conexão e a validade da chave API do Groq.']
        }

@ia_bp.route('/ia/dashboard')
@login_required
def dashboard_ia():
    """
    Exibe o dashboard com análises da IA com suporte a filtros (União Main + Branch)
    """
    # Segurança da Branch
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        flash("Acesso negado! Apenas administradores podem ver as análises avançadas de IA.", "danger")
        return redirect(url_for('index'))

    # Filtros da Main
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    filtro_pre = request.args.get('filtro_pre', '')
    
    data_inicio = None
    data_fim = None
    
    # Processa as datas se fornecidas
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
    dados = preparar_dados_para_ia(data_inicio, data_fim)
    analise = gerar_analise_ia(dados)
    
    return render_template('ia_dashboard.html', 
                         dados=dados, 
                         analise=analise,
                         data_inicio=data_inicio_str,
                         data_fim=data_fim_str,
                         filtro_pre=filtro_pre)

@ia_bp.route('/api/ia/analise')
@login_required
def api_analise_ia():
    """
    API: Retorna análise da IA em JSON
    """
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    data_inicio = None
    data_fim = None
    
    if data_inicio_str:
        try: data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        except: pass
    if data_fim_str:
        try: data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except: pass

    dados = preparar_dados_para_ia(data_inicio, data_fim)
    analise = gerar_analise_ia(dados)
    
    return jsonify({
        'dados': dados,
        'analise': analise
    })

@ia_bp.route('/api/ia/dados')
@login_required
def api_dados_ia():
    """
    API: Retorna apenas os dados preparados para IA
    """
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    data_inicio = None
    data_fim = None
    
    if data_inicio_str:
        try: data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        except: pass
    if data_fim_str:
        try: data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except: pass

    dados = preparar_dados_para_ia(data_inicio, data_fim)
    return jsonify(dados)