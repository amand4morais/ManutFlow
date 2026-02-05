from flask import Blueprint, render_template, jsonify, current_app, redirect, url_for, flash, request, make_response
from flask_login import current_user, login_required
from models.equipamento import Equipamento
from models.manutencao import Manutencao
from models.database import db
from groq import Groq
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import csv
import io

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

def calcular_predicoes(equipamento, manutencoes):
    """
    Calcula o MTBF (Tempo Médio Entre Falhas) e estima a próxima falha
    """
    # Filtra apenas corretivas e ordena por data (mais recente primeiro)
    corretivas = sorted(
        [m for m in manutencoes if m.tipo == 'corretiva'], 
        key=lambda x: x.data_manutencao, 
        reverse=True
    )
    
    if len(corretivas) < 2:
        return None # Dados insuficientes para prever

    # Calcula intervalos em dias entre falhas
    intervalos = []
    for i in range(len(corretivas) - 1):
        delta = (corretivas[i].data_manutencao - corretivas[i+1].data_manutencao).days
        if delta > 0: # Evita erros de mesma data
            intervalos.append(delta)
    
    if not intervalos:
        return None

    # MTBF em dias
    mtbf = sum(intervalos) / len(intervalos)
    
    # Data da última falha
    ultima_falha = corretivas[0].data_manutencao
    
    # Previsão: Última falha + MTBF
    proxima_falha_estimada = ultima_falha + timedelta(days=mtbf)
    dias_restantes = (proxima_falha_estimada - datetime.now().date()).days
    
    # Determina risco
    if dias_restantes < 0:
        risco = 'crítico' # Já deveria ter quebrado
        confianca = 'Alta (Atrasado)'
    elif dias_restantes < 7:
        risco = 'alto'
        confianca = 'Alta'
    elif dias_restantes < 30:
        risco = 'médio'
        confianca = 'Média'
    else:
        risco = 'baixo'
        confianca = 'Baixa'

    return {
        'mtbf': round(mtbf, 1),
        'ultima_falha': ultima_falha.strftime('%d/%m/%Y'),
        'proxima_falha': proxima_falha_estimada.strftime('%d/%m/%Y'),
        'dias_restantes': dias_restantes,
        'risco': risco,
        'confianca': confianca
    }

