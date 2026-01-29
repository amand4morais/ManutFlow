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
        # Mantendo comparação simples para compatibilidade com o seed.py existente
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
        setor_id = request.form.get('setor_id') # Captura o setor

        # Validações básicas
        if not all([nome, email, senha, setor_id]):
            flash('Preencha todos os campos.', 'danger')
            return redirect(url_for('auth.cadastro'))

        user_exists = Funcionario.query.filter_by(email=email).first()

        if user_exists:
            flash('Este email já está cadastrado.', 'danger')
            return redirect(url_for('auth.cadastro'))

        # Cria novo funcionário (sem privilégios de admin por padrão)
        # O setor não é salvo diretamente na tabela funcionario neste modelo simples,
        # mas estamos capturando para validar o fluxo. Se precisasse salvar,
        # teria que adicionar setor_id no model Funcionario.
        # Vou assumir que o cadastro é apenas de usuário básico.
        
        new_user = Funcionario(
            nome=nome,
            email=email,
            senha=senha,
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

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))