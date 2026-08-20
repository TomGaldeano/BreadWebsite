import werkzeug.security
from flask import Flask, render_template, redirect, url_for, request
from functools import wraps
from flask_bootstrap import Bootstrap
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer, String, and_, text, desc, or_
import json
from extra import *
from config import Data, SecretData
import datetime
from flask_wtf.csrf import CSRFProtect
import os
import logging
from pathlib import Path
from math import asin, cos, radians, sin, sqrt

MAX_BREADS = 20
data = Data()
secret_data = SecretData()

app = Flask(__name__)
# Flask-SQLAlchemy settings
# Create DB and login manager instances here so models can reference them
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    Creates framework for it website to run (blackbox)
    """
    global app
    global db
    global login_manager
    # Use DATABASE_URL environment variable if provided; otherwise default to local SQLite for dev
    Bootstrap(app)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', "gdfgsksdflsdfjksjfkdsjfksjkfjdls")
    login_manager.init_app(app)
    dev_user = os.getenv('DEV_DB_USER', 'admin')
    dev_pass = os.getenv('DEV_DB_PASSWORD', '1234')
    dev_host = os.getenv('DEV_DB_HOST', '127.0.0.1')
    dev_port = os.getenv('DEV_DB_PORT', '3306')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{dev_user}:{dev_pass}@{dev_host}:{dev_port}/breadshop"
    # Optional: allow SQL logging in development
    app.config['SQLALCHEMY_ECHO'] = True

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    csrf = CSRFProtect(app)
    return app

# Note: create_app() will be invoked when running the app (__main__)

def find_num_breads(date,time):
        """

        """
        # stmt = text("""SELECT SUM(num_breads) FROM orders WHERE time_day = '"""+time+"""' AND date = '"""+str(date)+"""'""")
        # b = db.session.execute(stmt)
        # return b.first()[0]
        pass # Disabled for migration

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    group = db.Column(db.String(255), nullable=False)
    orders = relationship("Order", back_populates="customer")
    date = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean(), nullable=False, default=False)
    legacy = db.Column(db.Boolean(), nullable=False, default=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order = db.Column(db.String(5000), nullable=False)
    date = db.Column(db.Date)
    payed = db.Column(db.Boolean(), nullable=False, default=False)
    delivered = db.Column(db.Boolean(), nullable=False, default=False)
    time_day = db.Column(db.String(255), nullable=False)
    customer = relationship("User", back_populates="orders")
    client = db.Column(db.String(255), nullable=False)
    num_breads = db.Column(db.Integer)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    display_name = db.Column(db.String(255))
    display_name_es = db.Column(db.String(255))
    price = db.Column(db.Float)
    cost = db.Column(db.Float)
    benefits = db.Column(db.Float)
    category = db.Column(db.String(50))
    recipe_items = relationship("ProductIngredient", back_populates="product", cascade="all, delete-orphan")


class ProductIngredient(db.Model):
    __tablename__ = 'product_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantity = db.Column(db.Float)
    product = relationship("Product", back_populates="recipe_items")
    ingredient = relationship("Ingredient", back_populates="product_items")


class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    display_name = db.Column(db.String(255))
    display_name_es = db.Column(db.String(255))
    cost = db.Column(db.Float)
    product_items = relationship("ProductIngredient", back_populates="ingredient", cascade="all, delete-orphan")

class Bakery(db.Model):
    __tablename__ = 'bakeries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(500), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    base_delivery_cost = db.Column(db.Float, nullable=False, default=2.0)
    cost_per_km = db.Column(db.Float, nullable=False, default=0.5)

def calculate_distance_km(latitude_one, longitude_one, latitude_two, longitude_two):
    """Returns the great-circle distance between two coordinate pairs."""
    earth_radius_km = 6371.0
    latitude_delta = radians(latitude_two - latitude_one)
    longitude_delta = radians(longitude_two - longitude_one)
    haversine = (sin(latitude_delta / 2) ** 2
                 + cos(radians(latitude_one)) * cos(radians(latitude_two))
                 * sin(longitude_delta / 2) ** 2)
    return earth_radius_km * 2 * asin(sqrt(haversine))

def admin_required(f):
    """
    Makes sure only admin (user.id == 1) can acces when decorating page function and redirects to home if not
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
    #try:
        if current_user.is_authenticated:
            if current_user.id != 1:
               return redirect(url_for('home', next=request.url))
            else:
               return f(*args, **kwargs)
        else:
               return redirect(url_for('home', next=request.url))
    #except AttributeError:
        #return "Item not found", 400
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not current_user.is_authenticated:
                return redirect(url_for('home', next=request.url))
            else:
                return f(*args, **kwargs)
        except AttributeError:
            return "Item not found", 400
    return decorated_function

