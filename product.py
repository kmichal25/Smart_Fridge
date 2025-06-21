import json
import csv
import sqlite3
import requests
from flask import url_for

API_KEY = '50809115-7134a20d0f08bf7c5cbb7fed6'

def load_products():
    try:
        with open("products.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_products(products):
    with open("products.json", "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

def load_recipes():
    with open('recipes.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        recipes = []
        for row in reader:
            if not row['id'].isdigit():
                continue  
            row['id'] = int(row['id'])
            recipes.append(row)
    return recipes

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

def get_user_ingredients(user_id):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.product 
        FROM user_ingredients ui
        JOIN ingredients i ON ui.ingredient_id = i.id
        WHERE ui.user_id = ?
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return {row[0].strip().lower() for row in results}

def recipe_possible(recipe_id, available_ingredients):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ri.ingredient_name 
        FROM recipe_ingredients ri
        WHERE ri.recipe_id = ?
    """, (recipe_id,))
    required = {row[0].strip().lower() for row in cursor.fetchall()}
    conn.close()
    return required.issubset(available_ingredients)


def load_ingredient_names():
    names = []
    with open('ingredients.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            names.append(row['product'])
    return names

def get_pixabay_image_url(query):
    try:
        resp = requests.get(
            'https://pixabay.com/api/',
            params={
                'key': API_KEY,
                'q': query,
                'image_type': 'photo',
                'orientation': 'horizontal',
                'lang': 'pl',
                'per_page': 3
            }
        )
        data = resp.json()
        hits = data.get('hits', [])
        if hits:
            return hits[0]['webformatURL']
    except Exception:
        pass
    return '/static/img/fridge.jpg'

