import sqlite3
import json
import os
import shutil
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH, ENCRYPTION_KEY
from encryption import EncryptionManager

log_dir = os.path.dirname(DATABASE_PATH).replace("/db", "/logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "db_operations.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Database:
    # Разрешённые поля для обновления карточки (защита от SQL-инъекции)
    ALLOWED_CARD_FIELDS = {
        "title", "category", "country", "age", 
        "price", "badge", "description", "status"
    }

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.encryption = EncryptionManager(ENCRYPTION_KEY)
        self._init_db()
        self._run_backup()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self._get_connection() as conn:
            # Product Cards (karochki tovarov)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS product_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    country TEXT,
                    age TEXT,
                    price REAL NOT NULL,
                    badge TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Accounts (konkretnye akki)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER NOT NULL,
                    account_id TEXT UNIQUE NOT NULL,
                    email TEXT,
                    password TEXT,
                    cookies TEXT,
                    two_fa TEXT,
                    status TEXT DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (card_id) REFERENCES product_cards(id)
                )
            """)

            # Orders
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    card_id INTEGER,
                    account_id INTEGER,
                    total REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    plisio_invoice_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Users
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Balances
            conn.execute("""
                CREATE TABLE IF NOT EXISTS balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    balance REAL DEFAULT 0.0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Transactions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Audit Logs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    user_id INTEGER,
                    details TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info("Database initialized")

    def _run_backup(self):
        backup_dir = self.db_path.replace("/db/", "/backups/")
        os.makedirs(os.path.dirname(backup_dir), exist_ok=True)

        backup_file = os.path.join(
            os.path.dirname(backup_dir),
            f"shop_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
        )

        latest_backup = None
        if os.path.exists(os.path.dirname(backup_dir)):
            backups = [f for f in os.listdir(os.path.dirname(backup_dir)) if f.startswith("shop_")]
            if backups:
                latest_backup = max(backups)

        need_backup = True
        if latest_backup:
            backup_time_str = latest_backup.replace("shop_", "").replace(".db", "")
            try:
                backup_time = datetime.strptime(backup_time_str, "%Y-%m-%d_%H-%M-%S")
                if datetime.now() - backup_time < timedelta(hours=24):
                    need_backup = False
            except ValueError:
                pass

        if need_backup and os.path.exists(self.db_path):
            shutil.copy2(self.db_path, backup_file)
            logger.info(f"Backup created: {backup_file}")

    def _log_action(self, action: str, user_id: Optional[int] = None, details: str = ""):
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO audit_logs (action, user_id, details) VALUES (?, ?, ?)",
                    (action, user_id, details)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Logging error: {e}")

    # ===== PRODUCT CARDS =====
    def create_card(self, title: str, category: str, country: str, age: str, 
                    price: float, badge: str = "", description: str = "") -> int:
        """Create new product card"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO product_cards (title, category, country, age, price, badge, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, category, country, age, price, badge, description))
            conn.commit()
            card_id = cursor.lastrowid

        self._log_action("CREATE_CARD", details=f"ID={card_id}, title={title}")
        logger.info(f"Card created: ID={card_id}")
        return card_id

    def get_card(self, card_id: int) -> Optional[Dict]:
        """Get card by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM product_cards WHERE id = ?", (card_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_all_cards(self, category: Optional[str] = None) -> List[Dict]:
        """Get all cards"""
        query = "SELECT * FROM product_cards WHERE status = 'active'"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY created_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def update_card(self, card_id: int, data: Dict[str, Any]) -> bool:
        """Update card. Only allowed fields can be modified."""
        # Фильтруем только разрешённые поля (защита от SQL-инъекции)
        safe_data = {}
        for key, value in data.items():
            if key in self.ALLOWED_CARD_FIELDS:
                safe_data[key] = value
            else:
                logger.warning(f"Ignored unsafe field: {key}")

        if not safe_data:
            logger.warning(f"No valid fields to update for card {card_id}")
            return False

        fields = []
        values = []
        for key, value in safe_data.items():
            fields.append(f"{key} = ?")
            values.append(value)

        values.append(card_id)
        query = f"UPDATE product_cards SET {', '.join(fields)} WHERE id = ?"

        with self._get_connection() as conn:
            conn.execute(query, values)
            conn.commit()

        self._log_action("UPDATE_CARD", details=f"ID={card_id}, fields={list(safe_data.keys())}")
        logger.info(f"Card updated: ID={card_id}, fields={list(safe_data.keys())}")
        return True

    def delete_card(self, card_id: int) -> bool:
        """Delete card (soft delete)"""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE product_cards SET status = 'deleted' WHERE id = ?", (card_id,)
            )
            conn.commit()

        self._log_action("DELETE_CARD", details=f"ID={card_id}")
        logger.info(f"Card deleted: ID={card_id}")
        return True

    # ===== ACCOUNTS =====
    def add_account(self, card_id: int, account_id: str, email: str, password: str, 
                    cookies: str = "", two_fa: str = "") -> tuple:
        """Add account. Returns (success: bool, message: str)"""
        # Check duplicate by account_id
        with self._get_connection() as conn:
            existing = conn.execute(
                "SELECT id FROM accounts WHERE account_id = ?", (account_id,)
            ).fetchone()
            if existing:
                return False, f"Duplicate account_id: {account_id}"

            # Check duplicate by email
            if email:
                existing_email = conn.execute(
                    "SELECT id FROM accounts WHERE email = ?", (email,)
                ).fetchone()
                if existing_email:
                    return False, f"Duplicate email: {email}"

            # Encrypt sensitive data
            encrypted_password = self.encryption.encrypt(password) if password else ""
            encrypted_cookies = self.encryption.encrypt(cookies) if cookies else ""
            encrypted_2fa = self.encryption.encrypt(two_fa) if two_fa else ""

            cursor = conn.execute("""
                INSERT INTO accounts (card_id, account_id, email, password, cookies, two_fa)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (card_id, account_id, email, encrypted_password, encrypted_cookies, encrypted_2fa))
            conn.commit()

            self._log_action("ADD_ACCOUNT", details=f"card_id={card_id}, account_id={account_id}")
            logger.info(f"Account added: card_id={card_id}, account_id={account_id}")
            return True, f"Account {account_id} added successfully"

    def add_accounts_batch(self, card_id: int, accounts_data: List[Dict]) -> Dict:
        """Add multiple accounts. Returns stats"""
        added = 0
        skipped = 0
        errors = []

        for acc in accounts_data:
            success, msg = self.add_account(
                card_id=card_id,
                account_id=acc.get("account_id", ""),
                email=acc.get("email", ""),
                password=acc.get("password", ""),
                cookies=acc.get("cookies", ""),
                two_fa=acc.get("two_fa", "")
            )
            if success:
                added += 1
            else:
                skipped += 1
                errors.append(msg)

        return {
            "added": added,
            "skipped": skipped,
            "errors": errors
        }

    def get_account(self, account_id: int) -> Optional[Dict]:
        """Get account by ID with decryption"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM accounts WHERE id = ?", (account_id,)
            ).fetchone()

            if row:
                account = dict(row)
                # Decrypt sensitive fields
                if account.get("password"):
                    try:
                        account["password"] = self.encryption.decrypt(account["password"])
                    except:
                        pass
                if account.get("cookies"):
                    try:
                        account["cookies"] = self.encryption.decrypt(account["cookies"])
                    except:
                        pass
                if account.get("two_fa"):
                    try:
                        account["two_fa"] = self.encryption.decrypt(account["two_fa"])
                    except:
                        pass
                return account
            return None

    def get_available_account(self, card_id: int) -> Optional[Dict]:
        """Get first available account for card (FIFO)"""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM accounts 
                WHERE card_id = ? AND status = 'available' 
                ORDER BY created_at ASC 
                LIMIT 1
            """, (card_id,)).fetchone()

            if row:
                return self.get_account(row["id"])
            return None

    def mark_account_sold(self, account_id: int) -> bool:
        """Mark account as sold"""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE accounts SET status = 'sold' WHERE id = ?", (account_id,)
            )
            conn.commit()
            logger.info(f"Account marked as sold: ID={account_id}")
            return True

    def get_card_accounts(self, card_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get all accounts for card"""
        query = "SELECT id, account_id, email, status, created_at FROM accounts WHERE card_id = ?"
        params = [card_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at ASC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_card_stats(self, card_id: int) -> Dict:
        """Get account stats for card"""
        with self._get_connection() as conn:
            total = conn.execute(
                "SELECT COUNT(*) as count FROM accounts WHERE card_id = ?", (card_id,)
            ).fetchone()["count"]

            available = conn.execute(
                "SELECT COUNT(*) as count FROM accounts WHERE card_id = ? AND status = 'available'",
                (card_id,)
            ).fetchone()["count"]

            sold = conn.execute(
                "SELECT COUNT(*) as count FROM accounts WHERE card_id = ? AND status = 'sold'",
                (card_id,)
            ).fetchone()["count"]

            return {"total": total, "available": available, "sold": sold}

    # ===== ORDERS =====
    def create_order(self, order_id: str, user_id: int, username: str, 
                     first_name: str, card_id: int, account_id: int, total: float) -> bool:
        """Create order"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO orders (order_id, user_id, username, first_name, card_id, account_id, total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (order_id, user_id, username, first_name, card_id, account_id, total))
            conn.commit()

            self._log_action("CREATE_ORDER", user_id, f"order_id={order_id}, card_id={card_id}")
            logger.info(f"Order created: {order_id}")
            return True

    def update_order_status(self, order_id: str, status: str, 
                            plisio_invoice_id: Optional[str] = None) -> bool:
        with self._get_connection() as conn:
            if plisio_invoice_id:
                conn.execute(
                    "UPDATE orders SET status = ?, plisio_invoice_id = ? WHERE order_id = ?",
                    (status, plisio_invoice_id, order_id)
                )
            else:
                conn.execute(
                    "UPDATE orders SET status = ? WHERE order_id = ?",
                    (status, order_id)
                )
            conn.commit()

            self._log_action("UPDATE_ORDER", details=f"order_id={order_id}, status={status}")
            logger.info(f"Order status updated: {order_id} -> {status}")
            return True

    def get_user_orders(self, user_id: int) -> List[Dict]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    def get_all_orders(self, status: Optional[str] = None) -> List[Dict]:
        query = "SELECT * FROM orders"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    # ===== USERS =====
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, last_name))
            conn.commit()

    def get_user(self, user_id: int) -> Optional[Dict]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    # ===== BALANCE =====
    def get_balance(self, user_id: int) -> float:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT balance FROM balances WHERE user_id = ?", (user_id,)
            ).fetchone()
            return row["balance"] if row else 0.0

    def add_balance(self, user_id: int, amount: float) -> bool:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO balances (user_id, balance) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET 
                    balance = balance + excluded.balance,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, amount))
            conn.commit()

            self._log_action("ADD_BALANCE", user_id, f"amount={amount}")
            logger.info(f"Balance added: user_id={user_id}, amount={amount}")
            return True

    def deduct_balance(self, user_id: int, amount: float) -> bool:
        current = self.get_balance(user_id)
        if current < amount:
            return False

        with self._get_connection() as conn:
            conn.execute(
                "UPDATE balances SET balance = balance - ? WHERE user_id = ?",
                (amount, user_id)
            )
            conn.commit()

            self._log_action("DEDUCT_BALANCE", user_id, f"amount={amount}")
            logger.info(f"Balance deducted: user_id={user_id}, amount={amount}")
            return True

    # ===== TRANSACTIONS =====
    def add_transaction(self, user_id: int, type_: str, amount: float, 
                        description: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO transactions (user_id, type, amount, description)
                VALUES (?, ?, ?, ?)
            """, (user_id, type_, amount, description))
            conn.commit()
            return cursor.lastrowid

    def get_user_transactions(self, user_id: int) -> List[Dict]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    # ===== STATS =====
    def get_stats(self) -> Dict:
        with self._get_connection() as conn:
            total_cards = conn.execute(
                "SELECT COUNT(*) as count FROM product_cards WHERE status = 'active'"
            ).fetchone()["count"]

            total_accounts = conn.execute(
                "SELECT COUNT(*) as count FROM accounts"
            ).fetchone()["count"]

            available_accounts = conn.execute(
                "SELECT COUNT(*) as count FROM accounts WHERE status = 'available'"
            ).fetchone()["count"]

            sold_accounts = conn.execute(
                "SELECT COUNT(*) as count FROM accounts WHERE status = 'sold'"
            ).fetchone()["count"]

            total_orders = conn.execute(
                "SELECT COUNT(*) as count FROM orders"
            ).fetchone()["count"]

            paid_orders = conn.execute(
                "SELECT COUNT(*) as count FROM orders WHERE status = 'paid'"
            ).fetchone()["count"]

            revenue = conn.execute(
                "SELECT COALESCE(SUM(total), 0) as sum FROM orders WHERE status = 'paid'"
            ).fetchone()["sum"]

            users = conn.execute(
                "SELECT COUNT(*) as count FROM users"
            ).fetchone()["count"]

            return {
                "total_cards": total_cards,
                "total_accounts": total_accounts,
                "available_accounts": available_accounts,
                "sold_accounts": sold_accounts,
                "total_orders": total_orders,
                "paid_orders": paid_orders,
                "total_revenue": revenue,
                "total_users": users
            }

    def get_audit_logs(self, limit: int = 100) -> List[Dict]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]

# Global instance
db = Database()