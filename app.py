from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import csv

app = Flask(__name__, static_folder='static', template_folder='templates')

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
            row['prep_time'] = int(row['prep_time'])
            row['cook_time'] = int(row['cook_time'])
            recipes.append(row)
    return recipes

# Ładowanie składników
def load_ingredients():
    ingredients = {}
    with open('ingredients.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rid = row['recipe_id']
            if rid not in ingredients:
                ingredients[rid] = []
            ingredients[rid].append(row)
    return ingredients

@app.route('/')
def index():
    recipes = load_recipes()
    return render_template('login.html', recipes=recipes)

@app.route('/recipes')
def recipes():
    recipes = load_recipes()
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipes = load_recipes()
    ingredients = load_ingredients()

    recipe = next((r for r in recipes if int(r['id']) == recipe_id), None)
    if recipe is None:
        return "Przepis nie istnieje", 404

    ing = ingredients.get(str(recipe_id), [])
    return render_template('recipe_detail.html', recipe=recipe, ingredients=ing)

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

if __name__ == "__main__":
    app.run(port=3005, debug=True)
