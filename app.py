from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import csv
import requests
import re
app = Flask(__name__, static_folder='static', template_folder='templates')

API_KEY = '50809115-7134a20d0f08bf7c5cbb7fed6'

# Wczytaj produkty z pliku JSON
def load_products():
    try:
        with open("products.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Zapisz produkty do pliku JSON
def save_products(products):
    with open("products.json", "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

# Ładowanie przepisów
def load_recipes():
    recipes = []
    with open('recipes.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['id'] = int(row['id'])  # Konwersja id na int
            row['prep_time'] = int(row['prep_time'])
            row['cook_time'] = int(row['cook_time'])
            recipes.append(row)
    return recipes


# Ładowanie składników
def load_ingredients():
    ingredients = {}
    with open('recipe_ingredients.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rid = row['recipe_id']
            if rid not in ingredients:
                ingredients[rid] = []
            ingredients[rid].append(row)
    return ingredients

def load_ingredient_details():
    details = {}
    with open('ingredients.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            details[row['product']] = row
    return details

def load_recipe_ingredients(recipe_id):
    all_ingredients_info = load_ingredient_details()
    recipe_ings = []
    with open('recipe_ingredients.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['recipe_id'] == str(recipe_id):
                product_name = row['ingredient_name']
                info = all_ingredients_info.get(product_name, {})
                recipe_ings.append({
                    'name': product_name,
                    'quantity': row.get('quantity', ''),
                    'unit': row.get('unit', ''),
                    'category': info.get('category', 'Brak kategorii'),
                    'calories': info.get('calories', 'brak danych'),
                    'protein': info.get('protein', ''),
                    'fat': info.get('fat', ''),
                    'carbs': info.get('carbs', '')
                })
    return recipe_ings


@app.route('/')
def index():
    recipes = load_recipes()
    return render_template('login.html', recipes=recipes)


@app.route('/recipe/<int:recipe_id>')
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

@app.route('/recipes')
def recipes():
    recipes = load_recipes()
    enriched_recipes = []

    for recipe in recipes:
        query = recipe['title']
        try:
            resp = requests.get(
                'https://pixabay.com/api/',
                params={
                    'key': API_KEY,
                    'q': query,
                    'image_type': 'photo',
                    'orientation': 'horizontal',
                    'lang': 'pl',
                    'per_page': 1
                }
            )
            data = resp.json()
            hits = data.get('hits', [])
            image_url = hits[0]['webformatURL'] if hits else url_for('static', filename='placeholder.jpg')
        except Exception:
            image_url = url_for('static', filename='placeholder.jpg')

        recipe['image_url'] = image_url
        enriched_recipes.append(recipe)

    return render_template('recipes.html', recipes=enriched_recipes)

@app.route('/products.html')
def products_page():
    return render_template('products.html')

@app.route('/product')
def get_product():
    name = request.args.get("name")
    products = load_products()
    for product in products:
        if product["name"].lower() == name.lower():
            return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/product', methods=["POST"])
def add_product():
    new_product = request.get_json()
    products = load_products()
    products.append(new_product)
    save_products(products)
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/ingredients')
def get_ingredients():
    return jsonify(load_ingredients())

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/wyloguj')
def wyloguj():
    # np. logout logic
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # kod widoku
    return render_template('dashboard.html')

@app.route('/add-product', methods=['GET'], endpoint='add-product')
def add_product_form():
    return render_template('add-product.html')

if __name__ == "__main__":
    app.run(port=3005, debug=True)
