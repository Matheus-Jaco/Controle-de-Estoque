from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import list_products, get_product, create_product, update_product, delete_product, adjust_stock

products_bp = Blueprint('products', __name__, url_prefix='/products', template_folder='../templates')


def format_date(date_str):
    if not date_str:
        return ''
    date_str = date_str[:10]
    try:
        year, month, day = date_str.split('-')
        return f'{day}/{month}/{year}'
    except ValueError:
        return date_str


@products_bp.route('', strict_slashes=False)
def products_list():
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'name')
    products = list_products(search=search, sort=sort)
    low_stock = [p for p in products if 0 < p['quantity'] <= 5]
    out_stock = [p for p in products if p['quantity'] == 0]
    return render_template('products.html', products=products, search=search, sort=sort, low_stock=low_stock, out_stock=out_stock, format_date=format_date, title='Produtos')


@products_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '0')
        quantity = request.form.get('quantity', '0')
        if not name or float(price) < 0 or int(quantity) < 0:
            flash('Preencha todos os campos corretamente.', 'danger')
        else:
            create_product(name, price, quantity, session['user_id'])
            flash('Produto cadastrado com sucesso.', 'success')
            return redirect(url_for('products.products_list'))
    return render_template('product_form.html', action='Adicionar', product=None, title='Produtos')


@products_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = get_product(product_id)
    if not product:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('products.products_list'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '0')
        quantity = request.form.get('quantity', '0')
        if not name or float(price) < 0 or int(quantity) < 0:
            flash('Preencha todos os campos corretamente.', 'danger')
        else:
            update_product(product_id, name, price, quantity, session['user_id'])
            flash('Produto atualizado com sucesso.', 'success')
            return redirect(url_for('products.products_list'))
    return render_template('product_form.html', action='Editar', product=product, title='Produtos')


@products_bp.route('/delete/<int:product_id>', methods=['POST'])
def delete_product_route(product_id):
    delete_product(product_id, session['user_id'])
    flash('Produto excluído com sucesso.', 'success')
    return redirect(url_for('products.products_list'))


@products_bp.route('/move/<int:product_id>', methods=['POST'])
def move_stock(product_id):
    movement_type = request.form.get('movement_type')
    amount = int(request.form.get('amount', '0'))
    note = request.form.get('note', '')
    if amount <= 0 or movement_type not in ('sale', 'restock'):
        flash('Informe operação válida e quantidade maior que zero.', 'danger')
        return redirect(url_for('products.products_list'))
    if movement_type == 'sale':
        amount = -amount
    try:
        adjust_stock(product_id, amount, 'sale' if movement_type == 'sale' else 'restock', session['user_id'], note)
        flash('Movimentação registrada com sucesso.', 'success')
    except ValueError as error:
        flash(str(error), 'danger')
    return redirect(url_for('products.products_list'))
