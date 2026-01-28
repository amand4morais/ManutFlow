from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.manutencao import Manutencao
from models.equipamento import Equipamento
from models.database import db
from datetime import datetime

# Blueprint para rotas de manutenções
manutencao_bp = Blueprint('manutencao', __name__)

@manutencao_bp.route('/manutencoes')
@login_required
def listar_manutencoes():
    """Lista todas as manutenções"""
    manutencoes = Manutencao.get_all()
    return render_template('manutencoes.html', manutencoes=manutencoes)

@manutencao_bp.route('/manutencoes/nova', methods=['GET', 'POST'])
@login_required
def nova_manutencao():
    """Cadastra uma nova manutenção - FUNCIONÁRIOS E ADMIN PODEM"""
    equipamentos = Equipamento.get_all()
    
    if request.method == 'POST':
        try:
            equipamento_id = request.form.get('equipamento_id')
            tipo = request.form.get('tipo')
            data_manutencao_str = request.form.get('data_manutencao')
            descricao = request.form.get('descricao')
            custo_str = request.form.get('custo', '0')
            
            if not all([equipamento_id, tipo, data_manutencao_str, descricao]):
                flash('Todos os campos obrigatórios devem ser preenchidos!', 'danger')
                return render_template('cadastro_manutencao.html', equipamentos=equipamentos)
            
            data_manutencao = datetime.strptime(data_manutencao_str, '%Y-%m-%d').date()
            custo = float(custo_str.replace(',', '.'))
            
            manutencao = Manutencao(
                equipamento_id=equipamento_id,
                tipo=tipo,
                data_manutencao=data_manutencao,
                descricao=descricao,
                custo=custo,
                autor_id=current_user.id # PEGA O ID DO USUÁRIO LOGADO
            )
            
            manutencao.save()
            
            # Atualiza status do equipamento se for corretiva
            if tipo == 'corretiva':
                equipamento = Equipamento.get_by_id(equipamento_id)
                if equipamento and equipamento.status == 'ativo':
                    equipamento.status = 'em_manutencao'
                    equipamento.save()
            
            flash(f'Manutenção registrada com sucesso!', 'success')
            return redirect(url_for('manutencao.listar_manutencoes'))
            
        except Exception as e:
            flash(f'Erro ao registrar manutenção: {str(e)}', 'danger')
    
    return render_template('cadastro_manutencao.html', equipamentos=equipamentos)

@manutencao_bp.route('/manutencoes/<int:manutencao_id>/deletar', methods=['POST'])
@login_required
def deletar_manutencao(manutencao_id):
    """Deleta uma manutenção - SOMENTE ADMIN"""
    if not current_user.is_admin:
        flash('Acesso negado! Apenas administradores podem excluir registros.', 'danger')
        return redirect(url_for('manutencao.listar_manutencoes'))

    manutencao = Manutencao.get_by_id(manutencao_id)
    if manutencao:
        manutencao.delete()
        flash(f'Manutenção deletada!', 'success')
    
    return redirect(url_for('manutencao.listar_manutencoes'))
