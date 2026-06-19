import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, WEBAPP_URL, ADMIN_IDS
from database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ===== USER COMMANDS =====
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)

    welcome_text = "<b>Privet, " + user.first_name + "!</b>\n\nDobro pozhalovat v magazin akkauntov Facebook!\n\nKachestvennye farm-akkaunty, BM i akkaunty s zapuskom\nMgnovennaya vydacha posle oplaty\nOplata kryptoy (USDT)\n\nNazhmite knopku nizhe, chtoby otkryt magazin:"

    buttons = [
        [InlineKeyboardButton(text="Otkryt magazin", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="Moi zakazy", callback_data="my_orders")],
        [InlineKeyboardButton(text="Moy profil", callback_data="my_profile")]
    ]

    # Add admin button if user is admin
    if user.id in ADMIN_IDS:
        buttons.append([InlineKeyboardButton(text="ADMIN PANEL", callback_data="admin_panel")])

    webapp_button = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(welcome_text, reply_markup=webapp_button)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = "<b>Pomosh</b>\n\n<b>Kak kupit akkaunt:</b>\n1. Nazhmite Otkryt magazin\n2. Vyberite kategoriyu (Farm, BM, Zapusk)\n3. Dobavte v korzinu i oplatite\n4. Akkaunt vydajetsya avtomaticheski\n\n<b>Oplata:</b>\nPrinimajem USDT (TRC-20)\nKomissiya seti minimalnaya\nAvtomaticheskaya vydacha posle oplaty\n\n<b>Chto vhodit v akkaunt:</b>\nLogin i parol\nCookies dlya vkhoda\nKod dvuhfaktornoy auth (jesli est)\n\n<b>Vazhno:</b>\nAkkaunty prodayutsya odin raz\nPosle pokupki srazu menyajte dannye\nGarantiya 24 chasa na proverku\n\nPo voprosam: @your_support"
    await message.answer(help_text)

@dp.message(Command("orders"))
async def cmd_orders(message: Message):
    user_id = message.from_user.id
    orders = db.get_user_orders(user_id)

    if not orders:
        await message.answer("U vas poka net zakazov.\n\nNazhmite /start chtoby otkryt magazin!")
        return

    text = "<b>Vashi zakazy:</b>\n\n"
    for order in orders:
        status_emoji = "OK" if order['status'] == 'paid' else "..."
        text += status_emoji + " <b>Zakaz " + order['order_id'] + "</b>\n"
        text += "Summa: <b>" + str(order['total']) + " USDT</b>\n"
        text += "Data: " + str(order['created_at']) + "\n"
        text += "Tovarov: " + str(len(order['items'])) + "\n\n"

    await message.answer(text)

@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    user = message.from_user
    db_user = db.get_user(user.id)
    orders = db.get_user_orders(user.id)

    text = "<b>Vash profil:</b>\n\n"
    text += "Imya: " + (user.first_name or "Ne ukazano") + "\n"
    text += "Username: @" + (user.username or "Ne ukazano") + "\n"
    text += "ID: " + str(user.id) + "\n\n"
    text += "Vsego zakazov: " + str(len(orders)) + "\n"

    if orders:
        total_spent = sum(o['total'] for o in orders if o['status'] == 'paid')
        text += "Potracheno: " + str(total_spent) + " USDT\n"

    await message.answer(text)

# ===== ADMIN COMMANDS =====
@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Dostup zapreshchen!")
        return

    stats = db.get_stats()

    text = "<b>ADMIN PANEL</b>\n\n"
    text += "<b>Statistika:</b>\n"
    text += "Tovarov vsego: " + str(stats['total_products']) + "\n"
    text += "Dostupno: " + str(stats['available_products']) + "\n"
    text += "Prodano: " + str(stats['sold_products']) + "\n\n"
    text += "Zakazov vsego: " + str(stats['total_orders']) + "\n"
    text += "Oplacheno: " + str(stats['paid_orders']) + "\n"
    text += "V obrabotke: " + str(stats['pending_orders']) + "\n\n"
    text += "Vyruchka: " + str(stats['total_revenue']) + " USDT\n"
    text += "Polzovateley: " + str(stats['total_users']) + "\n\n"
    text += "<b>Komandy:</b>\n"
    text += "/addproduct - Dobavit tovar\n"
    text += "/products - Spisok tovarov\n"
    text += "/allorders - Vse zakazy"

    await message.answer(text)

