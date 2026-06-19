import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Plisio API
PLISIO_API_KEY = os.getenv("PLISIO_API_KEY", "")
PLISIO_WEBHOOK_URL = os.getenv("PLISIO_WEBHOOK_URL", "")

# Server Settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

# Database
DATABASE_PATH = "shop.db"

# Currency
CURRENCY = "USDT"
CURRENCY_NETWORK = "TRC20"

# Admins (Telegram IDs)
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()] if admin_ids_str else []