from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB = 'loja_bicicleta.db'

def criar_banco():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL
        )''')

@app.route('/')
def index():
    criar_banco()
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM produtos")
        produtos = c.fetchall()
    return render_template('index.html', produtos=produtos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    preco = float(request.form['preco'])
    quantidade = int(request.form['quantidade'])
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
                  (nome, preco, quantidade))
        conn.commit()
    return redirect('/')

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM produtos WHERE id = ?", (id,))
        conn.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
