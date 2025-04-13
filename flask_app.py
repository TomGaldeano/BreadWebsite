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
from sqlalchemy import ForeignKey, Column, Integer, String, and_, text, desc
import json
from extra import *
from config import Data, SecretData
import datetime
from flask_wtf.csrf import CSRFProtect

MAX_BREADS = 20
data = Data()
secret_data = SecretData()

app = Flask(__name__)
# Flask-SQLAlchemy settings
# Avoids SQLAlchemy warning

def create_app():
    """
    Creates framework for it website to run (blackbox)
    """
    global app
    global db
    global login_manager
    username="breadtombakery"
    host_adress="breadtombakery.mysql.eu.pythonanywhere-services.com"
    name_database = "breadtombakery$breadshop"
    password_database = "Flx6)]4frW"
    app = Flask(__name__)
    Bootstrap(app)
    app.config['SECRET_KEY'] = "gdfgsksdflsdfjksjfkdsjfksjkfjdls"
    login_manager = LoginManager()
    login_manager.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqldb://{username}:{password_database}@{host_adress}/{name_database}"  # File-based SQL database
    db = SQLAlchemy(app)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    csrf = CSRFProtect(app)
    return app

create_app()

def find_num_breads(date,time):
        """

        """
        stmt = text("""SELECT SUM(num_breads) FROM orders WHERE time_day = '"""+time+"""' AND date = '"""+str(date)+"""'""")
        b = db.session.execute(stmt)
        return b.first()[0]

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    group = db.Column(db.String(255), nullable=False)
    orders = relationship("Order", back_populates="customer")
    date = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean(), nullable=False)
    legacy = db.Column(db.Boolean(), nullable=False)



class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    order = db.Column(db.String(5000), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    payed = db.Column(db.Boolean(), nullable=False)
    delivered = db.Column(db.Boolean(), nullable=False)
    time_day = db.Column(db.String(255), nullable=False)
    customer = relationship("User", back_populates="orders")
    client = db.Column(db.String(255), nullable=False)
    num_breads = db.Column(db.Integer)

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

def index(lang):
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
        for bread in data.prices.keys():
            if verifier.verify_int(eval(f'order_form.{bread}.data'), 0, 6):
                order[bread] = eval(f'order_form.{bread}.data')
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
                if lang == "es":
                    return redirect(url_for("pedidos"))
                elif lang == "en":
                    return redirect(url_for("orders"))
    if lang == "es":
        return render_template("indexEs.html",
                           order_form=order_form, errors = errors)
    elif lang == "en":
        return render_template("indexEng.html",
                           order_form=order_form, errors = errors)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('indexEs'))

@app.route('/Eng', methods=['POST', 'GET'])
def indexEng():
    return index("en")

@app.route('/Es', methods=['POST', 'GET'])
def indexEs():
    return index("es")

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
                return redirect(url_for("indexEng"))
    return render_template("register.html", form=form, errors=errors)

@app.route('/registro', methods=['POST', 'GET'])
def registro():
    """
    Backend of spanish registering a new user after checking the email and user do not exist already in database.
    If no issues happen logs in new user, adds them to database and redirects to the mainpage
    """
    form = RegisterForm()
    form.validate_on_submit()
    errors = [None, None]
    if form.validate_on_submit():
        valid = True
        if User.query.filter_by(username=form.username.data).first():
            errors[0] = 'este usario ya ha sido elegido'
            valid = False
        if User.query.filter_by(username=form.email.data).first():
            errors[1] = "este correo ya ha sido elegido"
            valid = False
        if valid:
            verifier = ReVerify(loggin_logger)
            if verifier.verify_string(form.username.data) and verifier.verify_string(
                    form.password.data) and verifier.verify_string(form.group.data) and verifier.verify_string(
                form.email.data):
                new_user = User(username=form.username.data, password=generate_password_hash(str(form.password.data),
                method="pbkdf2:sha256",salt_length=14), group=form.group.data, date = (datetime.date.today()), email=form.email.data, verified = 0, legacy = 0)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                loggin_logger.info(f"user {form.username.data} from group {form.group.data} registered correctly")
                return redirect(url_for("indexEs"))
    return render_template("registro.html", form=form, errors=errors)

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
                    return redirect(url_for("indexEng"))
            else:
                error_no_user = "No such user exists"
    return render_template("login.html", form=form, error_no_user = error_no_user)

