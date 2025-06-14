from flask import Blueprint, render_template, request, jsonify, url_for, redirect, session
from flask_login import login_required, current_user
from models import Product, db
from product import load_recipes, load_recipe_ingredients, load_products, load_ingredients, recipe_possible
from product import get_user_ingredients, load_ingredient_names, load_ingredient_details
import requests
import re
import csv


dashboard_bp = Blueprint('dashboard', __name__)
API_KEY = 'your_api_key_here'

@dashboard_bp.route('/')
def index():
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

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

    # Załaduj dozwolone nazwy
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

    # oczyszczone instrukcje – według wcześniejszego rozwiązania
    instructions = recipe['instructions'].replace('\\n', '\n')
    lines = [re.sub(r'^\d+\.\s*', '', line).strip() for line in instructions.split('\n')]
    recipe['instructions'] = '\\n'.join(lines)

    ingredients = load_recipe_ingredients(recipe_id)

    query = recipe['title']
    try:
        resp = requests.get(
            'https://pixabay.com/api/',
            params={'key': API_KEY, 'q': query, 'image_type': 'photo', 'orientation': 'horizontal', 'lang': 'pl', 'per_page': 3}
        )
        data = resp.json()
        hits = data.get('hits', [])
        image_url = hits[0]['webformatURL'] if hits else url_for('static', filename='placeholder.jpg')
    except Exception:
        image_url = url_for('static', filename='placeholder.jpg')

    return render_template('recipe_detail.html', recipe=recipe, ingredients=ingredients, image_url=image_url)

@dashboard_bp.route('/recipes')
@login_required
def recipes():
    # 1. Pobierz produkty aktualnego użytkownika (nazwy produktów)
    user_products = db.session.query(Product.name).filter_by(user_id=current_user.id).all()
    user_products_set = set([p[0].lower() for p in user_products])  # małe litery dla porównania

    # 2. Wczytaj przepisy z CSV
    recipes = []
    with open('recipes.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipes.append(row)

    # 3. Wczytaj składniki przepisów z CSV
    recipe_ingredients = {}
    with open('recipe_ingredients.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row['recipe_id']
            if rid not in recipe_ingredients:
                recipe_ingredients[rid] = []
            recipe_ingredients[rid].append(row['ingredient_name'].lower().strip())

    # 4. Filtruj przepisy — wyświetl tylko te, których wszystkie składniki są dostępne
    filtered_recipes = []
    for r in recipes:
        rid = str(r['id'])
        ings = recipe_ingredients.get(rid, [])
        # jeśli przepis nie ma składników, pomijamy go lub traktujemy jako niewykonalny
        if ings and all(ing in user_products_set for ing in ings):
            filtered_recipes.append(r)

    # 5. Dodaj pola do wyświetlenia (np. image_url itd.) jeśli chcesz
    
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

