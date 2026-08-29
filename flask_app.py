import werkzeug.security
from flask import Flask, render_template, redirect, url_for, request, flash
from functools import wraps
from flask_bootstrap import Bootstrap
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, Integer, String, Float, Boolean, Date, DateTime, Text, and_, text, desc, or_
import json
from extra import *
from config import Data, SecretData
import datetime
from flask_wtf.csrf import CSRFProtect
import os
import logging
from pathlib import Path
from math import asin, cos, radians, sin, sqrt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

MAX_BREADS = 20
data = Data()
secret_data = SecretData()

app = Flask(__name__)
# Flask-SQLAlchemy settings
# Create DB and login manager instances here so models can reference them
db = SQLAlchemy()
login_manager = LoginManager()

def get_serializer():
    secret = app.config.get('SECRET_KEY', "gdfgsksdflsdfjksjfkdsjfksjkfjdls")
    return URLSafeTimedSerializer(secret)

bootstrap = Bootstrap()
csrf = CSRFProtect()
_app_initialized = False

def create_app(config_overrides=None):
    """
    Creates framework for website to run (blackbox)
    """
    global app, db, login_manager, _app_initialized
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', "gdfgsksdflsdfjksjfkdsjfksjkfjdls")
    dev_user = os.getenv('DEV_DB_USER', 'admin')
    dev_pass = os.getenv('DEV_DB_PASSWORD', '1234')
    dev_host = os.getenv('DEV_DB_HOST', '127.0.0.1')
    dev_port = os.getenv('DEV_DB_PORT', '3306')
    db_uri = os.getenv('DATABASE_URL')
    if not db_uri:
        db_uri = f"mysql+pymysql://{dev_user}:{dev_pass}@{dev_host}:{dev_port}/breadshop"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_overrides:
        app.config.update(config_overrides)

    if not _app_initialized:
        bootstrap.init_app(app)
        login_manager.init_app(app)
        db.init_app(app)
        csrf.init_app(app)
        _app_initialized = True

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
    address = db.Column(db.String(500), nullable=True)
    delivery_notes = db.Column(db.String(500), nullable=True)
    is_admin = db.Column(db.Boolean(), nullable=False, default=False)

    def is_superadmin(self):
        """User with id=1 is the superadmin."""
        return self.id == 1

    def has_admin_access(self):
        """True for superadmin (id=1) and any promoted admin."""
        return self.id == 1 or self.is_admin


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    preferred_language = db.Column(db.String(10), default='en')
    dark_mode = db.Column(db.Boolean, default=False)
    default_delivery_notes = db.Column(db.String(500), nullable=True)
    user = relationship("User", backref=db.backref("preferences", uselist=False))


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    @classmethod
    def get_setting(cls, key, default=None):
        try:
            setting = cls.query.filter_by(key=key).first()
            return setting.value if setting else default
        except Exception:
            return default

    @classmethod
    def set_setting(cls, key, value, description=None):
        try:
            setting = cls.query.filter_by(key=key).first()
            if not setting:
                setting = cls(key=key, value=str(value), description=description)
                db.session.add(setting)
            else:
                setting.value = str(value)
                if description:
                    setting.description = description
            db.session.commit()
            return setting
        except Exception:
            db.session.rollback()
            return None


class DeliveryPerson(db.Model):
    __tablename__ = 'delivery_persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    vehicle_type = db.Column(db.String(100), nullable=True, default="Van")
    active = db.Column(db.Boolean, nullable=False, default=True)
    orders = relationship("Order", back_populates="delivery_person")


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
    delivery_option = db.Column(db.String(50), nullable=True, default='profile')
    delivery_address = db.Column(db.String(500), nullable=True)
    delivery_notes = db.Column(db.String(500), nullable=True)
    delivery_latitude = db.Column(db.Float, nullable=True)
    delivery_longitude = db.Column(db.Float, nullable=True)
    assigned_delivery_id = db.Column(db.Integer, db.ForeignKey('delivery_persons.id'), nullable=True)
    delivery_person = relationship("DeliveryPerson", back_populates="orders")


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
    stock = db.Column(db.Float, nullable=False, default=0.0)
    unit = db.Column(db.String(50), nullable=False, default='kg')
    product_items = relationship("ProductIngredient", back_populates="ingredient", cascade="all, delete-orphan")
    logs = relationship("InventoryLog", back_populates="ingredient", cascade="all, delete-orphan")


class InventoryLog(db.Model):
    __tablename__ = 'inventory_logs'
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    change_amount = db.Column(db.Float, nullable=False)
    current_stock = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    ingredient = relationship("Ingredient", back_populates="logs")


class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    shifts = relationship("StaffTimetable", back_populates="staff", cascade="all, delete-orphan")


class StaffTimetable(db.Model):
    __tablename__ = 'staff_timetables'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False, default=0) # 0=Mon, ..., 6=Sun
    shift_date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.String(20), nullable=False, default="06:00")
    end_time = db.Column(db.String(20), nullable=False, default="14:00")
    notes = db.Column(db.String(255), nullable=True)
    staff = relationship("Staff", back_populates="shifts")


