from flask import Flask, render_template, request, redirect
import sqlite3 as sql
import threading
import webview

app = Flask(__name__)
DB = 'Estoque.db'

# ---------- BANCO DE DADOS ----------
def criar_banco():
    with sql.connect(DB) as conn:
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
    with sql.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM produtos")
        produtos = c.fetchall()
    return render_template('index.html', produtos=produtos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    preco = float(request.form['preco'])
    quantidade = int(request.form['quantidade'])
    with sql.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
                  (nome, preco, quantidade))
        conn.commit()
    return redirect('/')

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    with sql.connect(DB) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM produtos WHERE id = ?", (id,))
        conn.commit()
    return redirect('/')

@app.route('/baixar/<int:id>', methods=['POST'])
def baixar(id):
    quantidade_baixa = int(request.form['quantidade_baixa'])
    with sql.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT quantidade FROM produtos WHERE id = ?", (id,))
        resultado = c.fetchone()

        if resultado and resultado[0] >= quantidade_baixa:
            nova_quantidade = resultado[0] - quantidade_baixa
            c.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, id))
            conn.commit()
        else:
            print("Quantidade insuficiente no estoque")
    return redirect('/')

@app.route('/repor/<int:id>', methods=['POST'])
def repor_estoque(id):
    quantidade_repor = int(request.form['quantidade_repor'])
    with sql.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT quantidade FROM produtos WHERE id = ?", (id,))
        resultado_repor = c.fetchone()

        if resultado_repor:
            nova_quantidade = resultado_repor[0] + quantidade_repor
            c.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, id))
            conn.commit()
        else:
            print('Produto não encontrado.')
    return redirect('/')

@app.route('/pesquisar', methods=['GET'])
def pesquisar():
    termo = request.args.get('termo', '').strip()
    criar_banco()
    with sql.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM produtos WHERE nome LIKE ?", (f'%{termo}%',))
        produtos = c.fetchall()
    return render_template('index.html', produtos=produtos, termo=termo)

def start_flask():
    app.run(debug=False, port=5000, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()

    webview.create_window("📦 Sistema de Estoque", "http://127.0.0.1:5000/")
    webview.start()
