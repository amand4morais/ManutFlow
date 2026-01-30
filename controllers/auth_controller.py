from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.funcionario import Funcionario
from models.setor import Setor
from models.database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')

        user = Funcionario.query.filter_by(email=email).first()

        # Nota: Em um ambiente de produção real, deve-se usar hash de senha (werkzeug.security)
        if user and user.senha == senha:
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'danger')

    return render_template('login.html')

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form.get('username')
        email = request.form.get('email')
        senha = request.form.get('password')
        setor_id = request.form.get('setor_id')

        # Validações básicas
        if not all([nome, email, senha, setor_id]):
            flash('Preencha todos os campos.', 'danger')
            return redirect(url_for('auth.cadastro'))

        user_exists = Funcionario.query.filter_by(email=email).first()

        if user_exists:
            flash('Este email já está cadastrado.', 'danger')
            return redirect(url_for('auth.cadastro'))

        new_user = Funcionario(
            nome=nome,
            email=email,
            senha=senha,
            setor_id=setor_id,
            is_admin=False
        )

        try:
            new_user.save()
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')

    # Busca setores para o dropdown
    setores = Setor.get_all()
    return render_template('cadastro.html', setores=setores)

@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if not all([email, nova_senha, confirmar_senha]):
            flash('Preencha todos os campos.', 'danger')
            return render_template('recuperar_senha.html')
            
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('recuperar_senha.html')
            
        user = Funcionario.query.filter_by(email=email).first()
        
        if user:
            try:
                user.senha = nova_senha
                user.save()
                flash('Senha atualizada com sucesso! Faça login com a nova senha.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash(f'Erro ao atualizar senha: {str(e)}', 'danger')
        else:
            # Por segurança, geralmente não se avisa que o e-mail não existe, 
            # mas para facilitar o uso interno, vamos avisar.
            flash('E-mail não encontrado no sistema.', 'danger')
            
    return render_template('recuperar_senha.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))