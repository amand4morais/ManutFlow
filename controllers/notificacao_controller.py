from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models.notificacao import Notificacao
from models.agendamento import Agendamento
from models.equipamento import Equipamento
from models.funcionario import Funcionario
from models.database import db
from datetime import datetime, timedelta

notificacao_bp = Blueprint('notificacao', __name__)

@notificacao_bp.route('/notificacoes')
@login_required
def listar():
    """Lista todas as notificações do usuário logado"""
    notificacoes = Notificacao.query.filter_by(usuario_id=current_user.id).order_by(Notificacao.data_criacao.desc()).all()
    return render_template('notificacoes.html', notificacoes=notificacoes)

@notificacao_bp.route('/notificacoes/lida/<int:id>')
@login_required
def marcar_lida(id):
    """Marca uma notificação como lida e redireciona se houver link"""
    notif = Notificacao.query.get_or_404(id)
    if notif.usuario_id == current_user.id:
        notif.lida = True
        db.session.commit()
        if notif.link:
            return redirect(notif.link)
    return redirect(url_for('notificacao.listar'))

@notificacao_bp.route('/notificacoes/limpar-todas')
@login_required
def limpar_todas():
    """Marca todas as notificações do usuário como lidas"""
    Notificacao.query.filter_by(usuario_id=current_user.id, lida=False).update({Notificacao.lida: True})
    db.session.commit()
    flash('Todas as notificações foram marcadas como lidas.', 'success')
    return redirect(url_for('notificacao.listar'))

@notificacao_bp.route('/agendamentos')
@login_required
def listar_agendamentos():
    """Lista agendamentos de preventivas"""
    if current_user.is_admin:
        agendamentos = Agendamento.query.order_by(Agendamento.data_prevista.asc()).all()
    else:
        # Funcionário vê agendamentos dos equipamentos que ele é responsável
        agendamentos = Agendamento.query.join(Equipamento).filter(Equipamento.responsavel_id == current_user.id).order_by(Agendamento.data_prevista.asc()).all()
    
    return render_template('agendamentos.html', agendamentos=agendamentos)

@notificacao_bp.route('/agendamentos/novo', methods=['GET', 'POST'])
@login_required
def novo_agendamento():
    """Cria um novo agendamento de preventiva (Apenas Admin)"""
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem agendar manutenções.', 'danger')
        return redirect(url_for('notificacao.listar_agendamentos'))
    
    equipamentos = Equipamento.get_all()
    
    if request.method == 'POST':
        equipamento_id = request.form.get('equipamento_id')
        data_prevista_str = request.form.get('data_prevista')
        descricao = request.form.get('descricao')
        
        try:
            data_prevista = datetime.strptime(data_prevista_str, '%Y-%m-%d').date()
            novo = Agendamento(
                equipamento_id=equipamento_id,
                data_prevista=data_prevista,
                descricao=descricao
            )
            novo.save()
            
            # Notificar o responsável pelo equipamento
            eq = Equipamento.get_by_id(equipamento_id)
            if eq and eq.responsavel_id:
                Notificacao.criar(
                    usuario_id=eq.responsavel_id,
                    titulo="Nova Preventiva Agendada",
                    mensagem=f"Uma manutenção preventiva foi agendada para o equipamento {eq.nome} ({eq.codigo}) em {data_prevista.strftime('%d/%m/%Y')}.",
                    tipo="info",
                    link=url_for('notificacao.listar_agendamentos')
                )
            
            flash('Manutenção preventiva agendada com sucesso!', 'success')
            return redirect(url_for('notificacao.listar_agendamentos'))
        except Exception as e:
            flash(f'Erro ao agendar: {str(e)}', 'danger')
            
    return render_template('cadastro_agendamento.html', equipamentos=equipamentos)

@notificacao_bp.route('/api/notificacoes/count')
@login_required
def count_notificacoes():
    """Retorna a contagem de notificações não lidas para a navbar"""
    count = Notificacao.query.filter_by(usuario_id=current_user.id, lida=False).count()
    return jsonify({'count': count})

def verificar_prazos_preventivas():
    """
    Função para verificar agendamentos próximos e criar notificações.
    Pode ser chamada no login ou via tarefa agendada.
    """
    hoje = datetime.now().date()
    alerta_em = hoje + timedelta(days=3) # Alerta com 3 dias de antecedência
    
    # Busca agendamentos pendentes próximos da data
    agendamentos = Agendamento.query.filter(
        Agendamento.status == 'pendente',
        Agendamento.data_prevista <= alerta_em,
        Agendamento.data_prevista >= hoje # Apenas datas futuras ou hoje
    ).all()
    
    for ag in agendamentos:
        eq = ag.equipamento
        if not eq:
            continue
            
        # Título padronizado para busca exata
        titulo = f"ALERTA: Preventiva Próxima - {eq.codigo} ({ag.data_prevista.strftime('%d/%m/%Y')})"
        msg = f"O equipamento {eq.nome} tem uma manutenção preventiva agendada para {ag.data_prevista.strftime('%d/%m/%Y')}."
        
        # 1. Notificar Responsável (se houver)
        if eq.responsavel_id:
            # Busca rigorosa: mesmo título para o mesmo usuário
            ja_notificado = db.session.query(Notificacao).filter(
                Notificacao.usuario_id == eq.responsavel_id,
                Notificacao.titulo == titulo
            ).first()
            
            if not ja_notificado:
                Notificacao.criar(eq.responsavel_id, titulo, msg, 'warning', url_for('notificacao.listar_agendamentos'))
        
        # 2. Notificar Admins
        admins = Funcionario.query.filter_by(is_admin=True).all()
        for admin in admins:
            # Evita duplicar se o admin for o próprio responsável
            if admin.id != eq.responsavel_id:
                ja_notificado_admin = db.session.query(Notificacao).filter(
                    Notificacao.usuario_id == admin.id,
                    Notificacao.titulo == titulo
                ).first()
                
                if not ja_notificado_admin:
                    Notificacao.criar(admin.id, titulo, msg, 'warning', url_for('notificacao.listar_agendamentos'))
