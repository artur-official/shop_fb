import asyncio
import logging
import os
import hmac
import hashlib
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from config import WEBAPP_URL, ADMIN_IDS, PLISIO_SECRET, PLISIO_WEBHOOK_SECRET
from database import db
from plisio_api import plisio

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MODELS =====
class OrderCreate(BaseModel):
    user_id: int
    username: str
    first_name: str
    card_id: int
    total: float

class DepositCreate(BaseModel):
    user_id: int
    amount: float

class DepositConfirm(BaseModel):
    user_id: int
    amount: float

class ProductCreate(BaseModel):
    title: str
    category: str
    country: str
    age: str
    price: float
    badge: str = ""
    description: str = ""

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    age: Optional[str] = None
    price: Optional[float] = None
    badge: Optional[str] = None
    description: Optional[str] = None

# ===== PRODUCTS (CARDS) =====
@app.get("/api/products")
@limiter.limit("60/minute")
async def get_products(request: Request, category: Optional[str] = None, country: Optional[str] = None, age: Optional[str] = None):
    """Get product cards with stats"""
    cards = db.get_all_cards(category)
    
    result = []
    for card in cards:
        stats = db.get_card_stats(card['id'])
        result.append({
            "id": card['id'],
            "title": card['title'],
            "category": card['category'],
            "country": card['country'],
            "age": card['age'],
            "price": card['price'],
            "badge": card['badge'],
            "description": card['description'],
            "available": stats['available'],
            "total": stats['total']
        })
    
    if country:
        result = [p for p in result if p['country'] == country]
    if age:
        result = [p for p in result if p['age'] == age]
    
    return {"status": "success", "data": result}

@app.get("/api/products/{product_id}")
@limiter.limit("30/minute")
async def get_product(request: Request, product_id: int):
    """Get product card details"""
    card = db.get_card(product_id)
    if not card:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stats = db.get_card_stats(product_id)
    return {
        "status": "success",
        "data": {
            **card,
            "available": stats['available'],
            "total": stats['total']
        }
    }

# ===== ORDERS =====
@app.post("/api/orders")
@limiter.limit("10/minute")
async def create_order(request: Request, order: OrderCreate):
    """Create order"""
    order_id = f"ORD-{order.user_id}-{int(asyncio.get_event_loop().time())}"
    
    account = db.get_available_account(order.card_id)
    if not account:
        raise HTTPException(status_code=400, detail="No accounts available")
    
    db.create_order(order_id, order.user_id, order.username, order.first_name, 
                    order.card_id, account['id'], order.total)
    
    return {"status": "success", "order_id": order_id, "account_id": account['id']}

@app.get("/api/orders/{user_id}")
@limiter.limit("30/minute")
async def get_user_orders(request: Request, user_id: int):
    """Get user orders"""
    orders = db.get_user_orders(user_id)
    return {"status": "success", "data": orders}

@app.get("/api/orders/detail/{order_id}")
@limiter.limit("30/minute")
async def get_order_detail(request: Request, order_id: str):
    """Get order details"""
    return {"status": "success", "order_id": order_id}

# ===== USERS =====
@app.get("/api/user/{user_id}")
@limiter.limit("30/minute")
async def get_user(request: Request, user_id: int):
    """Get user profile"""
    user = db.get_user(user_id)
    balance = db.get_balance(user_id)
    orders = db.get_user_orders(user_id)
    transactions = db.get_user_transactions(user_id)
    
    return {
        "status": "success",
        "data": {
            "user": user,
            "balance": balance,
            "orders": orders,
            "transactions": transactions
        }
    }

# ===== BALANCE =====
@app.get("/api/balance/{user_id}")
@limiter.limit("30/minute")
async def get_balance(request: Request, user_id: int):
    """Get user balance"""
    balance = db.get_balance(user_id)
    return {"status": "success", "balance": balance}

@app.post("/api/balance/deposit")
@limiter.limit("5/minute")
async def create_deposit(request: Request, deposit: DepositCreate):
    """Create deposit"""
    invoice = await plisio.create_invoice(
        order_id=f"DEP-{deposit.user_id}",
        amount=deposit.amount,
        description=f"Deposit for user {deposit.user_id}"
    )
    
    if invoice and invoice.get('status') == 'success':
        return {"status": "success", "invoice_url": invoice['data']['invoice_url']}
    
    raise HTTPException(status_code=400, detail="Failed to create deposit")

@app.post("/api/balance/confirm")
@limiter.limit("10/minute")
async def confirm_deposit(request: Request, confirm: DepositConfirm):
    """Confirm deposit"""
    db.add_balance(confirm.user_id, confirm.amount)
    db.add_transaction(confirm.user_id, "deposit", confirm.amount, "Balance deposit")
    
    return {"status": "success", "balance": db.get_balance(confirm.user_id)}

# ===== TRANSACTIONS =====
@app.get("/api/transactions/{user_id}")
@limiter.limit("30/minute")
async def get_transactions(request: Request, user_id: int):
    """Get user transactions"""
    transactions = db.get_user_transactions(user_id)
    return {"status": "success", "data": transactions}

