from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from models.equipamento import Equipamento
from models.manutencao import Manutencao
from models.setor import Setor
from models.funcionario import Funcionario
from models.database import db
from datetime import datetime
import csv
import io

# Blueprint para rotas de equipamentos
equipamento_bp = Blueprint('equipamento', __name__)

@equipamento_bp.route('/equipamentos')
def listar_equipamentos():
    """Lista todos os equipamentos"""
    equipamentos = Equipamento.get_all()
    return render_template('equipamentos.html', equipamentos=equipamentos)

@equipamento_bp.route('/equipamentos/exportar')
@login_required
def exportar_equipamentos():
    """
    Exporta o inventário de equipamentos em CSV (Excel)
    """
    equipamentos = Equipamento.get_all()

    # Prepara o arquivo na memória
    si = io.StringIO()
    cw = csv.writer(si, delimiter=';')
    
    # Cabeçalho baseado ESTRITAMENTE nas colunas da sua tabela HTML
    cw.writerow(['Código', 'Nome do Equipamento', 'Setor', 'Responsável', 'Status', 'Qtd. Manutenções'])
    
    for eq in equipamentos:
        # Extrai os dados garantindo que não quebre se for nulo
        setor = eq.setor_rel.nome if hasattr(eq, 'setor_rel') and eq.setor_rel else "N/A"
        responsavel = eq.responsavel_rel.nome if hasattr(eq, 'responsavel_rel') and eq.responsavel_rel else "N/A"
        # Conta manutenções se a relação existir
        qtd_manutencoes = len(eq.manutencoes) if hasattr(eq, 'manutencoes') else 0
        
        cw.writerow([
            eq.codigo,
            eq.nome,
            setor,
            responsavel,
            eq.status.upper() if eq.status else 'N/A',
            qtd_manutencoes
        ])
        
    # Gera a resposta para download
    output = make_response(si.getvalue().encode('utf-8-sig'))
    output.headers["Content-Disposition"] = f"attachment; filename=inventario_equipamentos_{datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@equipamento_bp.route('/equipamentos/novo', methods=['GET', 'POST'])
@login_required
def novo_equipamento():
    """Cadastra um novo equipamento - SOMENTE ADMIN"""
    if not current_user.is_admin:
        flash('Acesso negado! Apenas administradores podem cadastrar equipamentos.', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))

    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            codigo = request.form.get('codigo')
            setor_id = request.form.get('setor_id')
            responsavel_id = request.form.get('responsavel_id')
            status = request.form.get('status', 'ativo')
            
            if not all([nome, codigo, setor_id, responsavel_id]):
                flash('Todos os campos são obrigatórios!', 'danger')
                return redirect(url_for('equipamento.novo_equipamento'))
            
            if Equipamento.get_by_codigo(codigo):
                flash(f'Já existe um equipamento com o código {codigo}!', 'danger')
                return redirect(url_for('equipamento.novo_equipamento'))
            
            equipamento = Equipamento(
                nome=nome,
                codigo=codigo,
                setor_id=setor_id,
                responsavel_id=responsavel_id,
                status=status
            )
            
            equipamento.save()
            flash(f'Equipamento {codigo} cadastrado com sucesso!', 'success')
            return redirect(url_for('equipamento.listar_equipamentos'))
            
        except Exception as e:
            flash(f'Erro ao cadastrar equipamento: {str(e)}', 'danger')
    
    setores = Setor.get_all()
    funcionarios = Funcionario.get_all()
    return render_template('cadastro_equipamento.html', setores=setores, funcionarios=funcionarios)

@equipamento_bp.route('/equipamentos/<int:equipamento_id>')
@login_required
def detalhe_equipamento(equipamento_id):
    """Exibe detalhes de um equipamento"""
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
@login_required
def editar_equipamento(equipamento_id):
    """Edita um equipamento existente - SOMENTE ADMIN"""
    if not current_user.is_admin:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))

    equipamento = Equipamento.get_by_id(equipamento_id)
    if not equipamento:
        flash('Equipamento não encontrado!', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))
    
    if request.method == 'POST':
        try:
            equipamento.nome = request.form.get('nome')
            equipamento.codigo = request.form.get('codigo')
            equipamento.setor_id = request.form.get('setor_id')
            equipamento.responsavel_id = request.form.get('responsavel_id')
            equipamento.status = request.form.get('status')
            
            equipamento.save()
            flash(f'Equipamento {equipamento.codigo} atualizado!', 'success')
            return redirect(url_for('equipamento.listar_equipamentos'))
        except Exception as e:
            flash(f'Erro ao atualizar: {str(e)}', 'danger')
    
    setores = Setor.get_all()
    funcionarios = Funcionario.get_all()
    return render_template('cadastro_equipamento.html', equipamento=equipamento, setores=setores, funcionarios=funcionarios)

@equipamento_bp.route('/equipamentos/<int:equipamento_id>/deletar', methods=['POST'])
@login_required
def deletar_equipamento(equipamento_id):
    """Deleta um equipamento - SOMENTE ADMIN"""
    if not current_user.is_admin:
        flash('Acesso negado!', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))

    equipamento = Equipamento.get_by_id(equipamento_id)
    if equipamento:
        codigo = equipamento.codigo
        equipamento.delete()
        flash(f'Equipamento {codigo} deletado!', 'success')
    
    return redirect(url_for('equipamento.listar_equipamentos'))

@equipamento_bp.route('/equipamentos/<int:equipamento_id>/concluir', methods=['POST'])
@login_required
def concluir_manutencao(equipamento_id):
    """Altera o status do equipamento para 'ativo' - Responsável ou Admin"""
    equipamento = Equipamento.get_by_id(equipamento_id)
    if not equipamento:
        flash('Equipamento não encontrado!', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))
    
    # Verifica se o usuário é o responsável ou admin
    if current_user.id == equipamento.responsavel_id or current_user.is_admin:
        equipamento.status = 'ativo'
        try:
            equipamento.save()
            flash(f'Manutenção concluída! O equipamento {equipamento.codigo} agora está ATIVO.', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar status: {str(e)}', 'danger')
    else:
        flash('Acesso negado! Apenas o responsável ou um administrador podem concluir a manutenção.', 'danger')
        
    return redirect(url_for('equipamento.detalhe_equipamento', equipamento_id=equipamento_id))