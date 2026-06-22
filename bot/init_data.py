import hmac
import hashlib
import json
import time
from typing import Optional, Dict, Any
from urllib.parse import parse_qsl

from config import BOT_TOKEN


def verify_init_data(init_data: str) -> Optional[Dict[str, Any]]:
    """
    Проверяет подпись Telegram WebApp initData.

    Args:
        init_data: Строка initData из Telegram WebApp

    Returns:
        dict с данными пользователя (id, username, first_name, etc.)
        None если подпись невалидна или данные устарели
    """
    if not init_data:
        return None

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не настроен в config.py")

    try:
        # Парсим initData в словарь
        data = dict(parse_qsl(init_data, keep_blank_values=True))

        # Извлекаем hash для проверки
        received_hash = data.pop('hash', '')
        if not received_hash:
            return None

        # Создаём data_check_string (отсортированные key=value через \n)
        data_check_string = '\n'.join(
            f"{k}={v}" for k, v in sorted(data.items())
        )

        # Создаём секретный ключ: HMAC-SHA256("WebAppData", BOT_TOKEN)
        secret_key = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Считаем hash: HMAC-SHA256(secret_key, data_check_string)
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Безопасное сравнение (защита от timing-атак)
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        # Проверяем auth_date (не старше 24 часов)
        auth_date = int(data.get('auth_date', 0))
        if time.time() - auth_date > 86400:
            return None

        # Парсим данные пользователя
        user_json = data.get('user', '{}')
        user = json.loads(user_json)

        return user

    except (ValueError, json.JSONDecodeError, KeyError):
        return None
    except Exception:
        return None


def get_user_id_from_init_data(init_data: str) -> Optional[int]:
    """
    Быстрое получение user_id из initData без полной проверки.
    Использовать только для логирования, не для авторизации!
    """
    try:
        data = dict(parse_qsl(init_data, keep_blank_values=True))
        user = json.loads(data.get('user', '{}'))
        return user.get('id')
    except Exception:
        return None