loggin_logger = Log("login ssuccseful", "login_info.log")
order_logger = Log("order succseful", "order_info.log")

def render_index(lang):
    """
    Presents the main webpage in either spaninsh or english and allows for ordering the right amount of bread if logged in
    Checks that not more than 15 breads ordered in a day
     """
    if lang == "es":
        order_form = PedidoPan()
    elif lang == "en":
        order_form = BreadOrderForm()
    order_form.validate_on_submit()
    errors = [None, None, None, None]
    if order_form.validate_on_submit(): #
        errors[0] = valid_day(order_form.date.data, lang)
        errors[1] = valid_period(order_form.date.data, order_form.day_time.data, lang)
        errors[3] = valid_month(order_form.date.data, lang)
        verifier = ReVerify(order_logger)
        order = {}
        # start of secondary vailidation
        valid_order = True
        #if (errors[0] or errors[1] or errors[3]):
        if (errors[0]  or errors[3]):
            valid_order = False
        order_logger.info(f"valid order:{valid_order}")
        # Build the order from every product currently available in the database.
        product_names = []
        try:
            db_products = Product.query.all()
            product_names = [p.name for p in db_products]
        except Exception:
            product_names = list(data.prices.keys())

        for name in product_names:
            try:
                raw_quantity = request.form.get(name, "0")
                if not verifier.verify_int(raw_quantity, 0, 6):
                    valid_order = False
                    continue
                quantity = int(raw_quantity)
                if quantity:
                    order[name] = quantity
            except Exception:
                valid_order = False
        if errors[1]:
            order_logger.info(f"{errors[1]}")
        if not verifier.verify_int(order_form.recurring.data, 0, 7):
            valid_order = False
        num_loafs = sum(list(order.values())[:len(order.values())-1])+sum(list(order.values())[len(order.values())-1:])/2
        if sum(order.values()) == 0:
            valid_order = False
        elif num_loafs > 15:
            if lang == "es":
                errors[2] = f"No se puede pedir mas de {MAX_BREADS} panes"
            elif lang == "en":
                errors[2] = f"You may not order more than {MAX_BREADS} breads"
            valid_order = False
        if valid_order:
            order_logger.info(f"{list(order.values())}--")
            # end of secondary validation
            date = order_form.date.data
            new_order_list = []
            for i in range(order_form.recurring.data+1):
                previous = find_num_breads(date,order_form.day_time.data)
                if num_loafs > MAX_BREADS:
                    if lang == "es":
                        errors[2] = f"No se puede pedir mas de {MAX_BREADS} panes"
                    elif lang == "en":
                        errors[2] = f"You may not order more than {MAX_BREADS} breads"
                elif previous == None:
                    new_order = Order(user_id=current_user.id, order=json.dumps(order), date=date, payed=False,
                    delivered=False, time_day=order_form.day_time.data, client=current_user.username, num_breads = num_loafs)
                    db.session.add(new_order)

                elif float(previous) + float(num_loafs) > MAX_BREADS:
                    if lang == "es":
                        errors[2] = f"No se puede pedir mas de {MAX_BREADS-previous} panes el {date}"
                    elif lang == "en":
                        errors[2] = f"You may not order more than {MAX_BREADS-previous} bread on {date}"
                else:
                    new_order = Order(user_id=current_user.id, order=json.dumps(order), date=date, payed=False,
                    delivered=False, time_day=order_form.day_time.data, client=current_user.username, num_breads = num_loafs)
                    db.session.add(new_order)

                date = date +datetime.timedelta(weeks=1)
                db.session.commit()
                order_logger.info("order received")
            if not errors[2]:
                return redirect(url_for("orders"))
    # fetch products for display (only include fields present in the order form)
    try:
        all_bread = Product.query.filter_by(category='bread').all()
        all_sweet = Product.query.filter_by(category='sweet').all()
        all_savory = Product.query.filter_by(category='savory').all()
    except Exception:
        all_bread = []
        all_sweet = []
        all_savory = []

    def _has_field(form, name):
        try:
            return hasattr(form, name)
        except Exception:
            return False

    # For display purposes, show all products in each category.
    # Keep filtering by form fields only for ordering logic elsewhere.
    bread = all_bread
    sweet = all_sweet
    savory = all_savory

    # Backwards compatibility: some code paths expect `loaves` and `sticks` variables.
    try:
        loaves = [p for p in bread if getattr(p, 'category', None) == 'loaf']
        sticks = [p for p in bread if getattr(p, 'category', None) == 'stick']
    except Exception:
        loaves = []
        sticks = []

    if lang == "es":
        # Spanish translations are available client-side; default server render is English
        return render_template("index.html", order_form=order_form, errors=errors, bread=bread, sweet=sweet, savory=savory, loaves=loaves, sticks=sticks, lang=lang)
    elif lang == "en":
        return render_template("index.html", order_form=order_form, errors=errors, bread=bread, sweet=sweet, savory=savory, loaves=loaves, sticks=sticks, lang=lang)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('index'))

