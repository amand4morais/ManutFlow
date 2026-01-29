from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.setor import Setor

setor_bp = Blueprint('setor', __name__)

@setor_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin:
        flash("Acesso negado! Apenas administradores podem gerenciar setores.", "danger")
        return redirect(url_for('index'))

@setor_bp.route('/setores')
def lista():
    setores = Setor.get_all()
    return render_template('setores.html', setores=setores)

@setor_bp.route('/setores/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            if not nome:
                flash("O nome do setor é obrigatório!", "danger")
                return redirect(url_for('setor.novo'))
            
            novo_setor = Setor(nome=nome)
            novo_setor.save()
            flash(f"Setor '{nome}' criado com sucesso!", "success")
            return redirect(url_for('setor.lista'))
        except Exception as e:
            flash(f"Erro ao criar setor: {str(e)}", "danger")
            
    return render_template('setores.html', show_modal=True, action='novo')

@setor_bp.route('/setores/<int:setor_id>/editar', methods=['GET', 'POST'])
def editar(setor_id):
    setor = Setor.get_by_id(setor_id)
    if not setor:
        flash("Setor não encontrado!", "danger")
        return redirect(url_for('setor.lista'))
        
    if request.method == 'POST':
        try:
            setor.nome = request.form.get('nome')
            setor.save()
            flash(f"Setor atualizado para '{setor.nome}'!", "success")
            return redirect(url_for('setor.lista'))
        except Exception as e:
            flash(f"Erro ao atualizar setor: {str(e)}", "danger")
            
    return render_template('setores.html', setores=Setor.get_all(), edit_setor=setor)

@setor_bp.route('/setores/<int:setor_id>/deletar', methods=['POST'])
def deletar(setor_id):
    setor = Setor.get_by_id(setor_id)
    if setor:
        try:
            nome = setor.nome
            # Verifica se há equipamentos ou funcionários vinculados
            if setor.equipamentos or setor.funcionarios:
                flash(f"Não é possível excluir o setor '{nome}' pois existem equipamentos ou funcionários vinculados a ele.", "warning")
            else:
                setor.delete()
                flash(f"Setor '{nome}' excluído com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao excluir setor: {str(e)}", "danger")
    
    return redirect(url_for('setor.lista'))