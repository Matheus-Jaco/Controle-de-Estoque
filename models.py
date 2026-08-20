import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db
from datetime import datetime


def sanitize_text(value):
    return value.strip() if isinstance(value, str) else value


def get_user_by_username(username):
    db = get_db()
    return db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()


def get_user_by_id(user_id):
    db = get_db()
    return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()


def is_username_available(username, exclude_user_id=None):
    db = get_db()
    query = 'SELECT id FROM users WHERE username = ?'
    params = [sanitize_text(username)]
    if exclude_user_id is not None:
        query += ' AND id != ?'
        params.append(exclude_user_id)
    row = db.execute(query, tuple(params)).fetchone()
    return row is None


def update_user_credentials(user_id, username, password):
    db = get_db()
    password_hash = generate_password_hash(password)
    db.execute(
        'UPDATE users SET username = ?, password_hash = ? WHERE id = ?',
        (sanitize_text(username), password_hash, user_id)
    )
    db.commit()


def authenticate_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None


def log_action(user_id, action, target, detail=None):
    db = get_db()
    db.execute(
        'INSERT INTO logs (user_id, action, target, detail, created_at) VALUES (?, ?, ?, ?, ?)',
        (user_id, action, target, detail or '', datetime.utcnow()),
    )
    db.commit()


def create_user(username, password):
    db = get_db()
    password_hash = generate_password_hash(password)
    db.execute('INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)',
               (sanitize_text(username), password_hash, datetime.utcnow()))
    db.commit()


def list_products(search=None, sort='name'):
    db = get_db()
    query = 'SELECT * FROM products'
    params = []
    if search:
        query += ' WHERE unaccent(name) LIKE unaccent(?) COLLATE NOCASE'
        params.append(f'%{sanitize_text(search)}%')
    if sort == 'price':
        query += ' ORDER BY price ASC'
    else:
        query += ' ORDER BY name COLLATE NOCASE ASC'
    return db.execute(query, params).fetchall()


def get_product(product_id):
    db = get_db()
    return db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()


def create_product(name, price, quantity, user_id):
    db = get_db()
    name = sanitize_text(name)
    db.execute(
        'INSERT INTO products (name, price, quantity, created_at) VALUES (?, ?, ?, ?)',
        (name, float(price), int(quantity), datetime.utcnow()),
    )
    product_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.commit()
    log_action(user_id, 'create_product', f'product:{product_id}', name)
    return product_id


def update_product(product_id, name, price, quantity, user_id):
    db = get_db()
    name = sanitize_text(name)
    db.execute(
        'UPDATE products SET name = ?, price = ?, quantity = ? WHERE id = ?',
        (name, float(price), int(quantity), product_id),
    )
    db.commit()
    log_action(user_id, 'update_product', f'product:{product_id}', name)


def delete_product(product_id, user_id):
    db = get_db()
    product = get_product(product_id)
    db.execute('DELETE FROM products WHERE id = ?', (product_id,))
    db.execute('INSERT INTO logs (user_id, action, target, detail, created_at) VALUES (?, ?, ?, ?, ?)',
               (user_id, 'delete_product', f'product:{product_id}', product['name'] if product else '', datetime.utcnow()))
    db.commit()


def adjust_stock(product_id, delta, movement_type, user_id, note=''):
    db = get_db()
    product = get_product(product_id)
    if not product:
        return None
    new_quantity = product['quantity'] + int(delta)
    if new_quantity < 0:
        raise ValueError('Quantidade insuficiente em estoque.')
    db.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, product_id))
    db.execute(
        'INSERT INTO stock_movements (product_id, movement_type, quantity, description, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (product_id, movement_type, int(delta), sanitize_text(note), user_id, datetime.utcnow()),
    )
    db.commit()
    log_action(user_id, f'stock_{movement_type}', f'product:{product_id}', note)
    return new_quantity


def product_summary():
    db = get_db()
    total = db.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    total_value = db.execute('SELECT SUM(price * quantity) FROM products').fetchone()[0] or 0
    low_stock = db.execute('SELECT COUNT(*) FROM products WHERE quantity > 0 AND quantity <= 5').fetchone()[0]
    out_of_stock = db.execute('SELECT COUNT(*) FROM products WHERE quantity = 0').fetchone()[0]
    return {
        'total': total,
        'value': total_value,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }


def list_notes(search=None, status=None):
    db = get_db()
    query = 'SELECT * FROM notes'
    params = []
    if status in ('pendente', 'pago'):
        query += ' WHERE status = ?'
        params.append(status)
        if search:
            query += ' AND unaccent(client_name) LIKE unaccent(?) COLLATE NOCASE'
            params.append(f'%{sanitize_text(search)}%')
    elif search:
        query += ' WHERE unaccent(client_name) LIKE unaccent(?) COLLATE NOCASE'
        params.append(f'%{sanitize_text(search)}%')
    query += ' ORDER BY due_date DESC'
    return db.execute(query, params).fetchall()


