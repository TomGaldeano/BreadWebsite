import unittest
import json
import datetime
from flask_app import app, db, create_app, User, Order, Product, Ingredient, ProductIngredient, Bakery, InventoryLog, UserPreference, SiteSetting, Staff, StaffTimetable, DeliveryPerson, get_serializer, calculate_distance_km
from werkzeug.security import generate_password_hash


class BreadWebsiteFeaturesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test_secret_key_123'
        })
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Seed initial data
        self.superadmin = User(
            id=1,
            username='superadmin',
            password=generate_password_hash('password123', method="pbkdf2:sha256", salt_length=14),
            email='admin@breadshop.com',
            group='admins',
            date=str(datetime.date.today()),
            verified=True,
            legacy=False,
            is_admin=True
        )
        self.regular_user = User(
            id=2,
            username='johndoe',
            password=generate_password_hash('password123', method="pbkdf2:sha256", salt_length=14),
            email='john@example.com',
            group='customers',
            address='123 Main St, Madrid',
            delivery_notes='Leave on porch',
            date=str(datetime.date.today()),
            verified=True,
            legacy=False,
            is_admin=False
        )
        self.legacy_user = User(
            id=3,
            username='legacycustomer',
            password=generate_password_hash('password123', method="pbkdf2:sha256", salt_length=14),
            email='legacy@example.com',
            group='legacygroup',
            address='456 Old Town St',
            date=str(datetime.date.today()),
            verified=True,
            legacy=True,
            is_admin=False
        )
        self.unverified_user = User(
            id=4,
            username='unverifieduser',
            password=generate_password_hash('password123', method="pbkdf2:sha256", salt_length=14),
            email='unverified@example.com',
            group='customers',
            date=str(datetime.date.today()),
            verified=False,
            legacy=False,
            is_admin=False
        )

        db.session.add_all([self.superadmin, self.regular_user, self.legacy_user, self.unverified_user])

        # Ingredients & Products
        self.flour = Ingredient(id=1, name='flour', display_name='Wheat Flour', display_name_es='Harina de Trigo', cost=0.8, stock=50.0, unit='kg')
        self.water = Ingredient(id=2, name='water', display_name='Water', display_name_es='Agua', cost=0.01, stock=100.0, unit='l')
        self.yeast = Ingredient(id=3, name='yeast', display_name='Yeast', display_name_es='Levadura', cost=2.0, stock=5.0, unit='kg')
        db.session.add_all([self.flour, self.water, self.yeast])

        self.bread_product = Product(id=1, name='White_loaf', display_name='White Loaf', display_name_es='Hogaza Blanca', price=3.0, category='loaf')
        db.session.add(self.bread_product)
        db.session.commit()

        self.pi1 = ProductIngredient(product_id=self.bread_product.id, ingredient_id=self.flour.id, quantity=0.5)
        self.pi2 = ProductIngredient(product_id=self.bread_product.id, ingredient_id=self.yeast.id, quantity=0.02)
        db.session.add_all([self.pi1, self.pi2])

        # Bakery
        self.bakery = Bakery(id=1, name='Downtown Bakery', address='Plaza Mayor 1', latitude=40.4168, longitude=-3.7038, base_delivery_cost=2.0, cost_per_km=0.5)
        db.session.add(self.bakery)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, username, password='password123'):
        return self.client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)

    # ── Test 1: Superadmin & Admin Hierarchy (todo #20) ─────────────────
    def test_admin_promotion_and_permissions(self):
        # Superadmin can promote regular user
        self.login('superadmin')
        res = self.client.post('/admin/promote', data={'user_id': 2, 'action': 'grant'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        user = db.session.get(User, 2)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.has_admin_access())
        self.assertFalse(user.is_superadmin())

        # Promoted admin cannot access superadmin promotion route
        self.client.get('/logout', follow_redirects=True)
        self.login('johndoe')
        res_promote = self.client.get('/admin/promote')
        self.assertEqual(res_promote.status_code, 302) # redirect to home

        # But promoted admin can access regular admin routes
        res_baker = self.client.get('/baker')
        self.assertEqual(res_baker.status_code, 200)

    # ── Test 2: User Preferences & Admin Settings (todo #5) ─────────────
    def test_user_preferences_and_admin_settings(self):
        self.login('johndoe')
        res = self.client.post('/settings', data={
            'preferred_language': 'es',
            'dark_mode': True,
            'default_delivery_notes': 'Ring the bell twice'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        pref = UserPreference.query.filter_by(user_id=2).first()
        self.assertIsNotNone(pref)
        self.assertEqual(pref.preferred_language, 'es')
        self.assertTrue(pref.dark_mode)
        self.assertEqual(pref.default_delivery_notes, 'Ring the bell twice')

        # Admin settings
        self.client.get('/logout', follow_redirects=True)
        self.login('superadmin')
        res_adm = self.client.post('/admin/settings', data={
            'require_email_verification': True,
            'admin_notification_email': 'manager@breadshop.com'
        }, follow_redirects=True)
        self.assertEqual(res_adm.status_code, 200)
        self.assertEqual(SiteSetting.get_setting('require_email_verification'), 'true')
        self.assertEqual(SiteSetting.get_setting('admin_notification_email'), 'manager@breadshop.com')

    # ── Test 3: Inventory Stock & Order Deduction (todo #8, #9) ─────────
    def test_inventory_deduction_and_logs(self):
        initial_flour_stock = self.flour.stock # 50.0
        self.login('johndoe')

        # Use a valid upcoming delivery date (September Monday, not in Jul/Aug)
        test_date = datetime.date.today() + datetime.timedelta(days=1)
        if test_date.month in [7, 8]:
            test_date = datetime.date(test_date.year, 9, 7)
        while test_date.weekday() in [4, 5, 6]:
            test_date += datetime.timedelta(days=1)

        # Place order for 2 White_loaf (recipe: 0.5kg flour each -> 1.0kg total flour)
        res = self.client.post('/index', data={
            'White_loaf': 2,
            'date': test_date.strftime('%Y-%m-%d'),
            'day_time': 'Evening',
            'recurring': 0,
            'delivery_option': 'profile',
            'delivery_notes': 'Please drop at front door'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        updated_flour = db.session.get(Ingredient, self.flour.id)
        self.assertAlmostEqual(updated_flour.stock, initial_flour_stock - 1.0)

        # Check InventoryLog was created
        log = InventoryLog.query.filter_by(ingredient_id=self.flour.id).first()
        self.assertIsNotNone(log)
        self.assertAlmostEqual(log.change_amount, -1.0)

        # Manual Stock Adjustment
        self.client.get('/logout', follow_redirects=True)
        self.login('superadmin')
        res_adj = self.client.post('/admin/inventory/adjust', data={
            'ingredient_id': self.flour.id,
            'adjustment_type': 'add',
            'amount': 20.0,
            'reason': 'Weekly restock from mill'
        }, follow_redirects=True)
        self.assertEqual(res_adj.status_code, 200)

        db.session.refresh(updated_flour)
        self.assertAlmostEqual(updated_flour.stock, initial_flour_stock - 1.0 + 20.0)

    # ── Test 4: Delivery Options & Profile Delivery Notes (todos #2, #4) 
    def test_delivery_notes_and_options(self):
        self.login('johndoe')
        # Update delivery notes in profile
        res = self.client.post('/account', data={
            'username': 'johndoe',
            'old_password': 'password123',
            'email': 'john@example.com',
            'group': 'customers',
            'address': '123 Main St, Madrid',
            'delivery_notes': 'Gate code #9988'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        user = db.session.get(User, 2)
        self.assertEqual(user.delivery_notes, 'Gate code #9988')

        # Place order with custom address and GPS coordinates
        test_date = datetime.date.today() + datetime.timedelta(days=1)
        if test_date.month in [7, 8]:
            test_date = datetime.date(test_date.year, 9, 7)
        while test_date.weekday() in [4, 5, 6]:
            test_date += datetime.timedelta(days=1)

        res_ord = self.client.post('/index', data={
            'White_loaf': 1,
            'date': test_date.strftime('%Y-%m-%d'),
            'day_time': 'Evening',
            'recurring': 0,
            'delivery_option': 'custom',
            'delivery_address': 'Calle Gran Via 22, Madrid',
            'delivery_notes': 'Ring buzzer 3A',
            'delivery_latitude': '40.4200',
            'delivery_longitude': '-3.7050'
        }, follow_redirects=True)
        self.assertEqual(res_ord.status_code, 200)

        order = Order.query.filter_by(user_id=2).order_by(Order.id.desc()).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.delivery_option, 'custom')
        self.assertEqual(order.delivery_address, 'Calle Gran Via 22, Madrid')
        self.assertEqual(order.delivery_notes, 'Ring buzzer 3A')
        self.assertAlmostEqual(order.delivery_latitude, 40.4200)
        self.assertAlmostEqual(order.delivery_longitude, -3.7050)

    # ── Test 5: Email Verification (todo #10) ───────────────────────────
    def test_email_verification_flow(self):
        serializer = get_serializer()
        token = serializer.dumps(self.unverified_user.id, salt='email-verify')

        # Visit verification link
        res = self.client.get(f'/verify-email/{token}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"verified successfully", res.data)

        user = db.session.get(User, self.unverified_user.id)
        self.assertTrue(user.verified)

    # ── Test 6: Daily Summary Report & Email Trigger (todo #17) ─────────
    def test_daily_summary_report(self):
        # Create an order for today
        today = datetime.date.today()
        test_order = Order(
            user_id=self.regular_user.id,
            client=self.regular_user.username,
            order=json.dumps({'White_loaf': 2}),
            date=today,
            payed=True,
            delivered=False,
            time_day='Evening',
            num_breads=2
        )
        db.session.add(test_order)
        db.session.commit()

        self.login('superadmin')
        res = self.client.get(f'/admin/daily-summary?date={today.strftime("%Y-%m-%d")}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Total Orders", res.data)

        # Trigger send email
        res_send = self.client.post('/admin/daily-summary/send', data={'date': today.strftime("%Y-%m-%d")}, follow_redirects=True)
        self.assertEqual(res_send.status_code, 200)
        self.assertIn(b"Daily summary email successfully sent", res_send.data)

    # ── Test 7: Staff Database & Timetable Management (todo #12) ────────
    def test_staff_and_timetable_crud(self):
        self.login('superadmin')

        # Add Staff
        res_staff = self.client.post('/admin/staff', data={
            'name': 'Carlos Baker',
            'role': 'Master Baker',
            'email': 'carlos@breadshop.com',
            'phone': '+34 600 111 222',
            'active': True
        }, follow_redirects=True)
        self.assertEqual(res_staff.status_code, 200)

        staff = Staff.query.filter_by(name='Carlos Baker').first()
        self.assertIsNotNone(staff)
        self.assertEqual(staff.role, 'Master Baker')

        # Add Shift to Timetable
        res_shift = self.client.post('/admin/timetable', data={
            'staff_id': staff.id,
            'day_of_week': '0', # Monday
            'start_time': '05:00',
            'end_time': '13:00',
            'notes': 'Sourdough mixing station'
        }, follow_redirects=True)
        self.assertEqual(res_shift.status_code, 200)

        shift = StaffTimetable.query.filter_by(staff_id=staff.id).first()
        self.assertIsNotNone(shift)
        self.assertEqual(shift.start_time, '05:00')
        self.assertEqual(shift.notes, 'Sourdough mixing station')

    # ── Test 8: Delivery Person & Route Calculation (todo #13) ──────────
    def test_delivery_person_and_route_optimizer(self):
        self.login('superadmin')

        # Add driver
        res_drv = self.client.post('/admin/delivery-routes', data={
            'action': 'add_driver',
            'name': 'Pedro Driver',
            'phone': '+34 622 333 444',
            'vehicle_type': 'Electric Van',
            'active': True
        }, follow_redirects=True)
        self.assertEqual(res_drv.status_code, 200)

        driver = DeliveryPerson.query.filter_by(name='Pedro Driver').first()
        self.assertIsNotNone(driver)

        # Distance calculation check
        dist = calculate_distance_km(40.4168, -3.7038, 40.4200, -3.7050)
        self.assertGreater(dist, 0.0)

        # Access route calculation view
        today = datetime.date.today()
        res_route = self.client.get(f'/admin/delivery-routes?bakery_id={self.bakery.id}&date={today.strftime("%Y-%m-%d")}')
        self.assertEqual(res_route.status_code, 200)
        self.assertIn(b"Optimal Delivery Sequence", res_route.data)

    # ── Test 9: Legacy User Ordering by Admin (todo #14) ────────────────
    def test_legacy_user_order_creation(self):
        self.login('superadmin')

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        while tomorrow.weekday() in [2, 5, 6]:
            tomorrow += datetime.timedelta(days=1)

        res = self.client.post('/admin/legacy-order', data={
            'user_id': self.legacy_user.id,
            'date': tomorrow.strftime('%Y-%m-%d'),
            'day_time': 'Evening',
            'delivery_notes': 'Please hand directly to customer',
            'White_loaf': 3
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify order was created in DB for legacy user
        order = Order.query.filter_by(user_id=self.legacy_user.id).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.client, self.legacy_user.username)
        self.assertEqual(order.delivery_notes, 'Please hand directly to customer')
        order_dict = json.loads(order.order)
        self.assertEqual(order_dict.get('White_loaf'), 3)


if __name__ == '__main__':
    unittest.main()