def preparar_dados_para_ia(data_inicio=None, data_fim=None):
    """
    Prepara os dados de equipamentos e manutenções para análise da IA
    """
    # Retornamos todos os equipamentos
    equipamentos = Equipamento.get_all()
    
    # Busca manutenções filtradas ou totais
    if data_inicio or data_fim:
        manutencoes = Manutencao.get_filtered(data_inicio, data_fim)
    else:
        manutencoes = Manutencao.get_all()
    
    # Estatísticas gerais
    total_equipamentos = len(equipamentos)
    equipamentos_ativos = len([e for e in equipamentos if e.status == 'ativo'])
    equipamentos_em_manutencao = len([e for e in equipamentos if e.status == 'em_manutencao'])
    equipamentos_sucateados = len([e for e in equipamentos if e.status == 'sucateado'])
    
    total_manutencoes = len(manutencoes)
    manutencoes_preventivas = len([m for m in manutencoes if m.tipo == 'preventiva'])
    manutencoes_corretivas = len([m for m in manutencoes if m.tipo == 'corretiva'])
    
    # Custo total
    custo_total = sum(m.custo for m in manutencoes)
    
    # Análise detalhada por equipamento e Predição
    equipamentos_detalhes = []
    lista_predicoes = []
    setores_stats = defaultdict(lambda: {'total_equipamentos': 0, 'custo_total': 0, 'total_manutencoes': 0})
    
    for eq in equipamentos:
        # Busca TODAS manutenções do equipamento para cálculo de histórico (independente do filtro visual)
        todas_manutencoes_eq = Manutencao.get_by_equipamento(eq.id)
        
        # Filtra apenas as do período para exibir na tabela de resumo
        manutencoes_eq_filtradas = todas_manutencoes_eq
        if data_inicio:
            manutencoes_eq_filtradas = [m for m in manutencoes_eq_filtradas if m.data_manutencao >= data_inicio]
        if data_fim:
            manutencoes_eq_filtradas = [m for m in manutencoes_eq_filtradas if m.data_manutencao <= data_fim]
            
        custo_eq = sum(m.custo for m in manutencoes_eq_filtradas)
        
        # Dados básicos
        eq_data = {
            'codigo': eq.codigo,
            'nome': eq.nome,
            'setor': eq.setor_rel.nome if hasattr(eq, 'setor_rel') and eq.setor_rel else "N/A",
            'status': eq.status,
            'total_manutencoes': len(manutencoes_eq_filtradas),
            'manutencoes_preventivas': len([m for m in manutencoes_eq_filtradas if m.tipo == 'preventiva']),
            'manutencoes_corretivas': len([m for m in manutencoes_eq_filtradas if m.tipo == 'corretiva']),
            'custo_total': custo_eq
        }
        equipamentos_detalhes.append(eq_data)
        
        # CALCULO PREDITIVO (Usa todo o histórico para precisão)
        predicao = calcular_predicoes(eq, todas_manutencoes_eq)
        if predicao:
            predicao['codigo'] = eq.codigo
            predicao['nome'] = eq.nome
            predicao['setor'] = eq_data['setor']
            lista_predicoes.append(predicao)
        
        # Dados para análise de setor
        setor_nome = eq_data['setor']
        setores_stats[setor_nome]['total_equipamentos'] += 1
        setores_stats[setor_nome]['custo_total'] += custo_eq
        setores_stats[setor_nome]['total_manutencoes'] += len(manutencoes_eq_filtradas)
    
    # Ordena predições por urgência (dias restantes menor primeiro)
    lista_predicoes.sort(key=lambda x: x['dias_restantes'])

    # Manutenções recentes para KPI
    data_limite_recente = datetime.now().date() - timedelta(days=30)
    manutencoes_recentes = [m for m in manutencoes if m.data_manutencao >= data_limite_recente]
    
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
        'predicoes': lista_predicoes, # Nova lista de dados preditivos
        'setores': dict(setores_stats),
        'periodo': {
            'inicio': data_inicio.strftime('%d/%m/%Y') if data_inicio else 'Início',
            'fim': data_fim.strftime('%d/%m/%Y') if data_fim else 'Hoje'
        }
    }
    
    return dados