class Bakery(db.Model):
    __tablename__ = 'bakeries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(500), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    base_delivery_cost = db.Column(db.Float, nullable=False, default=2.0)
    cost_per_km = db.Column(db.Float, nullable=False, default=0.5)

def deduct_inventory_for_order(order_dict, order_id=None):
    """Deducts ingredient stock based on recipes for ordered products and records logs."""
    try:
        for item_name, qty in order_dict.items():
            if not qty:
                continue
            product = Product.query.filter_by(name=item_name).first()
            if product and product.recipe_items:
                for recipe_item in product.recipe_items:
                    ingredient = db.session.get(Ingredient, recipe_item.ingredient_id)
                    if ingredient:
                        amount_to_deduct = (recipe_item.quantity or 0.0) * float(qty)
                        current_val = ingredient.stock if ingredient.stock is not None else 0.0
                        ingredient.stock = current_val - amount_to_deduct
                        log = InventoryLog(
                            ingredient_id=ingredient.id,
                            change_amount=-amount_to_deduct,
                            current_stock=ingredient.stock,
                            reason=f"Order #{order_id} ({qty}x {item_name})" if order_id else f"Order ({qty}x {item_name})",
                            timestamp=datetime.datetime.now(datetime.timezone.utc)
                        )
                        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deducting inventory: {e}")

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
    Allows access to users with admin access (superadmin id=1 or is_admin=True).
    Redirects to home if not authenticated or not admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.has_admin_access():
                return f(*args, **kwargs)
            else:
                return redirect(url_for('home', next=request.url))
        else:
            return redirect(url_for('home', next=request.url))
    return decorated_function

