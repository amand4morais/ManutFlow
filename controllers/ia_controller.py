from flask import Blueprint, render_template, jsonify, current_app
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

def preparar_dados_para_ia():
    """
    Prepara os dados de equipamentos e manutenções para análise da IA
    """
    equipamentos = Equipamento.get_all()
    manutencoes = Manutencao.get_all()
    
    # Estatísticas gerais
    total_equipamentos = len(equipamentos)
    equipamentos_ativos = len([e for e in equipamentos if e.status == 'ativo'])
    equipamentos_em_manutencao = len([e for e in equipamentos if e.status == 'em_manutencao'])
    equipamentos_sucateados = len([e for e in equipamentos if e.status == 'sucateado'])
    
    total_manutencoes = len(manutencoes)
    manutencoes_preventivas = len([m for m in manutencoes if m.tipo == 'preventiva'])
    manutencoes_corretivas = len([m for m in manutencoes if m.tipo == 'corretiva'])
    
    custo_total = Manutencao.get_custo_total()
    
    # Análise por equipamento
    equipamentos_detalhes = []
    for eq in equipamentos:
        manutencoes_eq = Manutencao.get_by_equipamento(eq.id)
        custo_eq = Manutencao.get_custo_por_equipamento(eq.id)
        
        equipamentos_detalhes.append({
            'codigo': eq.codigo,
            'nome': eq.nome,
            'setor': eq.setor,
            'status': eq.status,
            'total_manutencoes': len(manutencoes_eq),
            'manutencoes_preventivas': len([m for m in manutencoes_eq if m.tipo == 'preventiva']),
            'manutencoes_corretivas': len([m for m in manutencoes_eq if m.tipo == 'corretiva']),
            'custo_total': custo_eq
        })
    
    # Análise por setor
    setores_stats = defaultdict(lambda: {'total_equipamentos': 0, 'custo_total': 0, 'total_manutencoes': 0})
    for eq in equipamentos:
        setor = eq.setor
        setores_stats[setor]['total_equipamentos'] += 1
        setores_stats[setor]['custo_total'] += Manutencao.get_custo_por_equipamento(eq.id)
        setores_stats[setor]['total_manutencoes'] += len(Manutencao.get_by_equipamento(eq.id))
    
    # Manutenções recentes (últimos 30 dias)
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
        'setores': dict(setores_stats)
    }
    
    return dados

def gerar_analise_ia(dados):
    """
    Usa a IA do Groq para gerar análise e sugestões baseadas nos dados
    """
    groq_client = get_groq_client()
    
    if not groq_client:
        return {
            'resumo_saude': 'A chave da API do Groq não foi configurada. Por favor, configure a variável de ambiente GROQ_API_KEY.',
            'equipamentos_criticos': [],
            'analise_setores': [],
            'recomendacoes': ['Configure a chave da API para receber recomendações inteligentes.']
        }

    try:
        # Prepara o prompt para a IA
        prompt = f"""
Você é um especialista em gestão de manutenção industrial de alto nível. Analise os seguintes dados de equipamentos e manutenções e forneça uma análise estratégica profunda.

DADOS DO SISTEMA:
{json.dumps(dados, indent=2, ensure_ascii=False)}

Sua tarefa é gerar um relatório técnico em formato JSON com os seguintes pontos:

1. RESUMO DA SAÚDE GERAL: Avaliação qualitativa e quantitativa do parque de máquinas.
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
def dashboard_ia():
    """
    Exibe o dashboard com análises da IA
    """
    dados = preparar_dados_para_ia()
    analise = gerar_analise_ia(dados)
    
    return render_template('ia_dashboard.html', 
                         dados=dados, 
                         analise=analise)

@ia_bp.route('/api/ia/analise')
def api_analise_ia():
    """
    API: Retorna análise da IA em JSON
    """
    dados = preparar_dados_para_ia()
    analise = gerar_analise_ia(dados)
    
    return jsonify({
        'dados': dados,
        'analise': analise
    })

@ia_bp.route('/api/ia/dados')
def api_dados_ia():
    """
    API: Retorna apenas os dados preparados para IA
    """
    dados = preparar_dados_para_ia()
    return jsonify(dados)
