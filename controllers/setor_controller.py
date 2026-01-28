from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.setor import Setor

setor_bp = Blueprint('setor', __name__)

@setor_bp.route('/setores')
@login_required
def lista():
    setores = Setor.get_all()
    return render_template('setores.html', setores=setores)

@setor_bp.route('/setores/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if not current_user.is_admin:
        flash("Acesso negado!", "danger")
        return redirect(url_for('setor.lista'))
        
    if request.method == 'POST':
        nome = request.form.get('nome')
        novo_setor = Setor(nome=nome)
        novo_setor.save()
        flash("Setor criado com sucesso!", "success")
        return redirect(url_for('setor.lista'))
    return render_template('cadastro_setor.html')