def superadmin_required(f):
    """Only the superadmin (id=1) can access. Used for admin promotion pages."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return f(*args, **kwargs)
        return redirect(url_for('home', next=request.url))
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

        # Check site-wide email verification requirement (todo #10)
        if current_user.is_authenticated:
            req_verif = SiteSetting.get_setting('require_email_verification', 'false') == 'true'
            if req_verif and not current_user.verified:
                if lang == "es":
                    errors[2] = "Se requiere verificación de correo antes de realizar pedidos. Revisa tus preferencias o correo."
                else:
                    errors[2] = "Email verification is required before placing orders. Please check your settings or email."
                valid_order = False

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
            # delivery details (todos #2 #4)
            delivery_option = request.form.get('delivery_option', 'profile')
            delivery_notes = request.form.get('delivery_notes', '').strip()
            delivery_address = request.form.get('delivery_address', '').strip()
            raw_lat = request.form.get('delivery_latitude', '')
            raw_lng = request.form.get('delivery_longitude', '')
            try:
                delivery_lat = float(raw_lat) if raw_lat else None
            except ValueError:
                delivery_lat = None
            try:
                delivery_lng = float(raw_lng) if raw_lng else None
            except ValueError:
                delivery_lng = None

            if delivery_option == 'profile' and current_user.is_authenticated:
                if not delivery_address:
                    delivery_address = current_user.address or ""
                if not delivery_notes:
                    delivery_notes = current_user.delivery_notes or ""

            # end of secondary validation
            date = order_form.date.data
            for i in range(order_form.recurring.data+1):
                previous = find_num_breads(date,order_form.day_time.data)
                if num_loafs > MAX_BREADS:
                    if lang == "es":
                        errors[2] = f"No se puede pedir mas de {MAX_BREADS} panes"
                    elif lang == "en":
                        errors[2] = f"You may not order more than {MAX_BREADS} breads"
                elif previous == None:
                    new_order = Order(
                        user_id=current_user.id,
                        order=json.dumps(order),
                        date=date,
                        payed=False,
                        delivered=False,
                        time_day=order_form.day_time.data,
                        client=current_user.username,
                        num_breads=num_loafs,
                        delivery_option=delivery_option,
                        delivery_address=delivery_address or None,
                        delivery_notes=delivery_notes or None,
                        delivery_latitude=delivery_lat,
                        delivery_longitude=delivery_lng
                    )
                    db.session.add(new_order)
                    db.session.flush()
                    deduct_inventory_for_order(order, new_order.id)

                elif float(previous) + float(num_loafs) > MAX_BREADS:
                    if lang == "es":
                        errors[2] = f"No se puede pedir mas de {MAX_BREADS-previous} panes el {date}"
                    elif lang == "en":
                        errors[2] = f"You may not order more than {MAX_BREADS-previous} bread on {date}"
                else:
                    new_order = Order(
                        user_id=current_user.id,
                        order=json.dumps(order),
                        date=date,
                        payed=False,
                        delivered=False,
                        time_day=order_form.day_time.data,
                        client=current_user.username,
                        num_breads=num_loafs,
                        delivery_option=delivery_option,
                        delivery_address=delivery_address or None,
                        delivery_notes=delivery_notes or None,
                        delivery_latitude=delivery_lat,
                        delivery_longitude=delivery_lng
                    )
                    db.session.add(new_order)
                    db.session.flush()
                    deduct_inventory_for_order(order, new_order.id)

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
                form.email.data) and (not form.address.data or verifier.verify_string(form.address.data)):
                new_user = User(username=form.username.data, password=generate_password_hash(str(form.password.data),
                    method="pbkdf2:sha256",salt_length=14),group=form.group.data, email=form.email.data,
                    address=form.address.data.strip() or None, date=str(datetime.date.today()), verified = 0, legacy = 0)
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
    page = request.args.get('page', 1, type=int)
    per_page = 20

    undelivered_orders = OrderViewer(db.session.query(Order).filter(
        and_(Order.user_id == user_id, Order.date > (datetime.date.today() - datetime.timedelta(days=1)))).all(), "en")

    delivered_query = db.session.query(Order).filter(
        and_(Order.user_id == user_id, Order.date < (datetime.date.today() - datetime.timedelta(days=1)))).order_by(desc(Order.id))
    pagination = delivered_query.paginate(page=page, per_page=per_page, error_out=False)
    delivered_orders = OrderViewer(pagination.items, "en")

    form = generate_basic_form(message="Delete", num_entries=10)
    form = form()
    undelivered_orders.add_form(form)
    form.validate_on_submit()
    if form.validate_on_submit():
        for i in undelivered_orders:
            if undelivered_orders.form_data.data:
                db.session.delete(undelivered_orders.order_instance)
        db.session.commit()
        return redirect(url_for("orders"))
    return render_template("orders.html", form=form, delivered_orders=delivered_orders,
                           undelivered_orders=undelivered_orders, pagination=pagination)


@app.route('/account', methods=['POST', 'GET'])
@user_required
def account():
    """
    Presents user with a way to change the information if the user has their password and username in english
    """
    form = ModifyUser()
    form.validate_on_submit()
    errors = [None, None]
    user_data = {
        "user": current_user.username,
        "email": current_user.email,
        "group": current_user.group,
        "address": current_user.address or "",
        "delivery_notes": current_user.delivery_notes or ""
    }
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
                user.address = form.address.data.strip() if form.address.data else None
                user.delivery_notes = form.delivery_notes.data.strip() if form.delivery_notes.data else None
                if form.new_password.data:
                    user.password = generate_password_hash(str(form.new_password.data), method="pbkdf2:sha256",
                                                           salt_length=14)
                db.session.commit()
                return redirect(url_for("account"))
    return render_template("user.html", form=form, errors=errors, user_data=user_data)

@app.route('/info', methods=['POST', 'GET'])
def info():
    return(render_template("info.html"))

@app.route('/ingredients', methods=['POST', 'GET'])
def ingredients():
    """Redirects to manage_ingredients route."""
    return redirect(url_for('manage_ingredients'))

@app.route('/admin/ingredients', methods=['POST', 'GET'])
@admin_required
def manage_ingredients():
    """Allows the administrator to list, add, edit, and remove ingredients."""
    add_form = AddIngredientForm()
    edit_form = EditIngredientForm()
    edit_id = request.args.get('edit', type=int)
    delete_id = request.form.get('delete_id', type=int)
    action = request.form.get('action', '')
    message = None
    error = None

    if delete_id is not None or action == 'delete':
        target_id = delete_id or request.form.get('id', type=int)
        ingredient = db.session.get(Ingredient, target_id) if target_id else None
        if ingredient is None:
            error = "Ingredient not found."
        elif ingredient.product_items:
            error = "Remove this ingredient from all product recipes before deleting it."
        else:
            db.session.delete(ingredient)
            db.session.commit()
            message = "Ingredient deleted."
    elif action == 'edit' or (request.method == 'POST' and request.form.get('form_type') == 'edit'):
        ing_id = request.form.get('id', type=int) or (edit_form.id.data and int(edit_form.id.data))
        ingredient = db.session.get(Ingredient, ing_id) if ing_id else None
        if not ingredient:
            error = "Ingredient not found."
        else:
            name = request.form.get('name', '').strip()
            display_name = request.form.get('display_name', '').strip()
            display_name_es = request.form.get('display_name_es', '').strip()
            raw_cost = request.form.get('cost', '')
            raw_stock = request.form.get('stock', '')
            unit = request.form.get('unit', 'kg').strip() or 'kg'
            try:
                cost = float(raw_cost) if raw_cost != '' else None
            except ValueError:
                cost = ingredient.cost
            try:
                stock = float(raw_stock) if raw_stock != '' else ingredient.stock
            except ValueError:
                stock = ingredient.stock

            existing = Ingredient.query.filter(Ingredient.name == name, Ingredient.id != ing_id).first()
            if existing:
                error = "An ingredient with that internal name already exists."
            elif not name or not display_name or not display_name_es:
                error = "Name fields cannot be empty."
            else:
                ingredient.name = name
                ingredient.display_name = display_name
                ingredient.display_name_es = display_name_es
                ingredient.cost = cost
                ingredient.stock = stock if stock is not None else 0.0
                ingredient.unit = unit
                db.session.commit()
                message = "Ingredient updated."
                edit_id = None
    elif add_form.validate_on_submit() and (request.form.get('form_type') == 'add' or 'submit' in request.form):
        name = add_form.name.data.strip()
        if Ingredient.query.filter_by(name=name).first():
            error = "An ingredient with that internal name already exists."
        else:
            ingredient = Ingredient(
                name=name,
                display_name=add_form.display_name.data.strip(),
                display_name_es=add_form.display_name_es.data.strip(),
                cost=add_form.cost.data,
                stock=add_form.stock.data or 0.0,
                unit=add_form.unit.data or 'kg'
            )
            db.session.add(ingredient)
            db.session.commit()
            message = "Ingredient added."
            add_form = AddIngredientForm()

    if edit_id and not error and request.method == 'GET':
        edit_ing = db.session.get(Ingredient, edit_id)
        if edit_ing:
            edit_form.id.data = edit_ing.id
            edit_form.name.data = edit_ing.name
            edit_form.display_name.data = edit_ing.display_name
            edit_form.display_name_es.data = edit_ing.display_name_es
            edit_form.cost.data = edit_ing.cost
            edit_form.stock.data = edit_ing.stock
            edit_form.unit.data = edit_ing.unit

    all_ingredients = Ingredient.query.order_by(Ingredient.name).all()
    return render_template("manage_ingredients.html", add_form=add_form, edit_form=edit_form,
                           ingredients=all_ingredients, edit_id=edit_id, message=message, error=error)

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
    Admin page to see all unpaid orders and mark them as paid, with pagination.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 50
    delivered_query = db.session.query(Order).filter(
        Order.date <= datetime.date.today(), Order.payed == 0).order_by(desc(Order.id))
    pagination = delivered_query.paginate(page=page, per_page=per_page, error_out=False)
    delivered_orders = OrderViewer(pagination.items, "en")
    form = generate_basic_form(message="Mark as payed", num_entries=50)
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
    return render_template("payments.html", form=form, delivered_orders=delivered_orders, pagination=pagination)


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
    Admin page to control, view, add, edit, and delete users.
    """
    add_form = RegisterForm()
    edit_form = AdminEditUserForm()
    form = DeleteUserForm()
    delete_id = request.form.get('delete_id', type=int)
    action = request.form.get('action', '')
    message = None
    error = None

    if delete_id is not None or action == 'delete':
        target_id = delete_id or request.form.get('id', type=int)
        if target_id == 1:
            error = "Cannot delete the primary admin user."
        else:
            user = db.session.get(User, target_id) if target_id else None
            if user:
                stmt = text(f"DELETE FROM orders WHERE user_id = {target_id}")
                db.session.execute(stmt)
                db.session.delete(user)
                db.session.commit()
                message = "User deleted successfully."
            else:
                error = "User not found."
    elif action == 'add' or (request.method == 'POST' and request.form.get('form_type') == 'add'):
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        group = request.form.get('group', '').strip()
        password = request.form.get('password', '').strip()
        verified = True if request.form.get('verified') in ['true', 'on', '1', 1, True] else False
        legacy = True if request.form.get('legacy') in ['true', 'on', '1', 1, True] else False

        if User.query.filter_by(username=username).first():
            error = "Username is already taken by another user."
        elif User.query.filter_by(email=email).first():
            error = "Email is already taken by another user."
        elif not username or not email or not group or not password:
            error = "Username, Email, Group, and Password cannot be empty."
        else:
            new_user = User(
                username=username,
                email=email,
                group=group,
                password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=14),
                date=str(datetime.date.today()),
                verified=verified,
                legacy=legacy
            )
            db.session.add(new_user)
            db.session.commit()
            message = "User added successfully."
    elif action == 'edit' or (request.method == 'POST' and request.form.get('form_type') == 'edit'):
        user_id = request.form.get('id', type=int) or (edit_form.id.data and int(edit_form.id.data))
        user = db.session.get(User, user_id) if user_id else None
        if not user:
            error = "User not found."
        else:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            group = request.form.get('group', '').strip()
            verified = True if request.form.get('verified') in ['true', 'on', '1', 1, True] else False
            legacy = True if request.form.get('legacy') in ['true', 'on', '1', 1, True] else False
            new_password = request.form.get('new_password', '').strip()

            existing_user = User.query.filter(User.username == username, User.id != user_id).first()
            existing_email = User.query.filter(User.email == email, User.id != user_id).first()

            if existing_user:
                error = "Username is already taken by another user."
            elif existing_email:
                error = "Email is already in use by another user."
            elif not username or not email or not group:
                error = "Username, Email, and Group fields cannot be empty."
            else:
                user.username = username
                user.email = email
                user.group = group
                user.verified = verified
                user.legacy = legacy
                if new_password:
                    user.password = generate_password_hash(new_password, method="pbkdf2:sha256", salt_length=14)
                db.session.commit()
                message = "User updated successfully."
    elif form.validate_on_submit() and form.users_to_delete.data:
        try:
            target_ids = [int(x.strip()) for x in form.users_to_delete.data.split(',') if x.strip().isdigit()]
            for uid in target_ids:
                if uid != 1:
                    db.session.execute(text(f"DELETE FROM orders WHERE user_id = {uid}"))
                    db.session.execute(text(f"DELETE FROM users WHERE id = {uid}"))
            db.session.commit()
            message = "Selected user(s) deleted."
        except Exception as e:
            error = f"Error deleting users: {e}"

    users = db.session.query(User).order_by(User.id).all()
    return render_template("admin_users.html", users=users, form=form, add_form=add_form, edit_form=edit_form, message=message, error=error)

