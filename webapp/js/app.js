let tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

const API_URL = 'https://ingria-farm.com/api';
let cart = JSON.parse(localStorage.getItem('fb_cart')) || [];
let currentCategory = 'all';
let currentProduct = null;
let userBalance = 0;

const tgUser = tg.initDataUnsafe?.user || {};
const userId = tgUser.id || 'test_user';
const username = tgUser.username || '';
const firstName = tgUser.first_name || 'Пользователь';

// ===== NAVIGATION =====
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const screen = document.getElementById(screenId);
    if (screen) screen.classList.add('active');
    window.scrollTo(0, 0);
}

function showHome() {
    showScreen('homeScreen');
    updateNavActive(0);
}

function showCatalog() {
    showScreen('catalogScreen');
    renderProducts();
    updateNavActive(1);
}

function showCart() {
    showScreen('cartScreen');
    renderCart();
    updateNavActive(2);
}

function showProfile() {
    showScreen('profileScreen');
    updateNavActive(3);
    loadUserProfile();
    setupDepositClick();
}

function showProduct(productId) {
    loadProductDetail(productId);
    showScreen('productScreen');
}

function showCheckout() {
    if (cart.length === 0) {
        tg.showAlert('Корзина пуста!');
        return;
    }
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    document.getElementById('checkoutTotal').textContent = total + ' USDT';
    showScreen('checkoutScreen');
}

function updateNavActive(index) {
    document.querySelectorAll('.nav-btn').forEach((btn, i) => {
        btn.classList.toggle('active', i === index);
    });
}

// ===== DEPOSIT =====
function showDeposit() {
    tg.showAlert('Пополнение баланса через Plisio');
}

function setupDepositClick() {
    // Клик на баланс = пополнить
    const balance = document.getElementById('profileBalance');
    if (balance) {
        balance.onclick = () => showDeposit();
    }
}

// ===== PROFILE TABS =====
function showProfileTab(tabName) {
    document.querySelectorAll('.profile-tab-content').forEach(t => t.classList.remove('active'));
    const tab = document.getElementById(tabName + 'Tab');
    if (tab) tab.classList.add('active');

    if (tabName === 'purchases') loadUserOrders();
    else if (tabName === 'payments') loadUserTransactions();
}

// ===== USER DATA =====
async function loadUserProfile() {
    try {
        const response = await fetch(API_URL + '/user/' + userId);
        const data = await response.json();
        userBalance = data.balance || 0;
        document.getElementById('userName').textContent = firstName;
        document.getElementById('profileBalance').textContent = userBalance.toFixed(2) + '$';
    } catch (e) {
        console.error('Profile error:', e);
        document.getElementById('userName').textContent = firstName;
        document.getElementById('profileBalance').textContent = '0.00$';
    }
}

// ===== PURCHASES =====
async function loadUserOrders() {
    const container = document.getElementById('purchasesContent');
    if (!container) return;

    try {
        const response = await fetch(API_URL + '/orders/' + userId);
        const data = await response.json();
        const orders = data.orders || [];

        if (orders.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><p>Нет покупок</p></div>';
            return;
        }

        container.innerHTML = orders.map(order => {
            const status = order.status === 'paid' ? 'completed' : 'pending';
            const statusText = order.status === 'paid' ? '✅ Выполнен' : '⏳ Ожидание';
            return `
                <div class="order-card">
                    <div class="order-header">
                        <span>${order.order_id}</span>
                        <span class="order-status ${status}">${statusText}</span>
                    </div>
                    <div>Итого: ${order.total} $</div>
                </div>
            `;
        }).join('');
    } catch (e) {
        container.innerHTML = '<div class="empty-state"><p>Ошибка загрузки</p></div>';
    }
}

// ===== PAYMENTS =====
async function loadUserTransactions() {
    const container = document.getElementById('paymentsContent');
    if (!container) return;

    try {
        const response = await fetch(API_URL + '/transactions/' + userId);
        const data = await response.json();
        const transactions = data.transactions || [];

        if (transactions.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-icon">💳</div><p>Нет транзакций</p></div>';
            return;
        }

        container.innerHTML = transactions.map(tx => {
            const icon = tx.type === 'deposit' ? '💰' : '🛒';
            const sign = tx.type === 'deposit' ? '+' : '-';
            const color = tx.type === 'deposit' ? 'color:var(--success)' : '';
            return `
                <div class="transaction-card">
                    <div class="transaction-icon">${icon}</div>
                    <div class="transaction-info">
                        <div class="transaction-title">${tx.type === 'deposit' ? 'Пополнение' : 'Покупка'}</div>
                        <div class="transaction-desc">${tx.description || ''}</div>
                    </div>
                    <div class="transaction-amount" style="${color}">${sign}${tx.amount} $</div>
                </div>
            `;
        }).join('');
    } catch (e) {
        container.innerHTML = '<div class="empty-state"><p>Ошибка загрузки</p></div>';
    }
}