def get_note(note_id):
    db = get_db()
    return db.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()


def create_note(client_name, due_date, description, total_value, observations, user_id):
    db = get_db()
    client_name = sanitize_text(client_name)
    description = sanitize_text(description)
    observations = sanitize_text(observations)
    db.execute(
        'INSERT INTO notes (client_name, due_date, description, total_value, observations, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (client_name, due_date, description, float(total_value), observations, 'pendente', datetime.utcnow()),
    )
    note_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.commit()
    log_action(user_id, 'create_note', f'note:{note_id}', client_name)
    return note_id


def update_note(note_id, client_name, due_date, description, total_value, observations, user_id):
    db = get_db()
    client_name = sanitize_text(client_name)
    db.execute(
        'UPDATE notes SET client_name = ?, due_date = ?, description = ?, total_value = ?, observations = ? WHERE id = ?',
        (client_name, due_date, sanitize_text(description), float(total_value), sanitize_text(observations), note_id),
    )
    db.commit()
    log_action(user_id, 'update_note', f'note:{note_id}', client_name)


def toggle_note_status(note_id, new_status, user_id):
    db = get_db()
    note = get_note(note_id)
    if not note:
        return None
    db.execute('UPDATE notes SET status = ? WHERE id = ?', (new_status, note_id))
    db.commit()
    log_action(user_id, 'toggle_note_status', f'note:{note_id}', new_status)
    return new_status


def delete_note(note_id, user_id):
    db = get_db()
    note = get_note(note_id)
    db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    db.commit()
    log_action(user_id, 'delete_note', f'note:{note_id}', note['client_name'] if note else '')


def report_summary():
    db = get_db()
    sold_count = db.execute("SELECT SUM(ABS(s.quantity)) FROM stock_movements s JOIN products p ON p.id = s.product_id WHERE s.movement_type = 'sale'").fetchone()[0] or 0
    top_products = db.execute("SELECT p.name, SUM(ABS(s.quantity)) AS total FROM stock_movements s JOIN products p ON p.id = s.product_id WHERE s.movement_type = 'sale' GROUP BY p.id ORDER BY total DESC LIMIT 5").fetchall()
    total_sales = db.execute("SELECT SUM(ABS(p.price * s.quantity)) FROM stock_movements s JOIN products p ON p.id = s.product_id WHERE s.movement_type = 'sale'").fetchone()[0] or 0
    repurchases = db.execute("SELECT COUNT(*) FROM stock_movements s JOIN products p ON p.id = s.product_id WHERE s.movement_type = 'restock'").fetchone()[0]
    notes_created = db.execute('SELECT COUNT(*) FROM notes').fetchone()[0]
    notes_pending = db.execute("SELECT COUNT(*) FROM notes WHERE status = 'pendente'").fetchone()[0]
    notes_paid = db.execute("SELECT COUNT(*) FROM notes WHERE status = 'pago'").fetchone()[0]
    total_pending = db.execute("SELECT SUM(total_value) FROM notes WHERE status = 'pendente'").fetchone()[0] or 0
    total_paid = db.execute("SELECT SUM(total_value) FROM notes WHERE status = 'pago'").fetchone()[0] or 0
    recent_logs = db.execute('SELECT * FROM logs ORDER BY created_at DESC LIMIT 20').fetchall()
    return {
        'sold_count': sold_count,
        'top_products': top_products,
        'total_sales': total_sales,
        'repurchases': repurchases,
        'notes_created': notes_created,
        'notes_pending': notes_pending,
        'notes_paid': notes_paid,
        'total_pending': total_pending,
        'total_paid': total_paid,
        'recent_logs': recent_logs,
    }


def monthly_chart_data():
    db = get_db()
    sales = db.execute(
        "SELECT strftime('%Y-%m', s.created_at) AS month, SUM(ABS(s.quantity)) AS total FROM stock_movements s JOIN products p ON p.id = s.product_id WHERE s.movement_type = 'sale' GROUP BY month ORDER BY month"
    ).fetchall()
    restocks = db.execute(
        "SELECT strftime('%Y-%m', s.created_at) AS month, SUM(s.quantity) AS total FROM stock_movements s JOIN products p ON p.id = s.product_id WHERE s.movement_type = 'restock' GROUP BY month ORDER BY month"
    ).fetchall()
    notes = db.execute(
        "SELECT status, COUNT(*) AS total FROM notes GROUP BY status"
    ).fetchall()
    status_order = {'pago': 0, 'paid': 0, 'pendente': 1, 'pending': 1}
    sorted_notes = sorted(notes, key=lambda row: status_order.get(row['status'], 2))
    return {
        'sales': [{'month': row['month'], 'total': row['total']} for row in sales],
        'restocks': [{'month': row['month'], 'total': row['total']} for row in restocks],
        'notes': [{'status': row['status'], 'total': row['total']} for row in sorted_notes],
    }
