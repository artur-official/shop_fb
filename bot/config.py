import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# === BOT SETTINGS ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
PLISIO_WEBHOOK_SECRET = os.getenv("PLISIO_WEBHOOK_SECRET", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()] if ADMIN_IDS_STR else []

# === SERVER SETTINGS ===
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# === DATABASE ===
DATABASE_PATH = os.getenv("DATABASE_PATH", "C:/Users/Administrator/Desktop/fb-shop/data/db/shop.db")

# === PLISIO ===
PLISIO_API_KEY = os.getenv("PLISIO_API_KEY", "")
PLISIO_WEBHOOK_URL = os.getenv("PLISIO_WEBHOOK_URL", "")
PLISIO_SECRET = os.getenv("PLISIO_SECRET", "")

# === ENCRYPTION KEY ===
def get_encryption_key():
    """Получает ключ шифрования из Windows Credential Manager или .env"""
    
    try:
        import keyring
        key = keyring.get_password("FBShop", "encryption_key")
        if key and len(key) == 32:
            return key
    except Exception:
        pass
    
    key = os.getenv("ENCRYPTION_KEY", "")
    if len(key) == 32:
        return key
    
    raise ValueError(
        "Ключ шифрования не найден!\n"
        "Варианты решения:\n"
        "1. Установите keyring: pip install keyring\n"
        "2. Сохраните ключ: python -c \"import keyring; keyring.set_password('FBShop', 'encryption_key', 'ВАШ_КЛЮЧ')\"\n"
        "3. Или добавьте ENCRYPTION_KEY=ВАШ_КЛЮЧ_32_СИМВОЛА в .env (только для теста!)"
    )

ENCRYPTION_KEY = get_encryption_key()

# === CURRENCY ===
DEFAULT_CURRENCY = "USDT"
DEFAULT_NETWORK = "TRC20"