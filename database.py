import os
import sqlite3
from flask import current_app, g
import click
import unicodedata

def get_db():
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        db_exists = os.path.exists(db_path) and os.path.getsize(db_path) > 0
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
        g.db.row_factory = sqlite3.Row
        # register unaccent function to support accent-insensitive searches
        def _unaccent(value):
            if value is None:
                return None
            try:
                nfkd = unicodedata.normalize('NFKD', str(value))
                return ''.join([c for c in nfkd if not unicodedata.combining(c)])
            except Exception:
                return value
        try:
            g.db.create_function('unaccent', 1, _unaccent)
        except Exception:
            # fallback: ignore if registration fails
            pass
        if not db_exists:
            with current_app.open_resource('schema.sql') as f:
                g.db.executescript(f.read().decode('utf8'))
            g.db.commit()
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    db.commit()


@click.command('init-db')
@click.option('--clean', is_flag=True, default=False, help='Remove existing database and initialize fresh.')
def init_db_command(clean):
    """Initialize the database from schema.sql."""
    db_path = current_app.config['DATABASE']
    if clean and os.path.exists(db_path):
        os.remove(db_path)
    init_db()
    click.echo('Banco de dados inicializado com sucesso.')