@dp.message(Command("addproduct"))
async def cmd_add_product(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Dostup zapreshchen!")
        return

    text = "<b>Dobavlenie tovara:</b>\n\n"
    text += "Otpravte dannye v formate:\n"
    text += "<code>\n"
    text += "TITLE: Nazvanie\n"
    text += "CATEGORY: farm/bm/launch\n"
    text += "COUNTRY: usa/uk/eu\n"
    text += "AGE: 1-3/3-6/6+\n"
    text += "PRICE: 25\n"
    text += "BADGE: Populyarny\n"
    text += "LOGIN: email@gmail.com\n"
    text += "PASSWORD: pass123\n"
    text += "COOKIES: cookies.json\n"
    text += "2FA: 123456 (ili pusto)\n"
    text += "DESCRIPTION: Opisanie tovara\n"
    text += "</code>"

    await message.answer(text)

@dp.message(Command("products"))
async def cmd_products(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Dostup zapreshchen!")
        return

    products = db.get_all_products()
    if not products:
        await message.answer("Tovarov net.")
        return

    text = "<b>Spisok tovarov:</b>\n\n"
    for p in products[:20]:  # Limit to 20
        status = "Dostupno" if p['status'] == 'available' else "Prodano"
        text += "ID: " + str(p['id']) + " | " + p['title'] + " | " + str(p['price']) + " USDT | " + status + "\n"

    if len(products) > 20:
        text += "\n... i eshche " + str(len(products) - 20) + " tovarov"

    await message.answer(text)

@dp.message(Command("allorders"))
async def cmd_all_orders(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.answer("Dostup zapreshchen!")
        return

    orders = db.get_all_orders()
    if not orders:
        await message.answer("Zakazov net.")
        return

    text = "<b>Vse zakazy:</b>\n\n"
    for o in orders[:10]:
        status = "Oplachen" if o['status'] == 'paid' else "Ozhidanie"
        text += o['order_id'] + " | " + str(o['total']) + " USDT | " + status + " | " + str(o['created_at']) + "\n"

    if len(orders) > 10:
        text += "\n... i eshche " + str(len(orders) - 10) + " zakazov"

    await message.answer(text)

# ===== WEB APP DATA HANDLER =====
@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message):
    data = message.web_app_data.data

    try:
        import json
        order_data = json.loads(data)
        action = order_data.get('action')

        if action == 'create_invoice':
            from plisio_api import plisio

            user_id = message.from_user.id
            username = message.from_user.username or ""
            first_name = message.from_user.first_name or ""
            items = order_data.get('items', [])
            total = order_data.get('total', 0)
            order_id = "ORD-" + str(user_id) + "-" + str(int(asyncio.get_event_loop().time()))

            db.create_order(order_id, user_id, username, first_name, items, total)

            invoice = await plisio.create_invoice(
                order_id=order_id,
                amount=total,
                description="Zakaz " + order_id + " - " + str(len(items)) + " akkauntov"
            )

            if invoice and invoice.get('status') == 'success':
                invoice_data = invoice.get('data', {})
                invoice_url = invoice_data.get('invoice_url')
                invoice_id = invoice_data.get('id')

                db.update_order_status(order_id, 'pending', invoice_id)

                pay_button = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Oplatit cherez Plisio", url=invoice_url)]
                ])

                msg_text = "<b>Oplata zakaza " + order_id + "</b>\n\n"
                msg_text += "Summa: <b>" + str(total) + " USDT</b>\n"
                msg_text += "Tovarov: " + str(len(items)) + "\n\n"
                msg_text += "Nazhmite knopku nizhe dlya oplaty. Posle oplaty akkaunty budut vydany avtomaticheski!"

                await message.answer(msg_text, reply_markup=pay_button)
            else:
                await message.answer("Oshibka sozdaniya scheta.\nPoprobujte pozzhe ili obratites v podderzhku.")

    except Exception as e:
        logger.error("Error processing web_app_data: " + str(e))
        await message.answer("Proizoshla oshibka. Poprobujte pozzhe.")

async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
