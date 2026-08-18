import os
import json
from pathlib import Path

# Import app and models
from flask_app import create_app, db, Product, Ingredient, ProductIngredient

app = create_app()

PRICES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'prices'))
PRECIOS = os.path.join(PRICES_DIR, 'precios.json')
RECIPES = os.path.join(PRICES_DIR, 'recipes.json')
COSTS = os.path.join(PRICES_DIR, 'costs.json')


def _clean_key(k):
    return k.strip().replace('=', '').strip()


with app.app_context():
    db.create_all()

    # Load ingredient costs
    if os.path.exists(COSTS):
        with open(COSTS, encoding='utf-8') as f:
            costs = json.load(f)
        for name, cost in costs.items():
            ing = Ingredient.query.filter_by(name=name).first()
            if not ing:
                ing = Ingredient(name=name, display_name=name, display_name_es=name, cost=float(cost))
                db.session.add(ing)
            else:
                ing.display_name = ing.display_name or name
                ing.display_name_es = ing.display_name_es or name
                ing.cost = float(cost)
        db.session.commit()
        print(f"Loaded {len(costs)} ingredients")
    else:
        print(f"Costs file not found: {COSTS}")

    # Load products/prices
    if os.path.exists(PRECIOS):
        with open(PRECIOS, encoding='utf-8') as f:
            precios = json.load(f)
        for raw_name, meta in precios.items():
            name = raw_name.strip()
            # normalize category
            if '_loaf' in name:
                category = 'loaf'
            elif '_stick' in name:
                category = 'stick'
            else:
                category = 'other'
            prod = Product.query.filter_by(name=name).first()
            display_name = name.replace('_', ' ')
            if not prod:
                prod = Product(name=name, display_name=display_name,
                               price=meta.get('price'), cost=meta.get('cost'), benefits=meta.get('benefits'),
                               category=category)
                db.session.add(prod)
            else:
                prod.display_name = display_name
                prod.price = meta.get('price')
                prod.cost = meta.get('cost')
                prod.benefits = meta.get('benefits')
                prod.category = category
        db.session.commit()
        print(f"Loaded {len(precios)} products")
    else:
        print(f"Precios file not found: {PRECIOS}")

    # Load recipes
    if os.path.exists(RECIPES):
        with open(RECIPES, encoding='utf-8') as f:
            recipes = json.load(f)
        count = 0
        for raw_name, mapping in recipes.items():
            name = _clean_key(raw_name)
            # try several matching strategies to find product
            prod = Product.query.filter_by(name=name).first()
            if not prod:
                prod = Product.query.filter_by(name=name.replace(' ', '_')).first()
            if not prod:
                prod = Product.query.filter_by(display_name=name).first()
            if not prod:
                # skip if product not found
                continue

            # For each ingredient in mapping, find or create Ingredient, then create ProductIngredient
            for ing_name, qty in mapping.items():
                ing_key = ing_name.strip()
                ing = Ingredient.query.filter_by(name=ing_key).first()
                if not ing:
                    # create ingredient with default display names
                    ing = Ingredient(name=ing_key, display_name=ing_key, display_name_es=ing_key, cost=0.0)
                    db.session.add(ing)
                    db.session.flush()
                # check existing association
                assoc = ProductIngredient.query.filter_by(product_id=prod.id, ingredient_id=ing.id).first()
                if not assoc:
                    assoc = ProductIngredient(product_id=prod.id, ingredient_id=ing.id, quantity=float(qty))
                    db.session.add(assoc)
                else:
                    assoc.quantity = float(qty)
                count += 1
        db.session.commit()
        print(f"Loaded {count} recipes")
    else:
        print(f"Recipes file not found: {RECIPES}")

    print("Import complete")