# ===== ADMIN =====
@app.get("/api/admin/check/{user_id}")
@limiter.limit("30/minute")
async def check_admin(request: Request, user_id: int):
    """Check if user is admin"""
    is_admin = user_id in ADMIN_IDS
    return {"status": "success", "is_admin": is_admin}

@app.get("/api/admin/stats")
@limiter.limit("30/minute")
async def get_admin_stats(request: Request):
    """Get admin statistics"""
    stats = db.get_stats()
    return {"status": "success", "data": stats}

@app.get("/api/admin/products")
@limiter.limit("30/minute")
async def get_admin_products(request: Request):
    """Get all product cards for admin"""
    cards = db.get_all_cards()
    result = []
    for card in cards:
        stats = db.get_card_stats(card['id'])
        result.append({**card, **stats})
    return {"status": "success", "data": result}

@app.post("/api/admin/products")
@limiter.limit("10/minute")
async def create_product(request: Request, product: ProductCreate):
    """Create product card"""
    card_id = db.create_card(
        title=product.title,
        category=product.category,
        country=product.country,
        age=product.age,
        price=product.price,
        badge=product.badge,
        description=product.description
    )
    return {"status": "success", "id": card_id}

@app.put("/api/admin/products/{product_id}")
@limiter.limit("10/minute")
async def update_product(request: Request, product_id: int, product: ProductUpdate):
    """Update product card"""
    data = {k: v for k, v in product.dict().items() if v is not None}
    db.update_card(product_id, data)
    return {"status": "success"}

@app.delete("/api/admin/products/{product_id}")
@limiter.limit("10/minute")
async def delete_product(request: Request, product_id: int):
    """Delete product card"""
    db.delete_card(product_id)
    return {"status": "success"}

@app.get("/api/admin/orders")
@limiter.limit("30/minute")
async def get_admin_orders(request: Request):
    """Get all orders"""
    orders = db.get_all_orders()
    return {"status": "success", "data": orders}

# ===== WEBHOOK WITH SIGNATURE =====
def verify_plisio_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Plisio webhook signature using HMAC-SHA1"""
    if not secret:
        return True  # If no secret configured, skip verification (not recommended)
    
    # Plisio uses SHA1 for webhook signature
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

@app.post("/webhook/plisio")
@limiter.limit("5/minute")
async def plisio_webhook(request: Request):
    """Handle Plisio webhook with signature verification"""
    try:
        # Parse JSON body
        data = await request.json()
        
        # Get verify_hash from JSON body (for ?json=true callbacks)
        signature = data.get('verify_hash', '')
        
        # Verify signature using SHA1 (Plisio standard)
        secret = PLISIO_WEBHOOK_SECRET or PLISIO_SECRET
        if secret and signature:
            # Create payload string for verification (all fields except verify_hash)
            payload_dict = {k: v for k, v in data.items() if k != 'verify_hash'}
            payload_string = '&'.join(f"{k}={v}" for k, v in sorted(payload_dict.items()))
            
            expected = hmac.new(
                secret.encode('utf-8'),
                payload_string.encode('utf-8'),
                hashlib.sha1
            ).hexdigest()
            
            if not hmac.compare_digest(expected, signature):
                logger.warning(f"Invalid webhook signature from {request.client.host}")
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Extract data from webhook
        txn_id = data.get('txn_id')  # Plisio transaction ID
        status = data.get('status')
        invoice_total_sum = data.get('invoice_total_sum')
        ipn_type = data.get('ipn_type')  # 'pay_in' or 'invoice'
        
        logger.info(f"Webhook received: txn_id={txn_id}, status={status}, type={ipn_type}")
        
        # For invoice payments, order_id is usually in order_number or order_name
        order_id = data.get('order_number') or data.get('order_name')
        
        if not order_id and txn_id:
            # Try to find order by Plisio txn_id (we should store it when creating invoice)
            logger.info(f"Looking for order by txn_id: {txn_id}")
        
        if status == 'completed' and ipn_type == 'invoice':
            if order_id:
                # Update order status
                db.update_order_status(order_id, 'paid')
                
                # Get order details to find account
                orders = db.get_all_orders()
                order = next((o for o in orders if o['order_id'] == order_id), None)
                
                if order:
                    # Mark account as sold
                    db.mark_account_sold(order['account_id'])
                    
                    # TODO: Send account details to user via Telegram bot
                    logger.info(f"Order {order_id} completed, account marked as sold")
                else:
                    logger.warning(f"Order {order_id} not found")
            else:
                logger.warning(f"No order_id found in webhook data: {data}")
        elif status == 'completed' and ipn_type == 'pay_in':
            # This is a deposit, not invoice payment
            logger.info(f"Deposit received: {invoice_total_sum}")
        
        # Return 200 OK so Plisio knows we received it
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        # Still return 200 to prevent Plisio from retrying
        # But log the error for debugging
        return {"status": "error", "message": str(e)}

# ===== HEALTH =====
@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    return {"status": "ok", "service": "fb-shop-api"}