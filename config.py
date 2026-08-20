import os
import sys

if getattr(sys, 'frozen', False):
    # Se rodando a partir do executável (.exe)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Se rodando do código-fonte (desenvolvimento)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('PEÇAS_BAREL_SECRET') or os.urandom(24)
    DATABASE = os.path.join(BASE_DIR, 'data', 'barel.db')
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_PROTECTION = 'strong'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
