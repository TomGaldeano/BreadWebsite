"""Migration helper: add product display name and category columns if missing.

Run this with the project's environment (DATABASE env vars) available. It supports
MySQL and SQLite backends used by the app.

Usage:
  python scripts/add_product_columns.py

This script imports the app's `create_app` and uses the configured SQLAlchemy engine.
"""
import sqlalchemy
from sqlalchemy import text
from flask import current_app

from flask_app import create_app, db


def add_columns():
    app = create_app()
    with app.app_context():
        engine = db.engine
        insp = sqlalchemy.inspect(engine)
        try:
            cols = [c['name'] for c in insp.get_columns('products')]
        except Exception:
            print("Table 'products' does not exist or cannot be inspected. Create tables first.")
            return

        dialect = engine.dialect.name
        statements = []

        if 'display_name' not in cols:
            statements.append(("display_name", "ALTER TABLE products ADD COLUMN display_name VARCHAR(255) NULL"))
        if 'display_name_es' not in cols:
            statements.append(("display_name_es", "ALTER TABLE products ADD COLUMN display_name_es VARCHAR(255) NULL"))
        if 'category' not in cols:
            statements.append(("category", "ALTER TABLE products ADD COLUMN category VARCHAR(50) NULL"))

        if not statements:
            print('No columns to add; `products` already has display_name/display_name_es/category.')
            return

        for name, stmt in statements:
            try:
                if dialect == 'sqlite':
                    # SQLite supports simple ALTER TABLE ADD COLUMN
                    engine.execute(text(stmt))
                elif dialect in ('mysql', 'mariadb'):
                    # MySQL: safe to run ALTER TABLE
                    engine.execute(text(stmt))
                else:
                    # Fallback: attempt generic ALTER
                    engine.execute(text(stmt))
                print(f"Added column {name}")
            except Exception as e:
                print(f"Could not add column {name}: {e}")


if __name__ == '__main__':
    add_columns()
