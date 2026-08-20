from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import (
    authenticate_user,
    get_user_by_id,
    is_username_available,
    sanitize_text,
    update_user_credentials,
    log_action,
)

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = authenticate_user(username, password)
        if user:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            log_action(user['id'], 'login', f'user:{user['id']}', 'Login bem-sucedido')
            return redirect(url_for('dashboard.view_dashboard'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')


@auth_bp.route('/change-user-info', methods=['POST'])
def change_user_info():
    user_id = session.get('user_id')
    if not user_id:
        flash('Sessão inválida. Faça login novamente.', 'danger')
        return redirect(url_for('auth.login'))

    current_password = request.form.get('current_password', '')
    new_username = request.form.get('new_username', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    current_password = sanitize_text(current_password)
    new_username = sanitize_text(new_username)
    new_password = sanitize_text(new_password)
    confirm_password = sanitize_text(confirm_password)

    if not current_password or not new_username or not new_password or not confirm_password:
        flash('Todos os campos são obrigatórios.', 'danger')
        return redirect(request.referrer or url_for('dashboard.view_dashboard'))

    if new_password != confirm_password:
        flash('As senhas não conferem.', 'danger')
        return redirect(request.referrer or url_for('dashboard.view_dashboard'))

    if len(new_password) < 8 or not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
        flash('A nova senha deve ter ao menos 8 caracteres e incluir letras e números.', 'danger')
        return redirect(request.referrer or url_for('dashboard.view_dashboard'))

    user = get_user_by_id(user_id)
    if not user or not authenticate_user(user['username'], current_password):
        flash('Senha atual incorreta.', 'danger')
        return redirect(request.referrer or url_for('dashboard.view_dashboard'))

    if not is_username_available(new_username, exclude_user_id=user_id):
        flash('Este nome de usuário já está em uso.', 'danger')
        return redirect(request.referrer or url_for('dashboard.view_dashboard'))

    update_user_credentials(user_id, new_username, new_password)
    log_action(user_id, 'update_user_info', f'user:{user_id}', 'Alteração de nome de usuário e senha')
    flash('Informações atualizadas com sucesso. Faça login novamente.', 'success')
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        log_action(user_id, 'logout', f'user:{user_id}', 'Logout seguro')
    session.clear()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('auth.login'))