@app.route('/home', methods=['POST', 'GET'])
@app.route('/main', methods=['POST', 'GET'])
@app.route('/app', methods=['POST', 'GET'])
@app.route('/site', methods=['POST', 'GET'])
@app.route('/lang', methods=['POST', 'GET'])
@app.route('/index.html', methods=['POST', 'GET'])
@app.route('/app/index', methods=['POST', 'GET'])
@app.route('/app/home', methods=['POST', 'GET'])
@app.route('/app/main', methods=['POST', 'GET'])
@app.route('/app/site', methods=['POST', 'GET'])
@app.route('/app/app', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    return render_index("en")

@app.route('/register', methods=['POST', 'GET'])
def register():
    """
    Backend of english registering a new user after checking the email and user do not exist already in database.
    If no issues happen logs in new user, adds them to database and redirects to the mainpage
    """
    form = RegisterForm()
    form.validate_on_submit()
    errors = [None, None]
    if form.validate_on_submit():
        valid = True
        if User.query.filter_by(username=form.username.data).first():
            errors[0] = 'username taken'
            valid = False
        if User.query.filter_by(email=form.email.data).first():
            errors[1] = "email taken"
            valid = False
        if True:
            verifier = ReVerify(loggin_logger)
            if verifier.verify_string(form.username.data) and verifier.verify_string(
                    form.password.data) and verifier.verify_string(form.group.data) and verifier.verify_string(
                form.email.data):
                new_user = User(username=form.username.data, password=generate_password_hash(str(form.password.data),
                    method="pbkdf2:sha256",salt_length=14),group=form.group.data, email=form.email.data, date=str(datetime.date.today()), verified = 0, legacy = 0)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                loggin_logger.info(f"user {form.username.data} from group {form.group.data} registered correctly")
                return redirect(url_for("index"))
    return render_template("register.html", form=form, errors=errors)


@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Backend of english registering a new user after checking the user and logs in.
    If no issues happen logs in new user, adds them to database and redirects to the mainpage
    """
    error_no_user = None
    form = LoginForm()
    verifier = ReVerify(loggin_logger)
    if form.validate_on_submit():
        if verifier.verify_string(form.password.data) and verifier.verify_string(form.username.data):
            user_db = User.query.filter_by(username=form.username.data).first()
            if user_db:  # check if user in database
                if werkzeug.security.check_password_hash(user_db.password,form.password.data):  # check if correct password
                    login_user(user_db)
                    loggin_logger.info(f"user {form.username.data} logged in correctly")
                    return redirect(url_for("index"))
            else:
                error_no_user = "No such user exists"
    return render_template("login.html", form=form, error_no_user = error_no_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/delete')
@login_required
def delete():
    """
    Deletes the user from database when directed from user page in english
    """
    user_id = current_user.id
    logout_user()
    stmt = text('''DELETE FROM "users" WHERE id IN ('''+str(user_id)+");")
    db.session.execute(stmt)
    stmt = text('''DELETE FROM "orders" WHERE user_id IN ('''+str(user_id)+");")
    db.session.execute(stmt)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/orders', methods=['POST', 'GET'])
@user_required
def orders():
    """
    Presents the user with their orders and allows them to delete them
    """
    user_id = current_user.id
    undelivered_orders = OrderViewer(db.session.query(Order).filter(
        and_(Order.user_id == user_id, Order.date > (datetime.date.today() - datetime.timedelta(days=1)))).all(), "en")
    delivered_orders = OrderViewer(db.session.query(Order).filter(
        and_(Order.user_id == user_id, Order.date < (datetime.date.today() - datetime.timedelta(days=1)))).order_by(desc(Order.id)).all(), "en")
    form = generate_basic_form(message="Delete",num_entries = 10)
    form = form()
    undelivered_orders.add_form(form)
    form.validate_on_submit()
    if form.validate_on_submit():
        for i in undelivered_orders:
            if undelivered_orders.form_data.data:
                db.session.delete(undelivered_orders.order_instance)
        db.session.commit()
        return redirect(url_for("orders"))
    return render_template("orders.html", form=form, delivered_orders=delivered_orders,undelivered_orders=undelivered_orders)

@app.route('/account', methods=['POST', 'GET'])
@user_required
def account():
    """
    Presents user with a way to change the inforamationif the user has their password and username in english
    """
    form = ModifyUser()
    form.validate_on_submit()
    errors = [None, None]
    user_data = {"user": current_user.username, "email": current_user.email, "group": current_user.group}
    if form.validate_on_submit():
        valid = True
        user = User.query.filter_by(username=current_user.username).first()
        if User.query.filter_by(username=form.username.data).first():
            if user.username != form.username.data:
                errors[0] = 'username taken'
                valid = False
        if User.query.filter_by(username=form.email.data).first():
            if user.email != form.email.data:
                errors[1] = "email taken"
                valid = False
        if valid:
            if werkzeug.security.check_password_hash(current_user.password, form.old_password.data):
                user.username = form.username.data
                user.email = form.email.data
                user.group = form.group.data
                if form.new_password.data:
                    user.password = generate_password_hash(str(form.new_password.data), method="pbkdf2:sha256",
                                                           salt_length=14)
                db.session.commit()
                return redirect(url_for("account"))
    return render_template("user.html", form=form, errors = errors, user_data=user_data)

@app.route('/info', methods=['POST', 'GET'])
def info():
    return(render_template("info.html"))

@app.route('/ingredients', methods=['POST', 'GET'])
def ingredients():
    """
    Displays all ingredients with search functionality by name in English or Spanish
    depending on the currently selected language.
    """
    search_query = request.args.get('search', '').strip()
    lang = request.args.get('lang', 'en')
    
    # Validate language parameter
    if lang not in ['en', 'es']:
        lang = 'en'
    
    try:
        all_ingredients = Ingredient.query.all()
    except Exception:
        all_ingredients = []
    
    # Filter ingredients based on search query
    filtered_ingredients = []
    if search_query:
        search_lower = search_query.lower()
        for ingredient in all_ingredients:
            # Search in both English and Spanish names
            name_en = (ingredient.display_name or ingredient.name or '').lower()
            name_es = (ingredient.display_name_es or ingredient.name or '').lower()
            
            if search_lower in name_en or search_lower in name_es:
                filtered_ingredients.append(ingredient)
    else:
        filtered_ingredients = all_ingredients
    
    # Sort ingredients by display name
    filtered_ingredients.sort(key=lambda x: (x.display_name_es if lang == 'es' and x.display_name_es else x.display_name or x.name))
    
    return render_template("ingredients.html", 
                         ingredients=filtered_ingredients, 
                         search_query=search_query,
                         lang=lang)

@app.route('/admin/ingredients', methods=['POST', 'GET'])
@admin_required
def manage_ingredients():
    """Allows the administrator to add or remove ingredients."""
    add_form = AddIngredientForm()
    delete_id = request.form.get('delete_id', type=int)
    message = None
    error = None

    if delete_id is not None:
        ingredient = db.session.get(Ingredient, delete_id)
        if ingredient is None:
            error = "Ingredient not found."
        elif ingredient.product_items:
            error = "Remove this ingredient from all product recipes before deleting it."
        else:
            db.session.delete(ingredient)
            db.session.commit()
            message = "Ingredient deleted."
    elif add_form.validate_on_submit():
        name = add_form.name.data.strip()
        if Ingredient.query.filter_by(name=name).first():
            error = "An ingredient with that internal name already exists."
        else:
            ingredient = Ingredient(
                name=name,
                display_name=add_form.display_name.data.strip(),
                display_name_es=add_form.display_name_es.data.strip(),
                cost=add_form.cost.data,
            )
            db.session.add(ingredient)
            db.session.commit()
            message = "Ingredient added."
            add_form = AddIngredientForm()

    all_ingredients = Ingredient.query.order_by(Ingredient.name).all()
    return render_template("manage_ingredients.html", add_form=add_form,
                           ingredients=all_ingredients, message=message, error=error)

@app.route('/delivery-cost', methods=['GET', 'POST'])
def delivery_cost():
    """Calculates a delivery estimate from a bakery to destination coordinates."""
    bakeries = Bakery.query.order_by(Bakery.name).all()
    form = DeliveryCostForm()
    form.bakery_id.choices = [(bakery.id, bakery.name) for bakery in bakeries]
    result = None

    if form.validate_on_submit():
        bakery = db.session.get(Bakery, form.bakery_id.data)
        if bakery is not None:
            distance_km = calculate_distance_km(
                bakery.latitude,
                bakery.longitude,
                form.destination_latitude.data,
                form.destination_longitude.data,
            )
            result = {
                "bakery": bakery,
                "distance_km": distance_km,
                "delivery_cost": bakery.base_delivery_cost + distance_km * bakery.cost_per_km,
            }

    return render_template("delivery_cost.html", form=form, bakeries=bakeries, result=result)

@app.route('/admin/bakeries', methods=['GET', 'POST'])
@admin_required
def manage_bakeries():
    """Allows the administrator to list, search, add, edit, and remove bakeries."""
    search_query = request.args.get('search', '').strip()
    edit_id = request.args.get('edit', type=int)
    form = BakeryForm()
    message = None
    error = None

    delete_id = request.form.get('delete_id', type=int)
    if delete_id is not None:
        bakery = db.session.get(Bakery, delete_id)
        if bakery is None:
            error = "Bakery not found."
        else:
            db.session.delete(bakery)
            db.session.commit()
            message = "Bakery deleted."
    elif form.validate_on_submit():
        bakery_id = form.id.data and int(form.id.data)
        bakery = db.session.get(Bakery, bakery_id) if bakery_id else None
        duplicate = Bakery.query.filter(Bakery.name == form.name.data.strip())
        if bakery is not None:
            duplicate = duplicate.filter(Bakery.id != bakery.id)

        if duplicate.first() is not None:
            error = "A bakery with that name already exists."
        else:
            if bakery is None:
                bakery = Bakery()
                db.session.add(bakery)
            bakery.name = form.name.data.strip()
            bakery.address = form.address.data.strip()
            bakery.latitude = form.latitude.data
            bakery.longitude = form.longitude.data
            bakery.base_delivery_cost = form.base_delivery_cost.data
            bakery.cost_per_km = form.cost_per_km.data
            db.session.commit()
            message = "Bakery updated." if bakery_id else "Bakery added."
            form = BakeryForm()
            edit_id = None
    elif edit_id:
        bakery = db.session.get(Bakery, edit_id)
        if bakery is None:
            error = "Bakery not found."
            edit_id = None
        else:
            form = BakeryForm(obj=bakery)

    bakeries_query = Bakery.query.order_by(Bakery.name)
    if search_query:
        search_pattern = f"%{search_query}%"
        bakeries_query = bakeries_query.filter(
            or_(Bakery.name.ilike(search_pattern), Bakery.address.ilike(search_pattern))
        )
    bakeries = bakeries_query.all()
    return render_template("manage_bakeries.html", form=form, bakeries=bakeries,
                           search_query=search_query, edit_id=edit_id,
                           message=message, error=error)

@app.route('/products', methods=['POST', 'GET'])
def products():
    """Displays all products with search and client-side language switching."""
    search_query = request.args.get('search', '').strip()
    lang = request.args.get('lang', 'en')

    if lang not in ['en', 'es']:
        lang = 'en'

    try:
        all_products = Product.query.order_by(Product.name).all()
    except Exception:
        all_products = []

    if search_query:
        search_lower = search_query.lower()
        filtered_products = [
            product for product in all_products
            if search_lower in (product.display_name or product.name or '').lower()
            or search_lower in (product.display_name_es or product.name or '').lower()
        ]
    else:
        filtered_products = all_products

    return render_template("products.html",
                           products=filtered_products,
                           search_query=search_query,
                           lang=lang)

# ADMIN PAGES
@app.route('/baker', methods=['POST', 'GET'])
@admin_required
def baker():
    """
    Admin page to see all orders and delete future ones
    """
    undelivered_orders = db.session.query(Order).filter(and_(Order.date > (datetime.date.today()))).all()
    undelivered_orders_viewer = OrderViewer(undelivered_orders, "en")
    delivered_orders = db.session.query(Order).filter(and_(Order.date < (datetime.date.today()))).order_by(desc(Order.id)).all()
    delivered_orders_viewer = OrderViewer(delivered_orders, "en")
    today_orders = db.session.query(Order).filter(Order.date == (datetime.date.today())).all()
    today_orders_viewer = OrderViewer(today_orders, "en")
    today_orders_viewer.simple_view()
    form = generate_basic_form(message="Delete",num_entries = 50)
    form = form()
    undelivered_orders_viewer.add_form(form)
    form.validate_on_submit()
    if form.validate_on_submit():
        for i in undelivered_orders_viewer:
            if undelivered_orders_viewer.form_data.data:
                db.session.delete(undelivered_orders_viewer.order_instance)
                db.session.commit()
        return redirect(url_for("baker"))
    return render_template("admin.html", form=form, undelivered_orders=undelivered_orders_viewer,
                           today_orders=today_orders_viewer, delivered_orders = delivered_orders_viewer)

@app.route('/payments', methods=['POST', 'GET'])
@admin_required
def payments():
    """
    Admin page to see all orders and delete future ones
    """
    delivered_orders = OrderViewer(db.session.query(Order).filter(
        Order.date <= datetime.date.today(),Order.payed == 0).all(), "en")
    form = generate_basic_form(message ="Mark as payed",num_entries = 50)
    form = form()
    delivered_orders.add_form(form)
    form.validate_on_submit()
    if form.validate_on_submit():
        for i in delivered_orders:
            if delivered_orders.form_data.data:
                stmt = text(f'''UPDATE orders SET payed = 1 WHERE id = {str(delivered_orders.order_instance.id)};''')
                db.session.execute(stmt)
        db.session.commit()
        return redirect(url_for("payments"))
    return render_template("payments.html", form=form, delivered_orders=delivered_orders)

@app.route('/future_payments', methods=['POST', 'GET'])
@admin_required
def future_payments():
    """
    Admin page to see all orders and delete future ones
    """
    delivered_orders = OrderViewer(db.session.query(Order).filter(
        Order.date > datetime.date.today(),Order.payed == 0).all(), "en")
    form = generate_basic_form(message ="Mark as payed",num_entries = 50)
    form = form()
    delivered_orders.add_form(form)
    form.validate_on_submit()
    if form.validate_on_submit():
        for i in delivered_orders:
            if delivered_orders.form_data.data:
                stmt = text(f'''UPDATE orders SET payed = 1 WHERE id = {str(delivered_orders.order_instance.id)};''')
                db.session.execute(stmt)
        db.session.commit()
        return redirect(url_for("future_payments"))
    return render_template("future_payments.html", form=form, delivered_orders=delivered_orders)

@app.route('/baker_users', methods=['POST', 'GET'])
@admin_required
def baker_users():
    """
    Admin page to control and allow the deleting of users by admin
    """
    users = db.session.query(User).all()
    form = DeleteUserForm()
    form.validate_on_submit()
    if form.validate_on_submit():
        stmt = text('''DELETE FROM users WHERE id IN ('''+str(form.users_to_delete.data)+");")
        db.session.execute(stmt)
        stmt = text('''DELETE FROM orders WHERE user_id IN ('''+str(form.users_to_delete.data)+");")
        db.session.execute(stmt)
        db.session.commit()
        return redirect(url_for("baker_users"))
    return render_template("admin_users.html", users = users,form = form)

@app.route('/statistics')
@admin_required
def statistics():
    """
    Admin page to see information on last months orders
    """
    date = datetime.date.today()
    first_day_month = date.replace(day = 1,month=date.month-1)
    last_day_month =  date.replace(day = 1)+timedelta(days=-1)
    orders_last_month = db.session.query(Order.order).filter(
        and_(Order.date >= first_day_month, Order.date <= last_day_month)).all()
    orders_this_month =  db.session.query(Order.order).filter(
        and_(Order.date >= date.replace(day = 1))).all()
    generator = Statistic_generator(orders_last_month,orders_this_month)
    return render_template("statistics.html",data = generator)

@app.route('/legacy<int:user_id>')
@admin_required
def legacies(user_id):
    """
    Admin page to control and allow new users to order bread
    """
    user = User.query.get(user_id)
    if user:
        return render_template("legacy.html")
    else:
        return "User not found", 404


@app.route('/botcontrol')
@admin_required
def bot_control():
    return render_template("robot.html")

@app.route('/verify', methods=['POST', 'GET'])
@admin_required
def verify():
    """
    Admin page to control and allow new users to order bread
    """
    users = db.session.query(User).filter(User.verified == 0).all()
    form = DeleteUserForm()
    form.validate_on_submit()
    if form.validate_on_submit():
        stmt = text(f'''UPDATE users SET verified = 1 WHERE id IN ('''+str(form.users_to_delete.data)+");")
        db.session.execute(stmt)
        db.session.commit()
        return redirect(url_for("verify"))
    return render_template("verify.html", users = users,form = form)

@app.route('/legacymanager', methods=['POST', 'GET'])
@admin_required
def legacymanager():
    """
    Admin page to control and allow new users to order bread
    """
    legacy_users = db.session.query(User).filter(User.legacy == 1).all()
    remove_form = RemoveLegacyForm()
    remove_form.validate_on_submit()
    nonlegacy_users = db.session.query(User).filter(User.legacy == 0).all()
    add_form = AddLegacyForm()
    add_form.validate_on_submit()
    if remove_form.validate_on_submit() and remove_form.users_to_remove.data:
        stmt = text(f'''UPDATE users SET legacy = 0 WHERE id IN ('''+str(remove_form.users_to_remove.data)+");")
        db.session.execute(stmt)
        db.session.commit()
        return redirect(url_for("baker"))
    if add_form.validate_on_submit() and add_form.users_to_add.data:
        stmt = text(f'''UPDATE users SET legacy = 1 WHERE id IN ('''+str(add_form.users_to_add.data)+");")
        db.session.execute(stmt)
        db.session.commit()
        return redirect(url_for("legacymanager"))
    return render_template("legacymanager.html",legacy_users = legacy_users,remove_form = remove_form,nonlegacy_users = nonlegacy_users,add_form = add_form)

# Run Stuff
if __name__ == "__main__":
    # Initialize app, create DB tables if needed, then run
    app = create_app()
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        created = False
        # If using SQLite, check whether file exists before creating
        if db_uri.startswith('sqlite:///'):
            sqlite_path = Path(app.config.get('SQLITE_DB_PATH'))
            if not sqlite_path.exists():
                logging.info(f"SQLite DB not found at {sqlite_path}, creating new database and tables.")
                db.create_all()
                created = True
            else:
                logging.info(f"SQLite DB found at {sqlite_path}, ensuring tables exist (create_all).")
                db.create_all()
        else:
            # For other DB backends, attempt to create missing tables (idempotent)
            try:
                db.create_all()
                created = True
            except Exception as e:
                logging.error(f"Could not create tables: {e}")
        if created:
            print("Database/tables created or updated.")
        else:
            print("Database already existed or no changes required.")
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
