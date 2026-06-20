import sqlite3
import json
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        # ===== PRODUCTS =====
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                country TEXT NOT NULL,
                age TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                specs TEXT,
                badge TEXT,
                status TEXT DEFAULT 'available',
                login TEXT,
                password TEXT,
                cookies TEXT,
                two_fa TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ===== ORDERS =====
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                items TEXT NOT NULL,
                total REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                plisio_invoice_id TEXT,
                plisio_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_at TIMESTAMP
            )
        """)

        # ===== USERS =====
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'ru',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ===== BALANCES =====
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # ===== TRANSACTIONS =====
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                description TEXT,
                plisio_invoice_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        self.conn.commit()
        self.init_demo_products()

    def init_demo_products(self):
        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] > 0:
            return

        demo_products = [
            {
                'title': 'Farm-akkaunt Facebook USA',
                'category': 'farm',
                'country': 'usa',
                'age': '3-6',
                'price': 25,
                'description': 'Kachestvenny farm-akkaunt Facebook, zaregistrirovanny v SSHA.',
                'specs': json.dumps({
                    'Strana': 'SSHA',
                    'Vozrast': '3-6 mesyatsev',
                    'Tip': 'Farm-akkaunt',
                    'Verifikatsiya': 'Po email + telefon',
                    'Cookies': 'Vklyucheny',
                    '2FA': 'Otklyuchen'
                }),
                'badge': 'Populyarny',
                'login': 'fb_user_usa_001@gmail.com',
                'password': 'Pass2024!USA',
                'cookies': 'cookies_usa_001.json',
                'two_fa': None
            },
            {
                'title': 'Business Manager UK',
                'category': 'bm',
                'country': 'uk',
                'age': '6+',
                'price': 45,
                'description': 'Gotovy Business Manager s privyazannym reklamnym akkauntom.',
                'specs': json.dumps({
                    'Strana': 'Velikobritaniya',
                    'Vozrast': '6+ mesyatsev',
                    'Tip': 'Business Manager',
                    'Limit': '$250/den',
                    'Verifikatsiya': 'Polnaya',
                    'Cookies': 'Vklyucheny'
                }),
                'badge': 'BM',
                'login': 'bm_user_uk_001@gmail.com',
                'password': 'BMpass2024!UK',
                'cookies': 'cookies_bm_uk_001.json',
                'two_fa': '123456'
            },
            {
                'title': 'Akkaunt s zapuskom EU',
                'category': 'launch',
                'country': 'eu',
                'age': '1-3',
                'price': 35,
                'description': 'Akkaunt s istoriey zapuska reklamy.',
                'specs': json.dumps({
                    'Strana': 'Evropa',
                    'Vozrast': '1-3 mesyatsa',
                    'Tip': 'S zapuskom',
                    'Istoriya': 'Est zapuski',
                    'Verifikatsiya': 'Po email',
                    'Cookies': 'Vklyucheny'
                }),
                'badge': 'Zapusk',
                'login': 'launch_eu_001@gmail.com',
                'password': 'Launch2024!EU',
                'cookies': 'cookies_launch_eu_001.json',
                'two_fa': None
            },
            {
                'title': 'Farm-akkaunt Facebook UK',
                'category': 'farm',
                'country': 'uk',
                'age': '6+',
                'price': 30,
                'description': 'Premium farm-akkaunt iz Velikobritanii.',
                'specs': json.dumps({
                    'Strana': 'Velikobritaniya',
                    'Vozrast': '6+ mesyatsev',
                    'Tip': 'Farm-akkaunt',
                    'Verifikatsiya': 'Polnaya',
                    'Cookies': 'Vklyucheny',
                    '2FA': 'Vklyuchen'
                }),
                'badge': 'VIP',
                'login': 'farm_vip_uk_001@gmail.com',
                'password': 'VIPfarm2024!UK',
                'cookies': 'cookies_vip_uk_001.json',
                'two_fa': '654321'
            },
            {
                'title': 'Business Manager USA',
                'category': 'bm',
                'country': 'usa',
                'age': '3-6',
                'price': 55,
                'description': 'Amerikansky Business Manager s povyshennym limitom.',
                'specs': json.dumps({
                    'Strana': 'SSHA',
                    'Vozrast': '3-6 mesyatsev',
                    'Tip': 'Business Manager',
                    'Limit': '$500/den',
                    'Verifikatsiya': 'Polnaya + BM',
                    'Cookies': 'Vklyucheny'
                }),
                'badge': 'BM',
                'login': 'bm_usa_pro_001@gmail.com',
                'password': 'BMpro2024!USA',
                'cookies': 'cookies_bm_usa_001.json',
                'two_fa': '789012'
            },
            {
                'title': 'Akkaunt s zapuskom USA',
                'category': 'launch',
                'country': 'usa',
                'age': '3-6',
                'price': 40,
                'description': 'Amerikansky akkaunt s uspeshnoy istoriey zapuska.',
                'specs': json.dumps({
                    'Strana': 'SSHA',
                    'Vozrast': '3-6 mesyatsev',
                    'Tip': 'S zapuskom',
                    'Istoriya': '5+ kampaniy',
                    'Verifikatsiya': 'Polnaya',
                    'Cookies': 'Vklyucheny'
                }),
                'badge': 'Zapusk',
                'login': 'launch_usa_001@gmail.com',
                'password': 'LaunchUSA2024!',
                'cookies': 'cookies_launch_usa_001.json',
                'two_fa': '345678'
            },
            {
                'title': 'Farm-akkaunt Facebook EU',
                'category': 'farm',
                'country': 'eu',
                'age': '1-3',
                'price': 20,
                'description': 'Evropeysky farm-akkaunt nachalnogo urovnya.',
                'specs': json.dumps({
                    'Strana': 'Evropa',
                    'Vozrast': '1-3 mesyatsa',
                    'Tip': 'Farm-akkaunt',
                    'Verifikatsiya': 'Po email',
                    'Cookies': 'Vklyucheny',
                    '2FA': 'Otklyuchen'
                }),
                'badge': 'Novyy',
                'login': 'farm_eu_new_001@gmail.com',
                'password': 'NewFarm2024!EU',
                'cookies': 'cookies_farm_eu_001.json',
                'two_fa': None
            },
            {
                'title': 'Business Manager EU',
                'category': 'bm',
                'country': 'eu',
                'age': '6+',
                'price': 50,
                'description': 'Evropeysky Business Manager s otlichnoy reputatsiey.',
                'specs': json.dumps({
                    'Strana': 'Evropa',
                    'Vozrast': '6+ mesyatsev',
                    'Tip': 'Business Manager',
                    'Limit': '$250/den',
                    'Verifikatsiya': 'Polnaya',
                    'Cookies': 'Vklyucheny'
                }),
                'badge': 'BM',
                'login': 'bm_eu_001@gmail.com',
                'password': 'BMeu2024!Pro',
                'cookies': 'cookies_bm_eu_001.json',
                'two_fa': '901234'
            }
        ]

        for product in demo_products:
            self.cursor.execute("""
                INSERT INTO products (title, category, country, age, price, description, specs, badge, login, password, cookies, two_fa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product['title'], product['category'], product['country'], product['age'],
                product['price'], product['description'], product['specs'], product['badge'],
                product['login'], product['password'], product['cookies'], product['two_fa']
            ))

        self.conn.commit()

    # ===== PRODUCTS =====
    def get_products(self, category=None, country=None, age=None):
        query = "SELECT * FROM products WHERE status = 'available'"
        params = []

        if category and category != 'all':
            query += " AND category = ?"
            params.append(category)
        if country and country != 'all':
            query += " AND country = ?"
            params.append(country)
        if age and age != 'all':
            query += " AND age = ?"
            params.append(age)

        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_products(self):
        self.cursor.execute("SELECT * FROM products ORDER BY id DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_product(self, product_id):
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def add_product(self, title, category, country, age, price, description, specs, badge, login, password, cookies, two_fa=None):
        self.cursor.execute("""
            INSERT INTO products (title, category, country, age, price, description, specs, badge, login, password, cookies, two_fa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, category, country, age, price, description, json.dumps(specs), badge, login, password, cookies, two_fa))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_product(self, product_id, **kwargs):
        allowed = ['title', 'category', 'country', 'age', 'price', 'description', 'badge', 'login', 'password', 'cookies', 'two_fa', 'status']
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False

        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [product_id]

        self.cursor.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
        return True

    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()

    def mark_product_sold(self, product_id):
        self.cursor.execute("UPDATE products SET status = 'sold' WHERE id = ?", (product_id,))
        self.conn.commit()

    # ===== ORDERS =====
    def create_order(self, order_id, user_id, username, first_name, items, total, plisio_invoice_id=None):
        self.cursor.execute("""
            INSERT INTO orders (order_id, user_id, username, first_name, items, total, plisio_invoice_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (order_id, user_id, username, first_name, json.dumps(items), total, plisio_invoice_id))
        self.conn.commit()
        return order_id

    def get_order(self, order_id):
        self.cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = self.cursor.fetchone()
        if row:
            order = dict(row)
            order['items'] = json.loads(order['items'])
            return order
        return None

    def get_all_orders(self):
        self.cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
        orders = []
        for row in self.cursor.fetchall():
            order = dict(row)
            order['items'] = json.loads(order['items'])
            orders.append(order)
        return orders

    def update_order_status(self, order_id, status, plisio_status=None):
        if plisio_status:
            self.cursor.execute(
                "UPDATE orders SET status = ?, plisio_status = ? WHERE order_id = ?",
                (status, plisio_status, order_id)
            )
        else:
            self.cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        self.conn.commit()

    def get_user_orders(self, user_id):
        self.cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        orders = []
        for row in self.cursor.fetchall():
            order = dict(row)
            order['items'] = json.loads(order['items'])
            orders.append(order)
        return orders

    # ===== USERS =====
    def add_user(self, user_id, username, first_name, last_name):
        self.cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, username, first_name, last_name))
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ===== BALANCE =====
    def get_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        self.cursor.execute("INSERT INTO balances (user_id, balance) VALUES (?, 0.0)", (user_id,))
        self.conn.commit()
        return 0.0

    def add_balance(self, user_id, amount):
        self.cursor.execute("""
            INSERT INTO balances (user_id, balance) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP
        """, (user_id, amount, amount))
        self.conn.commit()

    def deduct_balance(self, user_id, amount):
        current = self.get_balance(user_id)
        if current < amount:
            return False
        self.cursor.execute("""
            UPDATE balances SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?
        """, (amount, user_id))
        self.conn.commit()
        return True

    # ===== TRANSACTIONS =====
    def create_transaction(self, user_id, type, amount, description=None, plisio_invoice_id=None):
        self.cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, description, plisio_invoice_id)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, type, amount, description, plisio_invoice_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_user_transactions(self, user_id):
        self.cursor.execute("""
            SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC
        """, (user_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def update_transaction_status(self, transaction_id, status):
        self.cursor.execute("""
            UPDATE transactions SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (status, transaction_id))
        self.conn.commit()

    def get_transaction_by_plisio_id(self, plisio_invoice_id):
        self.cursor.execute("SELECT * FROM transactions WHERE plisio_invoice_id = ?", (plisio_invoice_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ===== STATS =====
    def get_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM products")
        total_products = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM products WHERE status = 'available'")
        available_products = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'paid'")
        paid_orders = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(SUM(total), 0) FROM orders WHERE status = 'paid'")
        total_revenue = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM users")
        total_users = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COALESCE(SUM(balance), 0) FROM balances")
        total_balance = self.cursor.fetchone()[0]

        return {
            'total_products': total_products,
            'available_products': available_products,
            'sold_products': total_products - available_products,
            'total_orders': total_orders,
            'paid_orders': paid_orders,
            'pending_orders': total_orders - paid_orders,
            'total_revenue': total_revenue,
            'total_users': total_users,
            'total_balance': total_balance
        }

db = Database()