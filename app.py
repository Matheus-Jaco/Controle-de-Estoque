import os
from datetime import date
from flask import Flask, redirect, request, session, url_for, render_template
from config import Config
from database import close_db, get_db, init_db_command
from modules.auth import auth_bp
from modules.products import products_bp
from modules.notes import notes_bp
from modules.reports import reports_bp
from modules.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(reports_bp)

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    @app.before_request
    def require_login():
        open_paths = ['auth.login', 'static']
        if request.endpoint is None or request.endpoint in open_paths:
            return
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

    @app.template_filter('format_date')
    def format_date(value):
        if not value:
            return ''
        try:
            return date.fromisoformat(value).strftime('%d/%m/%Y')
        except ValueError:
            parts = value.split('-')
            return '/'.join(reversed(parts)) if len(parts) >= 3 else value

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500

    return app

import sys
import threading
import webview

app = create_app()

def start_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        # Em modo executável: roda o Flask em uma thread secundária
        flask_thread = threading.Thread(target=start_flask)
        flask_thread.daemon = True
        flask_thread.start()
        
        # Cria a janela nativa do app com o pywebview
        webview.create_window("Peças Barel - Controle de Estoque", "http://127.0.0.1:5000/login", width=1280, height=800)
        webview.start()
    else:
        # Em modo de desenvolvimento: mantém debug ativo e rodando no navegador normal
        app.run(debug=True, port=5000)
