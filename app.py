from flask import Flask, request, jsonify, render_template
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

# Routing do strony głównej (np. index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Routing do products.html
@app.route('/products.html')
def products_page():
    return render_template('products.html')

# Endpoint zwracający produkt po nazwie
@app.route('/product')
def get_product():
    name = request.args.get("name")
    products = load_products()
    for product in products:
        if product["name"].lower() == name.lower():
            return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

# Endpoint dodający nowy produkt
@app.route('/product', methods=["POST"])
def add_product():
    new_product = request.get_json()
    products = load_products()
    products.append(new_product)
    save_products(products)
    return jsonify({"message": "Product added successfully"}), 201

# Endpoint zwracający listę składników
@app.route('/ingredients')
def get_ingredients():
    return jsonify(load_ingredients())

# Uruchom serwer na porcie 3005
if __name__ == "__main__":
    app.run(port=3005, debug=True)

