from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.manutencao import Manutencao
from models.equipamento import Equipamento
from models.database import db
from datetime import datetime

# Blueprint para rotas de manutenções
manutencao_bp = Blueprint('manutencao', __name__)

@manutencao_bp.route('/manutencoes')
def listar_manutencoes():
    """
    Lista manutenções com filtro de data
    """
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
    
    # Busca com filtro ou busca tudo
    if data_inicio or data_fim:
        manutencoes = Manutencao.get_filtered(data_inicio, data_fim)
    else:
        manutencoes = Manutencao.get_all()
        
    return render_template('manutencoes.html', 
                         manutencoes=manutencoes,
                         data_inicio=data_inicio_str,
                         data_fim=data_fim_str,
                         filtro_pre=filtro_pre)

@manutencao_bp.route('/manutencoes/nova', methods=['GET', 'POST'])
def nova_manutencao():
    """
    Cadastra uma nova manutenção
    """
    equipamentos = Equipamento.get_all()
    
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            equipamento_id = request.form.get('equipamento_id')
            tipo = request.form.get('tipo')
            data_manutencao_str = request.form.get('data_manutencao')
            descricao = request.form.get('descricao')
            custo_str = request.form.get('custo', '0')
            
            # Validações
            if not all([equipamento_id, tipo, data_manutencao_str, descricao]):
                flash('Todos os campos obrigatórios devem ser preenchidos!', 'danger')
                return render_template('cadastro_manutencao.html', equipamentos=equipamentos)
            
            # Converte data
            try:
                data_manutencao = datetime.strptime(data_manutencao_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Data inválida!', 'danger')
                return render_template('cadastro_manutencao.html', equipamentos=equipamentos)
            
            # Converte custo
            try:
                custo = float(custo_str.replace(',', '.'))
            except ValueError:
                custo = 0.0
            
            # Verifica se o equipamento existe
            equipamento = Equipamento.get_by_id(equipamento_id)
            if not equipamento:
                flash('Equipamento não encontrado!', 'danger')
                return render_template('cadastro_manutencao.html', equipamentos=equipamentos)
            
            # Cria nova manutenção
            manutencao = Manutencao(
                equipamento_id=equipamento_id,
                tipo=tipo,
                data_manutencao=data_manutencao,
                descricao=descricao,
                custo=custo
            )
            
            manutencao.save()
            
            # Se o tipo for corretiva, atualiza status do equipamento para "em_manutencao"
            if tipo == 'corretiva' and equipamento.status == 'ativo':
                equipamento.status = 'em_manutencao'
                equipamento.save()
            
            flash(f'Manutenção registrada com sucesso!', 'success')
            return redirect(url_for('manutencao.listar_manutencoes'))
            
        except Exception as e:
            flash(f'Erro ao registrar manutenção: {str(e)}', 'danger')
            return render_template('cadastro_manutencao.html', equipamentos=equipamentos)
    
    return render_template('cadastro_manutencao.html', equipamentos=equipamentos)

@manutencao_bp.route('/manutencoes/<int:manutencao_id>')
def detalhe_manutencao(manutencao_id):
    """
    Exibe detalhes de uma manutenção
    """
    manutencao = Manutencao.get_by_id(manutencao_id)
    
    if not manutencao:
        flash('Manutenção não encontrada!', 'danger')
        return redirect(url_for('manutencao.listar_manutencoes'))
    
    return render_template('detalhe_manutencao.html', manutencao=manutencao)

@manutencao_bp.route('/manutencoes/<int:manutencao_id>/editar', methods=['GET', 'POST'])
def editar_manutencao(manutencao_id):
    """
    Edita uma manutenção existente
    """
    manutencao = Manutencao.get_by_id(manutencao_id)
    equipamentos = Equipamento.get_all()
    
    if not manutencao:
        flash('Manutenção não encontrada!', 'danger')
        return redirect(url_for('manutencao.listar_manutencoes'))
    
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            equipamento_id = request.form.get('equipamento_id')
            tipo = request.form.get('tipo')
            data_manutencao_str = request.form.get('data_manutencao')
            descricao = request.form.get('descricao')
            custo_str = request.form.get('custo', '0')
            
            # Validações
            if not all([equipamento_id, tipo, data_manutencao_str, descricao]):
                flash('Todos os campos obrigatórios devem ser preenchidos!', 'danger')
                return render_template('cadastro_manutencao.html', manutencao=manutencao, equipamentos=equipamentos)
            
            # Converte data
            try:
                data_manutencao = datetime.strptime(data_manutencao_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Data inválida!', 'danger')
                return render_template('cadastro_manutencao.html', manutencao=manutencao, equipamentos=equipamentos)
            
            # Converte custo
            try:
                custo = float(custo_str.replace(',', '.'))
            except ValueError:
                custo = 0.0
            
            # Verifica se o equipamento existe
            equipamento = Equipamento.get_by_id(equipamento_id)
            if not equipamento:
                flash('Equipamento não encontrado!', 'danger')
                return render_template('cadastro_manutencao.html', manutencao=manutencao, equipamentos=equipamentos)
            
            # Atualiza dados
            manutencao.equipamento_id = equipamento_id
            manutencao.tipo = tipo
            manutencao.data_manutencao = data_manutencao
            manutencao.descricao = descricao
            manutencao.custo = custo
            
            manutencao.save()
            flash(f'Manutenção atualizada com sucesso!', 'success')
            return redirect(url_for('manutencao.listar_manutencoes'))
            
        except Exception as e:
            flash(f'Erro ao atualizar manutenção: {str(e)}', 'danger')
            return render_template('cadastro_manutencao.html', manutencao=manutencao, equipamentos=equipamentos)
    
    return render_template('cadastro_manutencao.html', manutencao=manutencao, equipamentos=equipamentos)

@manutencao_bp.route('/manutencoes/<int:manutencao_id>/deletar', methods=['POST'])
def deletar_manutencao(manutencao_id):
    """
    Deleta uma manutenção
    """
    manutencao = Manutencao.get_by_id(manutencao_id)
    
    if not manutencao:
        flash('Manutenção não encontrada!', 'danger')
        return redirect(url_for('manutencao.listar_manutencoes'))
    
    try:
        manutencao.delete()
        flash(f'Manutenção deletada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar manutenção: {str(e)}', 'danger')
    
    return redirect(url_for('manutencao.listar_manutencoes'))

@manutencao_bp.route('/api/manutencoes')
def api_listar_manutencoes():
    """
    API: Retorna lista de manutenções em JSON
    """
    manutencoes = Manutencao.get_all()
    return jsonify([m.to_dict() for m in manutencoes])

@manutencao_bp.route('/api/manutencoes/<int:manutencao_id>')
def api_detalhe_manutencao(manutencao_id):
    """
    API: Retorna detalhes de uma manutenção em JSON
    """
    manutencao = Manutencao.get_by_id(manutencao_id)
    
    if not manutencao:
        return jsonify({'erro': 'Manutenção não encontrada'}), 404
    
    return jsonify(manutencao.to_dict())