@app.route('/acceso', methods=['POST', 'GET'])
def acceso():
    """
    Page that allows user to log in to the account and get redirectod to main page in spanish
    """
    form = LoginForm()
    verifier = ReVerify(loggin_logger)
    error_no_user = None
    if form.validate_on_submit():
        if verifier.verify_string(form.password.data) and verifier.verify_string(form.username.data):
            user_db = User.query.filter_by(username=form.username.data).first()
            if user_db:  # check if user in database
                if werkzeug.security.check_password_hash(user_db.password,
                                                         form.password.data):  # check if correct password
                    login_user(user_db)
                    loggin_logger.info(f"user {form.username.data} logged in correctly")
                    return redirect(url_for("indexEs"))
            else:
                error_no_user = "No existe ese usuario"
    return render_template("loginES.html", form=form, error_no_user= error_no_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('indexEng'))

@app.route('/desconectar')
@login_required
def desconectar():
    logout_user()
    return redirect(url_for('indexEs'))

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
    return redirect(url_for('indexEng'))

@app.route('/eliminar')
@user_required
def eliminar():
    """
    Deletes the user from database when directed from user page in spanish
    """
    user_id = current_user.id
    logout_user()
    stmt = text('''DELETE FROM users WHERE id IN ('''+str(user_id)+");")
    db.session.execute(stmt)
    stmt = text('''DELETE FROM orders WHERE user_id IN ('''+str(user_id)+");")
    db.session.execute(stmt)
    db.session.commit()
    return redirect(url_for('indexEs'))

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

@app.route('/pedidos', methods=['POST', 'GET'])
@user_required
def pedidos():
    """
    Page thath shows all orders the user has  done in spaninsh
    """
    user_id = current_user.id
    undelivered_orders = OrderViewer(db.session.query(Order).filter(
        and_(Order.user_id == user_id, Order.date > (datetime.date.today() - datetime.timedelta(days=1)))).all(), "es")
    delivered_orders = OrderViewer(db.session.query(Order).filter(
        and_(Order.user_id == user_id, Order.date < (datetime.date.today() - datetime.timedelta(days=1)))).order_by(desc(Order.id)).all(), "es")
    form = generate_basic_form(message="Delete",num_entries = 10)
    form =form()
    undelivered_orders.add_form(form)
    form.validate_on_submit()
    if form.validate_on_submit():
        for i in undelivered_orders:
            if undelivered_orders.form_data.data:
                db.session.delete(undelivered_orders.order_instance)
        db.session.commit()
        return redirect(url_for("pedidos"))
    return render_template("pedidos.html", form=form, delivered_orders=delivered_orders,
                           undelivered_orders=undelivered_orders)

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

@app.route('/usuario', methods=['POST', 'GET'])
@user_required
def usuario():
    """
    Presents user with a way to change the inforamationif the user has their password and username in spanish
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
                errors[0] = 'Usuario ya cogido'
                valid = False
        if User.query.filter_by(username=form.email.data).first():
            if user.email != form.email.data:
                errors[1] = "Correo ya escogido"
                valid = False
        if valid:
            if werkzeug.security.check_password_hash(current_user.password, form.old_password.data):
                user.username = form.username.data
                user.email = form.email.data
                user.group = form.group.data
                if form.new_password.data:
                    user.password = generate_password_hash(str(form.new_password.data), method="pbkdf2:sha256", salt_length=14)
                db.session.commit()
                return redirect(url_for("usuario"))
    return render_template("usuario.html", form=form, errors = errors, user_data=user_data)

@app.route('/info', methods=['POST', 'GET'])
def info():
    return(render_template("info.html"))

@app.route('/infoEng', methods=['POST', 'GET'])
def infoEng():
    return(render_template("info_Eng.html"))

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
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
