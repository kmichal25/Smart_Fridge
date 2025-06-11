from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Product, db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@dashboard_bp.route('/add-product', methods=['GET'])
@login_required
def add_product_page():
    return render_template('add-product.html')

@dashboard_bp.route('/add-product', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()
    name = data.get('name')
    amount = data.get('amount')
    expiry_date = data.get('expiryDate')

    if not name or not isinstance(name, str):
        return jsonify({'error': 'Nazwa produktu jest wymagana.'}), 400
    if not isinstance(amount, (int, float)) or amount < 0:
        return jsonify({'error': 'Ilość musi być liczbą nieujemną.'}), 400
    if not expiry_date or not isinstance(expiry_date, str):
        return jsonify({'error': 'Data ważności jest wymagana.'}), 400

    name = name.strip().capitalize()

    new_product = Product(
        name=name,
        amount=amount,
        expiry_date=expiry_date,
        user_id=current_user.id
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        'message': 'Produkt dodany pomyślnie',
        'product': {
            'name': new_product.name,
            'amount': new_product.amount,
            'expiryDate': new_product.expiry_date
        }
    }), 201


@dashboard_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    products = Product.query.filter_by(user_id=current_user.id).all()
    data = [{
        'name': p.name,
        'amount': p.amount,
        'expiryDate': p.expiry_date
    } for p in products]
    return jsonify(data)


@dashboard_bp.route('/products/<name>', methods=['DELETE'])
@login_required
def delete_product(name):
    product = Product.query.filter_by(user_id=current_user.id, name=name.capitalize()).first()
    if not product:
        return jsonify({'error': 'Nie znaleziono produktu.'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Produkt usunięty pomyślnie'})