@app.route('/admin/promote', methods=['POST', 'GET'])
@superadmin_required
def promote_admin():
    """
    Superadmin-only page to grant or revoke admin privileges for users.
    """
    message = None
    error = None
    action = request.form.get('action', '')
    target_id = request.form.get('user_id', type=int)

    if request.method == 'POST' and target_id:
        if target_id == 1:
            error = "Cannot change the superadmin's admin status."
        else:
            user = db.session.get(User, target_id)
            if not user:
                error = "User not found."
            elif action == 'grant':
                user.is_admin = True
                db.session.commit()
                message = f"Admin access granted to {user.username}."
            elif action == 'revoke':
                user.is_admin = False
                db.session.commit()
                message = f"Admin access revoked from {user.username}."

    all_users = db.session.query(User).filter(User.id != 1).order_by(User.username).all()
    return render_template("promote_admin.html", users=all_users, message=message, error=error)

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

# ── User Preferences & Settings (todo #5) ──────────────────────────────
@app.route('/settings', methods=['GET', 'POST'])
@user_required
def user_settings():
    """Page for user to configure preferences (language, dark theme, delivery instructions)."""
    pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id, preferred_language='en', dark_mode=False, default_delivery_notes=current_user.delivery_notes)
        db.session.add(pref)
        db.session.commit()

    form = UserPreferencesForm(obj=pref)
    message = None

    if form.validate_on_submit():
        pref.preferred_language = form.preferred_language.data
        pref.dark_mode = form.dark_mode.data
        pref.default_delivery_notes = form.default_delivery_notes.data.strip() if form.default_delivery_notes.data else None
        current_user.delivery_notes = pref.default_delivery_notes
        db.session.commit()
        message = "Preferences updated successfully."

    return render_template("settings.html", form=form, pref=pref, message=message)

