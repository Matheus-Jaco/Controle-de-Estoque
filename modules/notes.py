from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import list_notes, get_note, create_note, update_note, toggle_note_status, delete_note

notes_bp = Blueprint('notes', __name__, url_prefix='/notes', template_folder='../templates')


@notes_bp.route('')
def notes_list():
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    filter_status = status if status in ('pendente', 'pago') else None
    notes = list_notes(search=search, status=filter_status)
    return render_template('notes.html', notes=notes, search=search, status=status, title='Anotações')


@notes_bp.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        client_name = request.form.get('client_name', '').strip()
        due_date = request.form.get('due_date', '').strip()
        description = request.form.get('description', '').strip()
        total_value = request.form.get('total_value', '0')
        observations = request.form.get('observations', '').strip()
        if not client_name or not due_date or float(total_value) < 0:
            flash('Preencha todos os campos obrigatórios corretamente.', 'danger')
        else:
            create_note(client_name, due_date, description, total_value, observations, session['user_id'])
            flash('Anotação registrada com sucesso.', 'success')
            return redirect(url_for('notes.notes_list'))
    return render_template('note_form.html', action='Adicionar', note=None, title='Anotações')


@notes_bp.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = get_note(note_id)
    if not note:
        flash('Anotação não encontrada.', 'danger')
        return redirect(url_for('notes.notes_list'))
    if request.method == 'POST':
        client_name = request.form.get('client_name', '').strip()
        due_date = request.form.get('due_date', '').strip()
        description = request.form.get('description', '').strip()
        total_value = request.form.get('total_value', '0')
        observations = request.form.get('observations', '').strip()
        if not client_name or not due_date or float(total_value) < 0:
            flash('Preencha todos os campos obrigatórios corretamente.', 'danger')
        else:
            update_note(note_id, client_name, due_date, description, total_value, observations, session['user_id'])
            flash('Anotação atualizada com sucesso.', 'success')
            return redirect(url_for('notes.notes_list'))
    return render_template('note_form.html', action='Editar', note=note, title='Anotações')


@notes_bp.route('/toggle/<int:note_id>', methods=['POST'])
def toggle_note(note_id):
    note = get_note(note_id)
    if not note:
        flash('Anotação não encontrada.', 'danger')
    else:
        new_status = 'pago' if note['status'] == 'pendente' else 'pendente'
        toggle_note_status(note_id, new_status, session['user_id'])
        flash('Status da anotação atualizado.', 'success')
    return redirect(url_for('notes.notes_list'))


@notes_bp.route('/delete/<int:note_id>', methods=['POST'])
def delete_note_route(note_id):
    note = get_note(note_id)
    if not note:
        flash('Anotação não encontrada.', 'danger')
    elif note['status'] == 'pendente':
        flash('Não é possível excluir uma anotação pendente. Marque como pago primeiro.', 'danger')
    else:
        delete_note(note_id, session['user_id'])
        flash('Anotação excluída com sucesso.', 'success')
    return redirect(url_for('notes.notes_list'))