def gerar_analise_ia(dados):
    """
    Usa a IA do Groq para gerar análise e sugestões baseadas nos dados e predições
    """
    # Verifica se há manutenções OU predições. Se ambos vazios, não analisa.
    if dados['estatisticas_gerais']['total_manutencoes'] == 0 and not dados['predicoes']:
        return {
            'resumo_saude': None,
            'equipamentos_criticos': [],
            'analise_setores': [],
            'recomendacoes': []
        }

    groq_client = get_groq_client()
    
    if not groq_client:
        return {
            'resumo_saude': 'A chave da API do Groq não foi configurada.',
            'equipamentos_criticos': [],
            'analise_setores': [],
            'recomendacoes': ['Configure a chave da API.']
        }

    try:
        periodo_texto = f"Período de análise: de {dados['periodo']['inicio']} até {dados['periodo']['fim']}."
        
        # Injeta as predições calculadas no prompt
        top_predicoes = dados['predicoes'][:5] # Top 5 mais urgentes
        texto_preditivo = "ANÁLISE PREDITIVA (Baseada em MTBF):\n"
        for p in top_predicoes:
            texto_preditivo += f"- {p['nome']} ({p['codigo']}): Risco {p['risco'].upper()}. Falha prevista em {p['dias_restantes']} dias. MTBF de {p['mtbf']} dias.\n"

        prompt = f"""
Você é um especialista em manutenção preditiva. Analise os dados e as PREDIÇÕES calculadas.

CONTEXTO:
{periodo_texto}

{texto_preditivo}

DADOS GERAIS:
{json.dumps(dados['estatisticas_gerais'], indent=2)}

Gere um JSON com:
1. RESUMO DA SAÚDE: Inclua comentários sobre as predições de falha.
2. EQUIPAMENTOS CRÍTICOS: Use os dados preditivos para apontar quem vai quebrar logo.
3. ANÁLISE POR SETOR.
4. RECOMENDAÇÕES: Ações preventivas baseadas nas predições.

IMPORTANTE: Responda EXCLUSIVAMENTE em formato JSON puro.
{{
    "resumo_saude": "texto detalhado citando as máquinas com risco de falha iminente",
    "equipamentos_criticos": [
        {{"codigo": "código", "nome": "nome", "prioridade": "alta/média/baixa", "justificativa": "Baseado na predição de falha em X dias"}}
    ],
    "analise_setores": [
        {{"setor": "nome", "custo_total": valor, "recomendacao": "ação sugerida"}}
    ],
    "recomendacoes": ["recomendação 1", "recomendação 2", "recomendação 3", "recomendação 4"]
}}
"""
        
        completion = groq_client.chat.completions.create(
            model=current_app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[
                {"role": "system", "content": "Você é um engenheiro de manutenção focado em predição."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        resposta_texto = completion.choices[0].message.content.strip()
        analise = json.loads(resposta_texto)
        return analise
        
    except Exception as e:
        print(f"Erro ao gerar análise do Groq: {str(e)}")
        return {
            'resumo_saude': f'Erro na análise IA: {str(e)}',
            'equipamentos_criticos': [],
            'analise_setores': [],
            'recomendacoes': []
        }

@ia_bp.route('/ia/dashboard')
@login_required
def dashboard_ia():
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        flash("Acesso negado!", "danger")
        return redirect(url_for('index'))

    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    filtro_pre = request.args.get('filtro_pre', '')
    
    data_inicio = None
    data_fim = None
    
    if data_inicio_str:
        try: data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        except ValueError: pass
            
    if data_fim_str:
        try: data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError: pass
            
    dados = preparar_dados_para_ia(data_inicio, data_fim)
    analise = gerar_analise_ia(dados)
    
    return render_template('ia_dashboard.html', 
                         dados=dados, 
                         analise=analise,
                         data_inicio=data_inicio_str,
                         data_fim=data_fim_str,
                         filtro_pre=filtro_pre)

@ia_bp.route('/ia/exportar')
@login_required
def exportar_analise_ia():
    """
    Exporta os dados da análise IA e predições em CSV
    """
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return redirect(url_for('index'))

    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    data_inicio = None
    data_fim = None
    
    if data_inicio_str:
        try: data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        except ValueError: pass
    if data_fim_str:
        try: data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError: pass
    
    dados = preparar_dados_para_ia(data_inicio, data_fim)
    
    si = io.StringIO()
    cw = csv.writer(si, delimiter=';')
    
    # Seção 1: Resumo Geral
    cw.writerow(['RESUMO GERAL DO PERÍODO'])
    cw.writerow(['Total Equipamentos', 'Preventivas', 'Corretivas', 'Custo Total', 'Manutenções (30d)'])
    cw.writerow([
        dados['estatisticas_gerais']['total_equipamentos'],
        dados['estatisticas_gerais']['manutencoes_preventivas'],
        dados['estatisticas_gerais']['manutencoes_corretivas'],
        f"{dados['estatisticas_gerais']['custo_total']:.2f}".replace('.', ','),
        dados['estatisticas_gerais']['manutencoes_ultimos_30_dias']
    ])
    cw.writerow([])
    
    # Seção 2: Análise Preditiva
    cw.writerow(['ANÁLISE PREDITIVA (RISCO DE FALHA)'])
    cw.writerow(['Equipamento', 'Código', 'Setor', 'MTBF (Dias)', 'Última Falha', 'Próxima Falha (Est.)', 'Risco', 'Dias Restantes'])
    
    for p in dados['predicoes']:
        cw.writerow([
            p['nome'],
            p['codigo'],
            p['setor'],
            p['mtbf'],
            p['ultima_falha'],
            p['proxima_falha'],
            p['risco'].upper(),
            p['dias_restantes']
        ])
    
    output = make_response(si.getvalue().encode('utf-8-sig'))
    output.headers["Content-Disposition"] = f"attachment; filename=relatorio_ia_preditiva_{datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@ia_bp.route('/api/ia/analise')
@login_required
def api_analise_ia():
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    dados = preparar_dados_para_ia()
    analise = gerar_analise_ia(dados)
    return jsonify({'dados': dados, 'analise': analise})

@ia_bp.route('/api/ia/dados')
@login_required
def api_dados_ia():
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    dados = preparar_dados_para_ia()
    return jsonify(dados)