# ── Email Verification (todo #10) ──────────────────────────────────────
@app.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verifies a user's email using a signed token."""
    serializer = get_serializer()
    try:
        user_id = serializer.loads(token, salt='email-verify', max_age=86400)
    except (SignatureExpired, BadSignature):
        return render_template("verify_result.html", success=False, message="The verification link is invalid or has expired.")

    user = db.session.get(User, user_id)
    if not user:
        return render_template("verify_result.html", success=False, message="User not found.")

    user.verified = True
    db.session.commit()
    return render_template("verify_result.html", success=True, message=f"Email for {user.username} verified successfully! You can now place orders.")

@app.route('/send-verification', methods=['POST'])
@user_required
def send_verification_email():
    """Generates and logs an email verification link for the current user."""
    serializer = get_serializer()
    token = serializer.dumps(current_user.id, salt='email-verify')
    verify_url = url_for('verify_email', token=token, _external=True)
    loggin_logger.info(f"Verification email link for {current_user.email}: {verify_url}")
    flash(f"Verification link generated: {verify_url}", "info")
    return redirect(url_for('user_settings'))

# ── Admin Site Settings (todo #5, #10) ──────────────────────────────────
@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Admin settings page for global site configuration."""
    form = AdminSettingsForm()
    message = None

    if request.method == 'GET':
        form.require_email_verification.data = (SiteSetting.get_setting('require_email_verification', 'false') == 'true')
        form.admin_notification_email.data = SiteSetting.get_setting('admin_notification_email', 'admin@breadshop.com')

    if form.validate_on_submit():
        SiteSetting.set_setting('require_email_verification', 'true' if form.require_email_verification.data else 'false', 'Require email verification before ordering')
        SiteSetting.set_setting('admin_notification_email', form.admin_notification_email.data.strip(), 'Admin email for daily summary and alerts')
        message = "Site settings saved successfully."

    return render_template("admin_settings.html", form=form, message=message)

# ── Inventory & Stock Management (todo #8, #9) ─────────────────────────
@app.route('/admin/inventory', methods=['GET', 'POST'])
@admin_required
def manage_inventory():
    """Admin page to view inventory, adjust stock levels, and inspect stock change logs."""
    adjust_form = StockAdjustmentForm()
    all_ingredients = Ingredient.query.order_by(Ingredient.name).all()
    adjust_form.ingredient_id.choices = [(i.id, f"{i.display_name or i.name} (Current: {i.stock:.2f} {i.unit})") for i in all_ingredients]
    message = None
    error = None

    logs = InventoryLog.query.order_by(InventoryLog.timestamp.desc()).limit(100).all()
    low_stock = [i for i in all_ingredients if (i.stock or 0.0) <= 5.0]

    return render_template("inventory.html", ingredients=all_ingredients, form=adjust_form, logs=logs, low_stock=low_stock, message=message, error=error)

@app.route('/admin/inventory/adjust', methods=['POST'])
@admin_required
def adjust_inventory():
    """Applies a manual stock adjustment and records an inventory log."""
    adjust_form = StockAdjustmentForm()
    all_ingredients = Ingredient.query.order_by(Ingredient.name).all()
    adjust_form.ingredient_id.choices = [(i.id, f"{i.display_name or i.name}") for i in all_ingredients]

    if adjust_form.validate_on_submit():
        ingredient = db.session.get(Ingredient, adjust_form.ingredient_id.data)
        if not ingredient:
            flash("Ingredient not found.", "danger")
            return redirect(url_for('manage_inventory'))

        adj_type = adjust_form.adjustment_type.data
        amount = float(adjust_form.amount.data)
        reason = adjust_form.reason.data.strip() if adjust_form.reason.data else "Manual adjustment"
        curr = ingredient.stock if ingredient.stock is not None else 0.0

        if adj_type == 'add':
            ingredient.stock = curr + amount
            change = amount
        elif adj_type == 'deduct':
            ingredient.stock = max(0.0, curr - amount)
            change = -amount
        elif adj_type == 'set':
            change = amount - curr
            ingredient.stock = max(0.0, amount)

        log = InventoryLog(
            ingredient_id=ingredient.id,
            change_amount=change,
            current_stock=ingredient.stock,
            reason=f"{reason} ({adj_type})",
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        flash(f"Stock for {ingredient.display_name or ingredient.name} updated to {ingredient.stock:.2f} {ingredient.unit}.", "success")
    else:
        flash("Invalid form data for stock adjustment.", "danger")

    return redirect(url_for('manage_inventory'))

# ── Daily Admin Order & Payment Email Summary (todo #17) ────────────────
@app.route('/admin/daily-summary', methods=['GET', 'POST'])
@admin_required
def daily_summary():
    """Shows daily order & payment statistics and triggers the summary email to admin."""
    date_str = request.args.get('date', str(datetime.date.today()))
    try:
        target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        target_date = datetime.date.today()

    orders_for_day = Order.query.filter_by(date=target_date).all()
    admin_email = SiteSetting.get_setting('admin_notification_email', 'admin@breadshop.com')

    total_orders = len(orders_for_day)
    total_loaves = 0
    total_sticks = 0
    total_revenue = 0.0
    paid_count = 0
    unpaid_count = 0
    paid_revenue = 0.0
    unpaid_revenue = 0.0

    order_details = []
    for ord_obj in orders_for_day:
        items = json.loads(ord_obj.order) if ord_obj.order else {}
        ord_price = 0.0
        for item, qty in items.items():
            price = data.prices.get(item, 0.0)
            ord_price += price * qty
            if item.endswith('stick'):
                total_sticks += qty
            else:
                total_loaves += qty
        total_revenue += ord_price
        if ord_obj.payed:
            paid_count += 1
            paid_revenue += ord_price
        else:
            unpaid_count += 1
            unpaid_revenue += ord_price

        order_details.append({
            'id': ord_obj.id,
            'client': ord_obj.client,
            'items': items,
            'price': ord_price,
            'payed': ord_obj.payed,
            'time_day': ord_obj.time_day,
            'address': ord_obj.delivery_address,
            'notes': ord_obj.delivery_notes
        })

    summary_data = {
        'date': target_date,
        'total_orders': total_orders,
        'total_loaves': total_loaves,
        'total_sticks': total_sticks,
        'total_revenue': total_revenue,
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'paid_revenue': paid_revenue,
        'unpaid_revenue': unpaid_revenue,
        'orders': order_details,
        'admin_email': admin_email
    }

    return render_template("daily_summary.html", summary=summary_data)

@app.route('/admin/daily-summary/send', methods=['POST'])
@admin_required
def send_daily_summary_email():
    """Simulates/sends the daily summary email to the configured admin email."""
    date_str = request.form.get('date', str(datetime.date.today()))
    try:
        target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        target_date = datetime.date.today()

    orders_for_day = Order.query.filter_by(date=target_date).all()
    admin_email = SiteSetting.get_setting('admin_notification_email', 'admin@breadshop.com')

    total_revenue = sum(
        sum(data.prices.get(item, 0.0) * qty for item, qty in json.loads(o.order).items())
        for o in orders_for_day if o.order
    )

    log_msg = f"[DAILY SUMMARY EMAIL TO {admin_email}] Date: {target_date} | Orders: {len(orders_for_day)} | Revenue: €{total_revenue:.2f}"
    order_logger.info(log_msg)
    flash(f"Daily summary email successfully sent to {admin_email} for date {target_date}.", "success")
    return redirect(url_for('daily_summary', date=str(target_date)))

# ── Staff & Timetable Management (todo #12) ─────────────────────────────
@app.route('/admin/staff', methods=['GET', 'POST'])
@admin_required
def manage_staff():
    """Admin CRUD for staff members."""
    form = StaffForm()
    edit_id = request.args.get('edit', type=int)
    delete_id = request.form.get('delete_id', type=int)
    toggle_id = request.form.get('toggle_id', type=int)
    action = request.form.get('action', '')
    message = None
    error = None

    if delete_id:
        staff_member = db.session.get(Staff, delete_id)
        if staff_member:
            db.session.delete(staff_member)
            db.session.commit()
            message = "Staff member deleted."
        else:
            error = "Staff member not found."
    elif toggle_id:
        staff_member = db.session.get(Staff, toggle_id)
        if staff_member:
            staff_member.active = not staff_member.active
            db.session.commit()
            message = f"Staff member '{staff_member.name}' status toggled to {'Active' if staff_member.active else 'Inactive'}."
    elif form.validate_on_submit():
        staff_id = form.id.data and int(form.id.data)
        if staff_id:
            staff_member = db.session.get(Staff, staff_id)
            if staff_member:
                staff_member.name = form.name.data.strip()
                staff_member.role = form.role.data.strip()
                staff_member.email = form.email.data.strip() if form.email.data else None
                staff_member.phone = form.phone.data.strip() if form.phone.data else None
                staff_member.active = form.active.data
                db.session.commit()
                message = "Staff member updated."
                form = StaffForm()
                edit_id = None
        else:
            new_staff = Staff(
                name=form.name.data.strip(),
                role=form.role.data.strip(),
                email=form.email.data.strip() if form.email.data else None,
                phone=form.phone.data.strip() if form.phone.data else None,
                active=form.active.data
            )
            db.session.add(new_staff)
            db.session.commit()
            message = "Staff member added."
            form = StaffForm()
    elif edit_id and request.method == 'GET':
        staff_member = db.session.get(Staff, edit_id)
        if staff_member:
            form.id.data = staff_member.id
            form.name.data = staff_member.name
            form.role.data = staff_member.role
            form.email.data = staff_member.email
            form.phone.data = staff_member.phone
            form.active.data = staff_member.active

    all_staff = Staff.query.order_by(Staff.name).all()
    return render_template("manage_staff.html", form=form, staff=all_staff, edit_id=edit_id, message=message, error=error)

@app.route('/admin/timetable', methods=['GET', 'POST'])
@admin_required
def manage_timetable():
    """Admin timetable management with weekly calendar view and shift scheduling."""
    form = TimetableForm()
    active_staff = Staff.query.filter_by(active=True).order_by(Staff.name).all()
    form.staff_id.choices = [(s.id, f"{s.name} ({s.role})") for s in active_staff]
    delete_id = request.form.get('delete_id', type=int)
    message = None
    error = None

    if delete_id:
        shift = db.session.get(StaffTimetable, delete_id)
        if shift:
            db.session.delete(shift)
            db.session.commit()
            message = "Shift deleted."
        else:
            error = "Shift not found."
    elif form.validate_on_submit():
        shift = StaffTimetable(
            staff_id=form.staff_id.data,
            day_of_week=int(form.day_of_week.data),
            shift_date=form.shift_date.data if form.shift_date.data else None,
            start_time=form.start_time.data.strip(),
            end_time=form.end_time.data.strip(),
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(shift)
        db.session.commit()
        message = "Shift added to timetable."
        form = TimetableForm()
        form.staff_id.choices = [(s.id, f"{s.name} ({s.role})") for s in active_staff]

    shifts = StaffTimetable.query.all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_shifts = {i: [] for i in range(7)}
    for s in shifts:
        weekly_shifts[s.day_of_week].append(s)

    return render_template("manage_timetable.html", form=form, staff=active_staff, weekly_shifts=weekly_shifts, days=days, message=message, error=error)

# ── Delivery Routes & Driver Option (todo #13) ──────────────────────────
@app.route('/admin/delivery-routes', methods=['GET', 'POST'])
@admin_required
def delivery_routes():
    """Calculates optimized delivery routes starting from a bakery to destinations using TSP haversine."""
    driver_form = DeliveryPersonForm()
    bakeries = Bakery.query.order_by(Bakery.name).all()
    drivers = DeliveryPerson.query.order_by(DeliveryPerson.name).all()
    selected_bakery_id = request.args.get('bakery_id', type=int) or (bakeries[0].id if bakeries else None)
    date_str = request.args.get('date', str(datetime.date.today()))
    message = None
    error = None

    # Handle driver creation
    if request.method == 'POST' and request.form.get('action') == 'add_driver':
        if driver_form.validate_on_submit():
            driver = DeliveryPerson(
                name=driver_form.name.data.strip(),
                phone=driver_form.phone.data.strip(),
                vehicle_type=driver_form.vehicle_type.data.strip() if driver_form.vehicle_type.data else "Van",
                active=driver_form.active.data
            )
            db.session.add(driver)
            db.session.commit()
            flash("Delivery driver added.", "success")
            return redirect(url_for('delivery_routes', bakery_id=selected_bakery_id, date=date_str))

    try:
        target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        target_date = datetime.date.today()

    selected_bakery = db.session.get(Bakery, selected_bakery_id) if selected_bakery_id else None
    orders_for_day = Order.query.filter_by(date=target_date).all()

    # Route calculation using TSP nearest-neighbor algorithm
    route_stops = []
    total_km = 0.0

    if selected_bakery and orders_for_day:
        stops_to_visit = []
        for ord_obj in orders_for_day:
            lat = ord_obj.delivery_latitude
            lng = ord_obj.delivery_longitude
            # Fallback coordinates if only address available
            if lat is None or lng is None:
                lat = selected_bakery.latitude + 0.01 * ((ord_obj.id % 5) - 2)
                lng = selected_bakery.longitude + 0.01 * ((ord_obj.id % 7) - 3)

            items_dict = json.loads(ord_obj.order) if ord_obj.order else {}
            stops_to_visit.append({
                'order_id': ord_obj.id,
                'client': ord_obj.client,
                'address': ord_obj.delivery_address or "Profile address",
                'notes': ord_obj.delivery_notes,
                'items': items_dict,
                'lat': lat,
                'lng': lng
            })

        curr_lat = selected_bakery.latitude
        curr_lng = selected_bakery.longitude
        step = 1

        while stops_to_visit:
            # Find nearest stop
            nearest_idx = min(range(len(stops_to_visit)), key=lambda i: calculate_distance_km(curr_lat, curr_lng, stops_to_visit[i]['lat'], stops_to_visit[i]['lng']))
            nearest = stops_to_visit.pop(nearest_idx)
            leg_km = calculate_distance_km(curr_lat, curr_lng, nearest['lat'], nearest['lng'])
            total_km += leg_km
            nearest['leg_km'] = leg_km
            nearest['cumulative_km'] = total_km
            nearest['step'] = step
            step += 1
            route_stops.append(nearest)
            curr_lat = nearest['lat']
            curr_lng = nearest['lng']

        # Return leg to bakery
        return_km = calculate_distance_km(curr_lat, curr_lng, selected_bakery.latitude, selected_bakery.longitude)
        total_km += return_km

    return render_template(
        "delivery_routes.html",
        bakeries=bakeries,
        drivers=drivers,
        selected_bakery=selected_bakery,
        target_date=target_date,
        route_stops=route_stops,
        total_km=total_km,
        orders_count=len(orders_for_day),
        driver_form=driver_form,
        message=message,
        error=error
    )

# ── Legacy User Ordering (todo #14) ─────────────────────────────────────
@app.route('/admin/legacy-order', methods=['GET', 'POST'])
@admin_required
def legacy_order():
    """Admin form to place orders on behalf of legacy users."""
    legacy_users = User.query.filter_by(legacy=True).order_by(User.username).all()
    form = LegacyOrderForm()
    form.user_id.choices = [(u.id, f"{u.username} ({u.email}) - {u.address or 'No address'}") for u in legacy_users]
    message = None
    error = None

    try:
        products = Product.query.order_by(Product.name).all()
    except Exception:
        products = []

    if form.validate_on_submit():
        user = db.session.get(User, form.user_id.data)
        if not user:
            error = "Selected legacy user not found."
        else:
            order = {}
            for p in products:
                raw_qty = request.form.get(p.name, "0")
                try:
                    qty = int(raw_qty)
                    if qty > 0:
                        order[p.name] = qty
                except ValueError:
                    pass

            if not order:
                error = "Please specify at least one product to order."
            else:
                num_loafs = sum(list(order.values())[:len(order.values())-1]) + sum(list(order.values())[len(order.values())-1:])/2
                new_order = Order(
                    user_id=user.id,
                    order=json.dumps(order),
                    date=form.date.data,
                    payed=False,
                    delivered=False,
                    time_day=form.day_time.data,
                    client=user.username,
                    num_breads=num_loafs,
                    delivery_option='profile',
                    delivery_address=user.address,
                    delivery_notes=form.delivery_notes.data.strip() if form.delivery_notes.data else user.delivery_notes
                )
                db.session.add(new_order)
                db.session.flush()
                deduct_inventory_for_order(order, new_order.id)
                db.session.commit()
                message = f"Order #{new_order.id} placed successfully for legacy user {user.username}."
                form = LegacyOrderForm()
                form.user_id.choices = [(u.id, f"{u.username} ({u.email}) - {u.address or 'No address'}") for u in legacy_users]

    return render_template("legacy_order.html", form=form, legacy_users=legacy_users, products=products, message=message, error=error)

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
