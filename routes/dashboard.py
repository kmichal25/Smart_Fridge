from flask import Blueprint, render_template, request, jsonify, url_for, redirect, session, current_app
from flask_login import login_required, current_user
from models import Product, db
from product import load_recipes, load_recipe_ingredients, load_products, load_ingredients, load_ingredient_names, get_pixabay_image_url, API_KEY
import requests
import re
import csv
import os


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    products = Product.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', products=products)

@dashboard_bp.route('/add-product', methods=['GET'])
@login_required
def add_product_page():
    ingredient_names = load_ingredient_names()
    return render_template('add-product.html', ingredient_names=ingredient_names)


@dashboard_bp.route('/add-product', methods=['POST'])
@login_required
def add_product():
    data = request.get_json()
    name = data.get('name')
    amount = data.get('amount')
    expiry_date = data.get('expiryDate')

    if not name or not isinstance(name, str):
        return jsonify({'error': 'Nazwa produktu jest wymagana.'}), 400

    allowed_products = set(load_ingredient_names())
    
    if name.strip() not in allowed_products:
        return jsonify({'error': 'Produkt nie znajduje się na liście dozwolonych produktów.'}), 400

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

@dashboard_bp.route('/recipe/<int:recipe_id>')
@login_required
def recipe_detail(recipe_id):
    recipes = load_recipes()
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if not recipe:
        return "Przepis nie istnieje", 404

    instructions = recipe['instructions'].replace('\\n', '\n')
    lines = [re.sub(r'^\d+\.\s*', '', line).strip() for line in instructions.split('\n')]
    recipe['instructions'] = '\\n'.join(lines)

    ingredients = load_recipe_ingredients(recipe_id)

    recipe['image_url'] = get_pixabay_image_url(recipe['title'])

    return render_template('recipe_detail.html', recipe=recipe, ingredients=ingredients)

@dashboard_bp.route('/recipes')
@login_required
def recipes():
    user_products = db.session.query(Product.name).filter_by(user_id=current_user.id).all()
    user_products_set = set([p[0].lower() for p in user_products])

    recipes = []
    with open('recipes.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['id'].isdigit():
                continue
            row['id'] = int(row['id'])
            recipes.append(row)

    recipe_ingredients = {}
    with open('recipe_ingredients.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row['recipe_id']
            if rid not in recipe_ingredients:
                recipe_ingredients[rid] = []
            recipe_ingredients[rid].append(row['ingredient_name'].lower().strip())

    filtered_recipes = []
    for r in recipes:
        rid = str(r['id'])
        ings = recipe_ingredients.get(rid, [])
        if ings and all(ing in user_products_set for ing in ings):
            r['image_url'] = get_pixabay_image_url(r['title'])
            filtered_recipes.append(r)

    return render_template('recipes.html', recipes=filtered_recipes)

@dashboard_bp.route('/products.html')
@login_required
def products_page():
    return render_template('products.html')

@dashboard_bp.route('/product')
@login_required
def get_product():
    name = request.args.get("name")
    products = load_products()
    for product in products:
        if product["name"].lower() == name.lower():
            return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@dashboard_bp.route('/ingredients')
@login_required
def get_ingredients():
    return jsonify(load_ingredients())

@dashboard_bp.route('/notifications')
@login_required
def notifications():
    return render_template('notifications.html')

@dashboard_bp.route('/product/<name>')
@login_required
def product_detail(name):
    name = name.strip().capitalize()

    product = Product.query.filter_by(user_id=current_user.id, name=name).first_or_404()

    nutrition_data = None
    csv_path = os.path.join(current_app.root_path, 'ingredients.csv')
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['product'].strip().lower() == name.lower():
                nutrition_data = {
                    'calories': row.get('calories'),
                    'protein': row.get('protein'),
                    'fat': row.get('fat'),
                    'carbs': row.get('carbs')
                }
                break

    image_url = get_pixabay_image_url(name)

    return render_template('product.html', product=product, nutrition=nutrition_data, image_url=image_url)
