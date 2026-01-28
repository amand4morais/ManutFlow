from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.equipamento import Equipamento
from models.manutencao import Manutencao
from models.database import db

# Blueprint para rotas de equipamentos
equipamento_bp = Blueprint('equipamento', __name__)

@equipamento_bp.route('/equipamentos')
def listar_equipamentos():
    """
    Lista todos os equipamentos
    """
    equipamentos = Equipamento.get_all()
    return render_template('equipamentos.html', equipamentos=equipamentos)

@equipamento_bp.route('/equipamentos/novo', methods=['GET', 'POST'])
def novo_equipamento():
    """
    Cadastra um novo equipamento
    """
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            nome = request.form.get('nome')
            codigo = request.form.get('codigo')
            setor = request.form.get('setor')
            responsavel = request.form.get('responsavel')
            status = request.form.get('status', 'ativo')
            
            # Validações
            if not all([nome, codigo, setor, responsavel]):
                flash('Todos os campos são obrigatórios!', 'danger')
                return render_template('cadastro_equipamento.html')
            
            # Verifica se o código já existe
            if Equipamento.get_by_codigo(codigo):
                flash(f'Já existe um equipamento com o código {codigo}!', 'danger')
                return render_template('cadastro_equipamento.html')
            
            # Cria novo equipamento
            equipamento = Equipamento(
                nome=nome,
                codigo=codigo,
                setor=setor,
                responsavel=responsavel,
                status=status
            )
            
            equipamento.save()
            flash(f'Equipamento {codigo} cadastrado com sucesso!', 'success')
            return redirect(url_for('equipamento.listar_equipamentos'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar equipamento: {str(e)}', 'danger')
            return render_template('cadastro_equipamento.html')
    
    return render_template('cadastro_equipamento.html')

@equipamento_bp.route('/equipamentos/<int:equipamento_id>')
def detalhe_equipamento(equipamento_id):
    """
    Exibe detalhes de um equipamento
    """
    equipamento = Equipamento.get_by_id(equipamento_id)
    
    if not equipamento:
        flash('Equipamento não encontrado!', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))
    
    manutencoes = Manutencao.get_by_equipamento(equipamento_id)
    custo_total = Manutencao.get_custo_por_equipamento(equipamento_id)
    
    return render_template('detalhe_equipamento.html', 
                         equipamento=equipamento, 
                         manutencoes=manutencoes,
                         custo_total=custo_total)

@equipamento_bp.route('/equipamentos/<int:equipamento_id>/editar', methods=['GET', 'POST'])
def editar_equipamento(equipamento_id):
    """
    Edita um equipamento existente
    """
    equipamento = Equipamento.get_by_id(equipamento_id)
    
    if not equipamento:
        flash('Equipamento não encontrado!', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))
    
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            nome = request.form.get('nome')
            codigo = request.form.get('codigo')
            setor = request.form.get('setor')
            responsavel = request.form.get('responsavel')
            status = request.form.get('status')
            
            # Validações
            if not all([nome, codigo, setor, responsavel, status]):
                flash('Todos os campos são obrigatórios!', 'danger')
                return render_template('cadastro_equipamento.html', equipamento=equipamento)
            
            # Verifica se o código já existe em outro equipamento
            equipamento_existente = Equipamento.get_by_codigo(codigo)
            if equipamento_existente and equipamento_existente.id != equipamento_id:
                flash(f'Já existe outro equipamento com o código {codigo}!', 'danger')
                return render_template('cadastro_equipamento.html', equipamento=equipamento)
            
            # Atualiza dados
            equipamento.nome = nome
            equipamento.codigo = codigo
            equipamento.setor = setor
            equipamento.responsavel = responsavel
            equipamento.status = status
            
            equipamento.save()
            flash(f'Equipamento {codigo} atualizado com sucesso!', 'success')
            return redirect(url_for('equipamento.listar_equipamentos'))
            
        except Exception as e:
            flash(f'Erro ao atualizar equipamento: {str(e)}', 'danger')
            return render_template('cadastro_equipamento.html', equipamento=equipamento)
    
    return render_template('cadastro_equipamento.html', equipamento=equipamento)

@equipamento_bp.route('/equipamentos/<int:equipamento_id>/deletar', methods=['POST'])
def deletar_equipamento(equipamento_id):
    """
    Deleta um equipamento
    """
    equipamento = Equipamento.get_by_id(equipamento_id)
    
    if not equipamento:
        flash('Equipamento não encontrado!', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))
    
    try:
        codigo = equipamento.codigo
        equipamento.delete()
        flash(f'Equipamento {codigo} deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar equipamento: {str(e)}', 'danger')
    
    return redirect(url_for('equipamento.listar_equipamentos'))

@equipamento_bp.route('/api/equipamentos')
def api_listar_equipamentos():
    """
    API: Retorna lista de equipamentos em JSON
    """
    equipamentos = Equipamento.get_all()
    return jsonify([eq.to_dict() for eq in equipamentos])

@equipamento_bp.route('/api/equipamentos/<int:equipamento_id>')
def api_detalhe_equipamento(equipamento_id):
    """
    API: Retorna detalhes de um equipamento em JSON
    """
    equipamento = Equipamento.get_by_id(equipamento_id)
    
    if not equipamento:
        return jsonify({'erro': 'Equipamento não encontrado'}), 404
    
    return jsonify(equipamento.to_dict())
