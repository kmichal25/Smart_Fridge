from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, origins=['http://127.0.0.1:5501'])  # Live Server

DATA_FILE = 'products.json'

def load_products():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_products(products):
    with open(DATA_FILE, 'w') as f:
        json.dump(products, f, indent=2)

@app.route('/add-product', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    amount = data.get('amount')
    expiry_date = data.get('expiryDate')

    # Walidacje
    if not name or not isinstance(name, str):
        return jsonify({'error': 'Nazwa produktu jest wymagana.'}), 400

    if not isinstance(amount, (int, float)) or amount < 0:
        return jsonify({'error': 'Ilość musi być liczbą nieujemną.'}), 400

    if not expiry_date or not isinstance(expiry_date, str):
        return jsonify({'error': 'Data ważności jest wymagana.'}), 400

    # Poprawa nazwy: Pierwsza litera duża
    name = name.strip().capitalize()

    products = load_products()
    products.append({
        'name': name,
        'amount': amount,
        'expiryDate': expiry_date
    })
    save_products(products)

    return jsonify({'message': 'Produkt dodany pomyślnie', 'product': products[-1]}), 201

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(load_products())

@app.route('/products/<name>', methods=['DELETE'])
def delete_product(name):
    name = name.lower()
    products = load_products()
    filtered = [p for p in products if p['name'].lower() != name]

    if len(filtered) == len(products):
        return jsonify({'error': 'Nie znaleziono produktu.'}), 404

    save_products(filtered)
    return jsonify({'message': 'Produkt usunięty pomyślnie'})

if __name__ == '__main__':
    app.run(port=3005)