// ===== PRODUCTS =====
async function loadProducts() {
    try {
        let url = API_URL + '/products';
        const country = document.getElementById('countryFilter')?.value;
        const age = document.getElementById('ageFilter')?.value;
        const params = [];
        if (country && country !== 'all') params.push('country=' + country);
        if (age && age !== 'all') params.push('age=' + age);
        if (params.length) url += '?' + params.join('&');

        const response = await fetch(url);
        const data = await response.json();
        return data.products || [];
    } catch (e) {
        return [];
    }
}

async function renderProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    grid.innerHTML = '<div class="loading">Загрузка...</div>';
    let products = await loadProducts();
    if (currentCategory !== 'all') products = products.filter(p => p.category === currentCategory);

    if (products.length === 0) {
        grid.innerHTML = '<div class="empty-state"><p>Ничего не найдено</p></div>';
        return;
    }

    grid.innerHTML = products.map(p => `
        <div class="product-card" onclick="showProduct(${p.id})">
            <div class="product-header">
                <div class="product-title">${p.title}</div>
                <div class="product-badge">${p.badge}</div>
            </div>
            <div class="product-tags">
                <span class="product-tag">${p.country?.toUpperCase()}</span>
                <span class="product-tag">${p.age}</span>
            </div>
            <div class="product-footer">
                <div class="product-price">${p.price} $</div>
                <button class="btn-add" onclick="event.stopPropagation(); addToCart(${p.id})">В корзину</button>
            </div>
        </div>
    `).join('');
}

async function loadProductDetail(productId) {
    try {
        const response = await fetch(API_URL + '/products/' + productId);
        currentProduct = await response.json();
        const specs = currentProduct.specs || {};
        document.getElementById('productDetail').innerHTML = `
            <div style="font-size:22px;font-weight:700;margin-bottom:10px;">${currentProduct.title}</div>
            <div style="color:var(--text2);margin-bottom:20px;">${currentProduct.description}</div>
            ${Object.entries(specs).map(([k,v]) => `
                <div class="spec-row"><span class="spec-label">${k}</span><span>${v}</span></div>
            `).join('')}
            <div style="font-size:28px;font-weight:700;margin:20px 0;color:var(--success);">${currentProduct.price} $</div>
            <button class="btn btn-primary" onclick="addToCart(${currentProduct.id})">В корзину</button>
        `;
    } catch (e) {
        console.error('Product error:', e);
    }
}

function filterCategory(category) {
    currentCategory = category;
    const titles = {'all': 'Все', 'farm': 'Фарм', 'bm': 'БМ', 'launch': 'Запуск'};
    document.getElementById('catalogTitle').textContent = titles[category] || 'Каталог';
    showCatalog();
}

function applyFilters() {
    renderProducts();
}

// ===== CART =====
function addToCart(productId) {
    if (!currentProduct || currentProduct.id !== productId) {
        loadProductDetail(productId).then(() => doAddToCart());
        return;
    }
    doAddToCart();
}

function doAddToCart() {
    if (!currentProduct) return;
    if (cart.find(item => item.id === currentProduct.id)) {
        tg.showAlert('Уже в корзине!');
        return;
    }
    cart.push(currentProduct);
    saveCart();
    updateCartBadge();
    tg.showAlert('Добавлено!');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartBadge();
    renderCart();
}

function saveCart() {
    localStorage.setItem('fb_cart', JSON.stringify(cart));
}

function updateCartBadge() {
    const count = cart.length;
    const cartCount = document.getElementById('cartCount');
    const navBadge = document.getElementById('navBadge');
    if (cartCount) cartCount.textContent = count;
    if (navBadge) {
        navBadge.textContent = count;
        navBadge.style.display = count > 0 ? 'block' : 'none';
    }
}

function renderCart() {
    const content = document.getElementById('cartContent');
    if (!content) return;

    if (cart.length === 0) {
        content.innerHTML = '<div class="empty-state"><div class="empty-icon">🛒</div><p>Корзина пуста</p><button class="btn btn-primary" onclick="showCatalog()">В каталог</button></div>';
        return;
    }

    const total = cart.reduce((sum, item) => sum + item.price, 0);
    content.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div><div style="font-weight:600;">${item.title}</div><div style="color:var(--success);">${item.price} $</div></div>
            <button class="cart-item-remove" onclick="removeFromCart(${item.id})">Удалить</button>
        </div>
    `).join('') + `
        <div class="cart-total">${total} $</div>
        <button class="btn btn-primary" onclick="showCheckout()">Оформить</button>
    `;
}

// ===== PAYMENT =====
async function processPayment() {
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    try {
        const response = await fetch(API_URL + '/balance/' + userId);
        const data = await response.json();
        if ((data.balance || 0) < total) {
            tg.showAlert('Недостаточно средств. Пополните баланс.');
            return;
        }
        tg.sendData(JSON.stringify({
            action: 'create_order',
            items: cart.map(i => ({id: i.id, title: i.title, price: i.price})),
            total: total,
            user_id: userId
        }));
        showSuccess();
    } catch (e) {
        tg.showAlert('Ошибка оплаты');
    }
}

function showSuccess() {
    cart = [];
    saveCart();
    updateCartBadge();
    showScreen('successScreen');
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();
    tg.setHeaderColor('#1a1a2e');
    tg.setBackgroundColor('#1a1a2e');
});