from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.funcionario import Funcionario
from models.setor import Setor
from models.database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')

        user = Funcionario.query.filter_by(email=email).first()

        # Nota: Em um ambiente de produção real, deve-se usar hash de senha
        if user and user.senha == senha:
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos.', 'danger')

    return render_template('login.html')

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

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

@auth_bp.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        nova_senha = request.form.get('password')
        confirmar_senha = request.form.get('confirm_password')

        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('auth.recuperar_senha'))

        user = Funcionario.query.filter_by(email=email).first()
        if user:
            user.senha = nova_senha
            try:
                user.save()
                flash('Senha atualizada com sucesso!', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash(f'Erro ao atualizar senha: {str(e)}', 'danger')
        else:
            flash('E-mail não encontrado no sistema.', 'danger')

    return render_template('recuperar_senha.html')

@auth_bp.route('/perfil')
@login_required
def perfil():
    # Busca manutenções que o funcionário cadastrou
    from models.manutencao import Manutencao
    manutencoes = Manutencao.query.filter_by(autor_id=current_user.id).order_by(Manutencao.data_registro.desc()).all()

    # Busca equipamentos que o funcionário é responsável
    from models.equipamento import Equipamento
    equipamentos = Equipamento.query.filter_by(responsavel_id=current_user.id).all()

    return render_template('perfil.html', manutencoes=manutencoes, equipamentos=equipamentos)

@auth_bp.route('/perfil/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        nome = request.form.get('nome')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if not nome:
            flash('O nome não pode estar vazio.', 'danger')
            return redirect(url_for('auth.configuracoes'))

        current_user.nome = nome

        if nova_senha:
            if nova_senha != confirmar_senha:
                flash('As senhas não coincidem.', 'danger')
                return redirect(url_for('auth.configuracoes'))
            current_user.senha = nova_senha

        try:
            current_user.save()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('auth.perfil'))
        except Exception as e:
            flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')

    return render_template('configuracoes_perfil.html')

@auth_bp.route('/admin/configuracoes')
@login_required
def admin_configuracoes():
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
        return redirect(url_for('dashboard'))

    funcionarios = Funcionario.get_all()
    return render_template('admin_configuracoes.html', funcionarios=funcionarios)

@auth_bp.route('/admin/funcionario/<int:funcionario_id>')
@login_required
def detalhe_funcionario(funcionario_id):
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
        return redirect(url_for('dashboard'))
    
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    
    # Busca manutenções que o funcionário registrou
    from models.manutencao import Manutencao
    manutencoes = Manutencao.query.filter_by(autor_id=funcionario.id).order_by(Manutencao.data_registro.desc()).all()
    
    return render_template('detalhe_funcionario.html', funcionario=funcionario, manutencoes=manutencoes)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))