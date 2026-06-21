import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery, FSInputFile, MenuButtonWebApp
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, WEBAPP_URL, ADMIN_IDS
from database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ===== STATES FOR ADMIN =====
admin_states = {}  # user_id -> {state, data}

# ===== USER COMMANDS =====
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await set_user_menu_button(message.chat.id)
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)

    welcome_text = (
        f"<b>Привет, {user.first_name}!</b>\n\n"
        "Добро пожаловать в магазин аккаунтов Facebook!\n\n"
        "Качественные фарм-аккаунты, БМ и аккаунты с запуском\n"
        "Мгновенная выдача после оплаты\n"
        "Оплата криптой (USDT)\n\n"
        "Нажмите кнопку ниже, чтобы открыть магазин:"
    )

    buttons = [
        [InlineKeyboardButton(text="Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🛒 Мои покупки", callback_data="my_orders")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")]
    ]

    if user.id in ADMIN_IDS:
        buttons.append([InlineKeyboardButton(text="🔐 ADMIN PANEL", callback_data="admin_panel")])

    webapp_button = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(welcome_text, reply_markup=webapp_button)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "<b>Помощь</b>\n\n"
        "<b>Как купить аккаунт:</b>\n"
        "1. Нажмите Открыть магазин\n"
        "2. Выберите категорию (Farm, BM, Запуск)\n"
        "3. Добавьте в корзину и оплатите\n"
        "4. Аккаунт выдается автоматически\n\n"
        "<b>Оплата:</b>\n"
        "Принимаем USDT (TRC-20)\n"
        "Автоматическая выдача после оплаты\n\n"
        "По вопросам: @your_support"
    )
    await message.answer(help_text)

@dp.message(Command("cancel"))
async def cmd_cancel(message: Message):
    """Отменяет текущее действие и сбрасывает состояние"""
    user_id = message.from_user.id

    if user_id in admin_states:
        del admin_states[user_id]
        await message.answer(
            "✅ <b>Действие отменено</b>\n\n"
            "Вы вернулись в главное меню.\n"
            "Используйте /start для открытия магазина."
        )
    else:
        await message.answer(
            "Нет активных действий для отмены.\n"
            "Используйте /start для открытия магазина."
        )

# ===== CALLBACK HANDLERS =====
@dp.callback_query(F.data == "my_orders")
async def callback_my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    orders = db.get_user_orders(user_id)

    if not orders:
        text = (
            "<b>🛒 Мои покупки</b>\n\n"
            "У вас пока нет покупок.\n\n"
            "Нажмите /start чтобы открыть магазин!"
        )
        await callback.message.answer(text)
    else:
        text = "<b>🛒 Мои покупки</b>\n\n"
        for order in orders:
            status_emoji = "✅" if order['status'] == 'paid' else "⏳"
            status_text = "Оплачен" if order['status'] == 'paid' else "В обработке"
            text += f"{status_emoji} <b>Заказ {order['order_id']}</b>\n"
            text += f"💰 Сумма: <b>{order['total']} USDT</b>\n"
            text += f"📅 Дата: {order['created_at']}\n"
            text += f"📋 Статус: {status_text}\n\n"

        await callback.message.answer(text)

    await callback.answer()

@dp.callback_query(F.data == "my_profile")
async def callback_my_profile(callback: CallbackQuery):
    user = callback.from_user
    orders = db.get_user_orders(user.id)
    balance = db.get_balance(user.id)

    text = (
        "<b>👤 Мой профиль</b>\n\n"
        f"👤 Имя: {user.first_name or 'Не указано'}\n"
        f"🔗 Username: @{user.username or 'Не указано'}\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"💰 Баланс: <b>{balance:.2f} USDT</b>\n"
        f"📦 Всего заказов: {len(orders)}\n"
    )

    if orders:
        total_spent = sum(o['total'] for o in orders if o['status'] == 'paid')
        text += f"💸 Потрачено: {total_spent} USDT\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "admin_panel")
