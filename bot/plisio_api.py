import aiohttp
from config import PLISIO_API_KEY, PLISIO_WEBHOOK_URL

class PlisioAPI:
    def __init__(self):
        self.api_key = PLISIO_API_KEY
        self.base_url = "https://api.plisio.net/api/v1"

    async def create_invoice(self, order_id, amount, description, email=None, network="TRC20"):
        params = {
            "api_key": self.api_key,
            "order_number": order_id,
            "order_name": description,
            "amount": amount,
            "currency": "USD",
            "source_currency": "USDT",
            "source_currency_network": network,
            "callback_url": PLISIO_WEBHOOK_URL,
            "email": email or "",
            "skip_confirm": "1"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/operations/invoices/new",
                params=params
            ) as response:
                return await response.json()

    async def get_invoice(self, invoice_id):
        params = {"api_key": self.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/operations/invoices/{invoice_id}",
                params=params
            ) as response:
                return await response.json()

plisio = PlisioAPI()