async def callback_admin_panel(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("Доступ запрещен!", show_alert=True)
        return

    stats = db.get_stats()

    text = (
        "<b>🔐 ADMIN PANEL</b>\n\n"
        "<b>📊 Статистика:</b>\n"
        f"🃏 Карточек: {stats['total_cards']}\n"
        f"📦 Аккаунтов: {stats['total_accounts']}\n"
        f"✅ Доступно: {stats['available_accounts']}\n"
        f"❌ Продано: {stats['sold_accounts']}\n\n"
        f"📋 Заказов: {stats['total_orders']}\n"
        f"💰 Оплачено: {stats['paid_orders']}\n\n"
        f"💵 Выручка: {stats['total_revenue']} USDT\n"
        f"👥 Пользователей: {stats['total_users']}\n\n"
        "<b>🛠 Команды:</b>\n"
        "/createcard - Создать карточку товара\n"
        "/editcard - Редактировать карточку\n"
        "/addproduct - Добавить аккаунты\n"
        "/products - Список карточек\n"
        "/allorders - Все заказы\n"
        "/cancel - Отменить действие"
    )

    await callback.message.answer(text)
    await callback.answer()

# ===== ADMIN COMMANDS =====

# 1. /createcard - Create product card
@dp.message(Command("createcard"))
async def cmd_create_card(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Доступ запрещен!")
        return

    admin_states[user_id] = {"state": "create_card", "data": {}}

    text = (
        "<b>🃏 Создание карточки товара</b>\n\n"
        "Отправьте данные в формате:\n"
        "<code>Категория/Название/Страна/Возраст/Цена/Описание</code>\n\n"
        "Пример:\n"
        "<code>farm/FB Farm USA/usa/3-6/25/Качественный фарм-аккаунт для запуска рекламы</code>\n\n"
        "Категории: farm, bm, launch\n"
        "Страны: usa, uk, eu\n"
        "Возраст: 1-3, 3-6, 6+\n\n"
        "⚠️ Описание может быть любой длины"
    )
    await message.answer(text)

@dp.message(lambda msg: admin_states.get(msg.from_user.id, {}).get("state") == "create_card")
async def process_create_card(message: Message):
    user_id = message.from_user.id
    try:
        parts = message.text.split("/")
        if len(parts) < 6:
            await message.answer("❌ Неверный формат! Нужно минимум 6 полей через /")
            return

        category, title, country, age, price_str = parts[:5]
        description = parts[5] if len(parts) > 5 else ""
        price = float(price_str)
        badge = ""  # Бейдж не обязателен

        card_id = db.create_card(
            title=title.strip(),
            category=category.strip(),
            country=country.strip(),
            age=age.strip(),
            price=price,
            badge=badge.strip(),
            description=description.strip()
        )

        del admin_states[user_id]

        await message.answer(
            f"✅ <b>Карточка создана!</b>\n\n"
            f"ID: <code>{card_id}</code>\n"
            f"Название: {title}\n"
            f"Цена: {price} USDT\n\n"
            f"Теперь добавьте аккаунты: /addproduct"
        )

    except ValueError as e:
        await message.answer(f"❌ Ошибка: {e}\n\nПроверьте формат. Цена должна быть числом.")
    except Exception as e:
        logger.error(f"Error creating card: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте снова.")

# 2. /editcard - Edit product card
@dp.message(Command("editcard"))
async def cmd_edit_card(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Доступ запрещен!")
        return

    cards = db.get_all_cards()
    if not cards:
        await message.answer("Нет карточек для редактирования.")
        return

    text = "<b>✏️ Редактирование карточки</b>\n\nВыберите ID карточки:\n\n"
    for card in cards:
        text += f"ID: <code>{card['id']}</code> | {card['title']} | {card['price']} USDT\n"

    admin_states[user_id] = {"state": "edit_card_select", "data": {}}
    await message.answer(text)

@dp.message(lambda msg: admin_states.get(msg.from_user.id, {}).get("state") == "edit_card_select")
async def process_edit_card_select(message: Message):
    user_id = message.from_user.id
    try:
        card_id = int(message.text.strip())
        card = db.get_card(card_id)

        if not card:
            await message.answer("❌ Карточка не найдена!")
            return

        admin_states[user_id] = {"state": "edit_card_fields", "data": {"card_id": card_id}}

        await message.answer(
            f"<b>Редактирование карточки ID: {card_id}</b>\n\n"
            f"Текущие данные:\n"
            f"Название: {card['title']}\n"
            f"Категория: {card['category']}\n"
            f"Страна: {card['country']}\n"
            f"Возраст: {card['age']}\n"
            f"Цена: {card['price']}\n"
            f"Бейдж: {card['badge']}\n"
            f"Описание: {card['description']}\n\n"
            f"Отправьте новые данные в формате:\n"
            f"<code>Название|Категория|Страна|Возраст|Цена|Бейдж|Описание</code>\n\n"
            f"Или отправьте только поля для изменения:\n"
            f"<code>price|30</code> - изменить только цену\n"
            f"<code>title|Новое название</code> - изменить только название"
        )

    except ValueError:
        await message.answer("❌ Введите число (ID карточки)")

@dp.message(lambda msg: admin_states.get(msg.from_user.id, {}).get("state") == "edit_card_fields")
async def process_edit_card_fields(message: Message):
    user_id = message.from_user.id
    card_id = admin_states[user_id]["data"]["card_id"]

    try:
        text = message.text.strip()

        # Check if single field update
        if "/" in text and text.count("/") == 1:
            field, value = text.split("/", 1)
            field = field.strip().lower()
            value = value.strip()

            if field == "price":
                value = float(value)

            db.update_card(card_id, {field: value})
            await message.answer(f"✅ Поле '{field}' обновлено!")
        else:
            # Full update
            parts = text.split("/")
            if len(parts) < 6:
                await message.answer("❌ Неверный формат! Нужно минимум 6 полей через /")
                return

            category, title, country, age, price_str = parts[:5]
            description = parts[5] if len(parts) > 5 else ""
            badge = ""

            db.update_card(card_id, {
                "title": title.strip(),
                "category": category.strip(),
                "country": country.strip(),
                "age": age.strip(),
                "price": float(price_str),
                "badge": badge.strip(),
                "description": description.strip()
            })
            await message.answer("✅ Карточка полностью обновлена!")

        del admin_states[user_id]

    except Exception as e:
        logger.error(f"Error editing card: {e}")
        await message.answer(f"❌ Ошибка: {e}")

# 3. /addproduct - Add accounts from file
@dp.message(Command("addproduct"))
async def cmd_add_product(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Доступ запрещен!")
        return

    cards = db.get_all_cards()
    if not cards:
        await message.answer(
            "❌ Нет карточек товаров!\n\n"
            "Сначала создайте карточку: /createcard"
        )
        return

    text = "<b>📦 Добавление аккаунтов</b>\n\nВыберите ID карточки:\n\n"
    for card in cards:
        stats = db.get_card_stats(card['id'])
        text += f"ID: <code>{card['id']}</code> | {card['title']} | {card['price']} USDT | Доступно: {stats['available']}\n"

    admin_states[user_id] = {"state": "add_product_select_card", "data": {}}
    await message.answer(text)

@dp.message(lambda msg: admin_states.get(msg.from_user.id, {}).get("state") == "add_product_select_card")
async def process_add_product_select(message: Message):
    user_id = message.from_user.id
    try:
        card_id = int(message.text.strip())
        card = db.get_card(card_id)

        if not card:
            await message.answer("❌ Карточка не найдена!")
            return

        admin_states[user_id] = {
            "state": "add_product_upload", 
            "data": {"card_id": card_id}
        }

        await message.answer(
            f"<b>📤 Загрузка аккаунтов для: {card['title']}</b>\n\n"
            f"Отправьте .txt файл с аккаунтами.\n\n"
            f"Формат (1 строка = 1 аккаунт):\n"
            f"<code>ID_аккаунта|email|пароль|cookies|2FA</code>\n\n"
            f"Пример:\n"
            f"<code>1000234567890123|user@gmail.com|pass123|cookie_data|123456</code>\n\n"
            f"⚠️ Проверка дубликатов: по ID и email"
        )

    except ValueError:
        await message.answer("❌ Введите число (ID карточки)")

@dp.message(lambda msg: admin_states.get(msg.from_user.id, {}).get("state") == "add_product_upload")
async def process_add_product_file(message: Message):
    user_id = message.from_user.id
    card_id = admin_states[user_id]["data"]["card_id"]

    if not message.document:
        await message.answer("❌ Пожалуйста, отправьте файл .txt")
        return

    # Download file
    try:
        file = await bot.get_file(message.document.file_id)
        file_path = f"C:/Users/Administrator/Desktop/fb-shop/temp_accounts_{user_id}.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        await bot.download_file(file.file_path, file_path)

        # Parse file
        accounts_data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) < 3:
                    await message.answer(f"⚠️ Строка {line_num}: пропущена (неверный формат)")
                    continue

                accounts_data.append({
                    "account_id": parts[0].strip(),
                    "email": parts[1].strip() if len(parts) > 1 else "",
                    "password": parts[2].strip() if len(parts) > 2 else "",
                    "cookies": parts[3].strip() if len(parts) > 3 else "",
                    "two_fa": parts[4].strip() if len(parts) > 4 else ""
                })

        # Add accounts
        result = db.add_accounts_batch(card_id, accounts_data)

        # Cleanup
        os.remove(file_path)
        del admin_states[user_id]

        # Report
        text = (
            f"<b>📊 Результат загрузки:</b>\n\n"
            f"✅ Добавлено: {result['added']}\n"
            f"⚠️ Пропущено: {result['skipped']}\n"
        )

        if result['errors']:
            text += f"\n<b>Ошибки:</b>\n"
            for error in result['errors'][:10]:  # Show first 10
                text += f"• {error}\n"
            if len(result['errors']) > 10:
                text += f"... и еще {len(result['errors']) - 10}\n"

        stats = db.get_card_stats(card_id)
        text += f"\n<b>Текущий склад:</b> {stats['available']} доступно / {stats['total']} всего"

        await message.answer(text)

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await message.answer(f"❌ Ошибка обработки файла: {e}")

# 4. /products - List cards
@dp.message(Command("products"))
async def cmd_products(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Доступ запрещен!")
        return

    cards = db.get_all_cards()
    if not cards:
        await message.answer("Нет карточек товаров.")
        return

    text = "<b>🃏 Список карточек:</b>\n\n"
    for card in cards:
        stats = db.get_card_stats(card['id'])
        text += (
            f"ID: <code>{card['id']}</code>\n"
            f"📌 {card['title']}\n"
            f"💰 {card['price']} USDT | 📦 {stats['available']} доступно\n"
            f"🏷 {card['category']} | 🌍 {card['country']} | 👶 {card['age']}\n\n"
        )

    await message.answer(text)

# 5. /allorders - All orders
@dp.message(Command("allorders"))
async def cmd_all_orders(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Доступ запрещен!")
        return

    orders = db.get_all_orders()
    if not orders:
        await message.answer("Заказов нет.")
        return

    text = "<b>📋 Все заказы:</b>\n\n"
    for o in orders[:10]:
        status = "✅ Оплачен" if o['status'] == 'paid' else "⏳ Ожидание"
        text += f"{o['order_id']} | {o['total']} USDT | {status} | {o['created_at']}\n"

    if len(orders) > 10:
        text += f"\n... и еще {len(orders) - 10} заказов"

    await message.answer(text)

# ===== WEB APP DATA HANDLER =====
@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message):
    data = message.web_app_data.data

    try:
        import json
        order_data = json.loads(data)
        action = order_data.get('action')

        if action == 'create_order':
            from plisio_api import plisio

            user_id = message.from_user.id
            username = message.from_user.username or ""
            first_name = message.from_user.first_name or ""
            card_id = order_data.get('card_id')
            total = order_data.get('total', 0)

            # Get first available account (FIFO)
            account = db.get_available_account(card_id)
            if not account:
                await message.answer("❌ Товар временно недоступен. Попробуйте позже.")
                return

            order_id = f"ORD-{user_id}-{int(asyncio.get_event_loop().time())}"

            db.create_order(order_id, user_id, username, first_name, card_id, account['id'], total)

            invoice = await plisio.create_invoice(
                order_id=order_id,
                amount=total,
                description=f"Заказ {order_id} - {account['account_id']}"
            )

            if invoice and invoice.get('status') == 'success':
                invoice_data = invoice.get('data', {})
                invoice_url = invoice_data.get('invoice_url')
                invoice_id = invoice_data.get('id')

                db.update_order_status(order_id, 'pending', invoice_id)

                pay_button = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💳 Оплатить через Plisio", url=invoice_url)]
                ])

                msg_text = (
                    f"<b>💳 Оплата заказа {order_id}</b>\n\n"
                    f"Товар: {account['account_id']}\n"
                    f"Сумма: <b>{total} USDT</b>\n\n"
                    "Нажмите кнопку ниже для оплаты."
                )

                await message.answer(msg_text, reply_markup=pay_button)
            else:
                await message.answer("Ошибка создания счета.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("Произошла ошибка.")

# ===== MENU BUTTON =====
async def set_global_menu_button():
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Магазин", web_app=WebAppInfo(url=WEBAPP_URL))
        )
        logger.info("Menu button set")
    except Exception as e:
        logger.error(f"Menu button error: {e}")

async def set_user_menu_button(chat_id: int):
    try:
        await bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonWebApp(text="Магазин", web_app=WebAppInfo(url=WEBAPP_URL))
        )
    except Exception as e:
        logger.error(f"User menu button error: {e}")

async def main():
    logger.info("Starting bot...")
    await set_global_menu_button()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")