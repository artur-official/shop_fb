updated_app_js = '''// ===== TELEGRAM WEB APP INIT =====
let tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Настройка цвета шапки Telegram
tg.setHeaderColor('#0a0a0f');
tg.setBackgroundColor('#0a0a0f');

// ===== API CONFIG =====
const API_URL = 'https://ingria-farm.com/api';

// ===== STATE =====
let cart = JSON.parse(localStorage.getItem('fb_cart')) || [];
let currentCategory = 'all';
let currentProduct = null;
let userBalance = 0;
let userTransactions = [];
let userOrders = [];

// Получаем данные пользователя из Telegram
const tgUser = tg.initDataUnsafe?.user || {};
const userId = tgUser.id || 'test_user';
const username = tgUser.username || '';
const firstName = tgUser.first_name || 'Пользователь';

// ===== NAVIGATION =====
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
    window.scrollTo(0, 0);
}

function showHome() {
    showScreen('homeScreen');
    updateNavActive('home');
}

function showCatalog() {
    showScreen('catalogScreen');
    renderProducts();
    updateNavActive('catalog');
}

function showCart() {
    showScreen('cartScreen');
    renderCart();
    updateNavActive('cart');
}

function showOrders() {
    showScreen('ordersScreen');
    loadUserOrders();
    updateNavActive('orders');
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
    document.getElementById('checkoutTotal').textContent = `${total} USDT`;
    showScreen('checkoutScreen');
}

function showSuccess() {
    showScreen('successScreen');
}

// ===== PROFILE / CABINET =====
function showProfile() {
    loadUserProfile();
    showScreen('profileScreen');
    updateNavActive('profile');
}

function showProfileTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.profile-tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.profile-tab-btn').forEach(t => t.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.closest('.profile-tab-btn').classList.add('active');
    
    // Load data if needed
    if (tabName === 'deposit') {
        renderDepositTab();
    } else if (tabName === 'purchases') {
        loadUserOrders();
    } else if (tabName === 'payments') {
        loadUserTransactions();
    }
}

// ===== LOAD USER DATA =====
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_URL}/user/${userId}`);
        const data = await response.json();
        
        userBalance = data.balance || 0;
        userOrders = data.orders || [];
        userTransactions = data.transactions || [];
        
        // Update profile header
        document.getElementById('profileName').textContent = firstName;
        document.getElementById('profileUsername').textContent = username ? '@' + username : '';
        document.getElementById('profileBalance').textContent = userBalance.toFixed(2) + ' USDT';
        document.getElementById('profileAvatar').textContent = firstName.charAt(0).toUpperCase();
        
    } catch (e) {
        console.error('Error loading profile:', e);
        // Fallback for testing
        document.getElementById('profileName').textContent = firstName;
        document.getElementById('profileUsername').textContent = username ? '@' + username : '';
        document.getElementById('profileBalance').textContent = '0.00 USDT';
        document.getElementById('profileAvatar').textContent = firstName.charAt(0).toUpperCase();
    }
}

// ===== DEPOSIT TAB =====
function renderDepositTab() {
    const container = document.getElementById('depositContent');
    container.innerHTML = `
        <div class="deposit-card">
            <div class="deposit-label">Текущий баланс</div>
            <div class="deposit-balance">${userBalance.toFixed(2)} <span>USDT</span></div>
        </div>
        
        <div class="deposit-card">
            <div class="deposit-label">Сумма пополнения</div>
            <div class="deposit-amounts">
                <button class="deposit-amount-btn" onclick="setDepositAmount(10)">10 USDT</button>
                <button class="deposit-amount-btn" onclick="setDepositAmount(25)">25 USDT</button>
                <button class="deposit-amount-btn" onclick="setDepositAmount(50)">50 USDT</button>
                <button class="deposit-amount-btn" onclick="setDepositAmount(100)">100 USDT</button>
                <button class="deposit-amount-btn" onclick="setDepositAmount(200)">200 USDT</button>
                <button class="deposit-amount-btn" onclick="setDepositAmount(500)">500 USDT</button>
            </div>
            <input type="number" id="customDepositAmount" class="deposit-input" placeholder="Или введите свою сумму" min="1" step="1">
        </div>
        
        <div class="deposit-info">
            <p>💳 Пополнение через Plisio (USDT TRC-20)</p>
            <p>⚡ Средства зачисляются автоматически</p>
            <p>🔒 Минимальная сумма: 1 USDT</p>
        </div>
        
        <button class="btn btn-primary btn-large" onclick="processDeposit()">
            <span class="btn-icon">💎</span>
            Пополнить баланс
        </button>
    `;
}

let selectedDepositAmount = 0;

function setDepositAmount(amount) {
    selectedDepositAmount = amount;
    document.querySelectorAll('.deposit-amount-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.includes(amount)) {
            btn.classList.add('active');
        }
    });
    document.getElementById('customDepositAmount').value = '';
}

async function processDeposit() {
    const customAmount = parseFloat(document.getElementById('customDepositAmount')?.value || 0);
    const amount = customAmount > 0 ? customAmount : selectedDepositAmount;
    
    if (amount < 1) {
        tg.showAlert('Введите сумму пополнения!');
        return;
    }
    
    try {
        // Create deposit transaction
        const response = await fetch(`${API_URL}/balance/deposit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                amount: amount,
                description: 'Balance deposit via Plisio'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Send to bot for Plisio invoice creation
            const depositData = {
                action: 'create_deposit',
                transaction_id: data.transaction_id,
                amount: amount,
                user_id: userId
            };
            
            tg.sendData(JSON.stringify(depositData));
            tg.showAlert('Создаём счёт на пополнение...');
        }
    } catch (e) {
        console.error('Deposit error:', e);
        tg.showAlert('Ошибка создания счёта. Попробуйте позже.');
    }
}

// ===== PURCHASES TAB =====
async function loadUserOrders() {
    const container = document.getElementById('purchasesContent');
    
    try {
        const response = await fetch(`${API_URL}/orders/${userId}`);
        const data = await response.json();
        userOrders = data.orders || [];
    } catch (e) {
        console.error('Error loading orders:', e);
    }
    
    if (userOrders.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <p>У вас пока нет покупок</p>
                <p class="empty-sub">Купите первый аккаунт!</p>
                <button class="btn btn-primary" style="margin-top: 20px;" onclick="showCatalog()">В каталог</button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = userOrders.map(order => {
        const statusClass = order.status === 'paid' ? 'completed' : 'pending';
        const statusText = order.status === 'paid' ? '✅ Выполнен' : '⏳ Ожидание';
        
        return `
            <div class="order-card">
                <div class="order-header">
                    <span class="order-id">${order.order_id}</span>
                    <span class="order-status ${statusClass}">${statusText}</span>
                </div>
                <div class="order-items">
                    ${order.items.map(item => `
                        <div class="order-item">${item.title} — ${item.price} USDT</div>
                    `).join('')}
                </div>
                <div class="order-total">Итого: ${order.total} USDT</div>
                ${order.status === 'paid' ? `
                    <div class="order-accounts">
                        <div class="accounts-label">Данные аккаунтов:</div>
                        <div class="account-data">
                            <div class="account-label">Аккаунт доступен</div>
                            <div>Login: ${item.login || 'Скрыто'}</div>
                            <div>Password: ${item.password || 'Скрыто'}</div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// ===== PAYMENTS TAB =====
async function loadUserTransactions() {
    const container = document.getElementById('paymentsContent');
    
    try {
        const response = await fetch(`${API_URL}/transactions/${userId}`);
        const data = await response.json();
        userTransactions = data.transactions || [];
    } catch (e) {
        console.error('Error loading transactions:', e);
    }
    
    if (userTransactions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">💳</div>
                <p>История транзакций пуста</p>
                <p class="empty-sub">Пополните баланс, чтобы увидеть записи</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="transactions-list">
            ${userTransactions.map(tx => {
                const typeIcon = tx.type === 'deposit' ? '💰' : '🛒';
                const typeText = tx.type === 'deposit' ? 'Пополнение' : 'Покупка';
                const statusClass = tx.status === 'completed' ? 'completed' : 'pending';
                const statusText = tx.status === 'completed' ? '✅ Завершено' : '⏳ В обработке';
                const amountSign = tx.type === 'deposit' ? '+' : '-';
                const amountColor = tx.type === 'deposit' ? 'var(--success)' : 'var(--text-primary)';
                
                return `
                    <div class="transaction-card">
                        <div class="transaction-icon">${typeIcon}</div>
                        <div class="transaction-info">
                            <div class="transaction-title">${typeText}</div>
                            <div class="transaction-desc">${tx.description || ''}</div>
                            <div class="transaction-date">${tx.created_at || ''}</div>
                        </div>
                        <div class="transaction-amount" style="color: ${amountColor}">
                            ${amountSign}${tx.amount} USDT
                        </div>
                        <div class="transaction-status ${statusClass}">${statusText}</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// ===== FILTERS =====
function filterCategory(category) {
    currentCategory = category;
    document.getElementById('catalogTitle').textContent = 
        category === 'all' ? 'Все аккаунты' :
        category === 'farm' ? 'Фарм-аккаунты' :
        category === 'bm' ? 'Business Manager' :
        category === 'launch' ? 'С запуском' : 'Каталог';
    showCatalog();
}

function applyFilters() {
    renderProducts();
}

// ===== LOAD PRODUCTS FROM API =====
async function loadProducts() {
    try {
        const response = await fetch(`${API_URL}/products`);
        const data = await response.json();
        return data.products || [];
    } catch (e) {
        console.error('Error loading products:', e);
        return [];
    }
}

async function loadProductDetail(productId) {
    try {
        const response = await fetch(`${API_URL}/products/${productId}`);
        const product = await response.json();
        currentProduct = product;
        renderProductDetail(product);
    } catch (e) {
        console.error('Error loading product:', e);
    }
}

// ===== RENDER PRODUCTS =====
async function renderProducts() {
    const grid = document.getElementById('productsGrid');
    const countryFilter = document.getElementById('countryFilter').value;
    const ageFilter = document.getElementById('ageFilter').value;
    
    grid.innerHTML = '<div class="loading">Загрузка...</div>';
    
    let products = await loadProducts();
    
    if (currentCategory !== 'all') {
        products = products.filter(p => p.category === currentCategory);
    }
    if (countryFilter !== 'all') {
        products = products.filter(p => p.country === countryFilter);
    }
    if (ageFilter !== 'all') {
        products = products.filter(p => p.age === ageFilter);
    }
    
    if (products.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <p>Ничего не найдено</p>
                <p class="empty-sub">Попробуйте изменить фильтры</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = products.map(product => `
        <div class="product-card" onclick="showProduct(${product.id})">
            <div class="product-header">
                <div class="product-title">${product.title}</div>
                <div class="product-badge">${product.badge}</div>
            </div>
            <div class="product-tags">
                <span class="product-tag">${product.country?.toUpperCase() || ''}</span>
                <span class="product-tag">${product.age}</span>
                <span class="product-tag">${product.category}</span>
            </div>
            <div class="product-footer">
                <div class="product-price">${product.price} <span>USDT</span></div>
                <button class="btn-add" onclick="event.stopPropagation(); addToCart(${product.id})">В корзину</button>
            </div>
        </div>
    `).join('');
}

function renderProductDetail(product) {
    const detail = document.getElementById('productDetail');
    const specs = product.specs || {};
    
    detail.innerHTML = `
        <div class="product-detail-header">
            <div class="product-detail-title">${product.title}</div>
            <div class="product-detail-desc">${product.description}</div>
        </div>
        <div class="product-detail-specs">
            ${Object.entries(specs).map(([key, value]) => `
                <div class="spec-row">
                    <span class="spec-label">${key}</span>
                    <span class="spec-value">${value}</span>
                </div>
            `).join('')}
        </div>
        <div class="product-detail-price">${product.price} USDT</div>
        <button class="btn btn-primary btn-large" onclick="addToCart(${product.id})">
            <span class="btn-icon">🛒</span>
            Добавить в корзину
        </button>
    `;
}

// ===== CART =====
function addToCart(productId) {
    // Load product from API or cache
    loadProductDetail(productId).then(() => {
        if (!currentProduct) return;
        
        if (cart.find(item => item.id === productId)) {
            tg.showAlert('Этот товар уже в корзине!');
            return;
        }
        
        cart.push(currentProduct);
        saveCart();
        updateCartBadge();
        
        tg.showAlert(`${currentProduct.title} добавлен в корзину!`);
        
        if (tg.HapticFeedback) {
            tg.HapticFeedback.impactOccurred('light');
        }
    });
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
    document.getElementById('cartCount').textContent = count;
    document.getElementById('navBadge').textContent = count;
    document.getElementById('navBadge').style.display = count > 0 ? 'block' : 'none';
}

function renderCart() {
    const content = document.getElementById('cartContent');
    
    if (cart.length === 0) {
        content.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🛒</div>
                <p>Корзина пуста</p>
                <p class="empty-sub">Добавьте аккаунты из каталога</p>
                <button class="btn btn-primary" style="margin-top: 20px;" onclick="showCatalog()">Перейти в каталог</button>
            </div>
        `;
        return;
    }
    
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    
    content.innerHTML = `
        ${cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.title}</div>
                    <div class="cart-item-price">${item.price} USDT</div>
                </div>
                <button class="cart-item-remove" onclick="removeFromCart(${item.id})">Удалить</button>
            </div>
        `).join('')}
        <div class="cart-total">
            <div class="cart-total-row">
                <span>Итого:</span>
                <span class="cart-total-amount">${total} USDT</span>
            </div>
        </div>
        <div class="cart-actions">
            <button class="btn btn-primary btn-large" onclick="showCheckout()">
                <span class="btn-icon">💎</span>
                Оформить заказ
            </button>
        </div>
    `;
}

// ===== CHECKOUT & PAYMENT =====
async function processPayment() {
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    
    // Check if user has enough balance
    try {
        const response = await fetch(`${API_URL}/balance/${userId}`);
        const data = await response.json();
        const balance = data.balance || 0;
        
        if (balance < total) {
            tg.showConfirm(
                `Недостаточно средств. Баланс: ${balance.toFixed(2)} USDT, нужно: ${total} USDT. Пополнить баланс?`,
                (confirmed) => {
                    if (confirmed) {
                        showProfile();
                        setTimeout(() => {
                            document.querySelector('[onclick="showProfileTab(\'deposit\')"]')?.click();
                        }, 300);
                    }
                }
            );
            return;
        }
        
        // Create order and pay with balance
        const orderData = {
            action: 'create_order',
            items: cart.map(item => ({ id: item.id, title: item.title, price: item.price })),
            total: total,
            user_id: userId,
            username: username,
            first_name: firstName
        };
        
        tg.sendData(JSON.stringify(orderData));
        
        // For demo — show success
        showSuccess();
        
    } catch (e) {
        console.error('Payment error:', e);
        tg.showAlert('Ошибка при оплате. Попробуйте позже.');
    }
}

// ===== SUCCESS =====
function showSuccess() {
    cart = [];
    saveCart();
    updateCartBadge();
    showScreen('successScreen');
    
    if (tg.HapticFeedback) {
        tg.HapticFeedback.notificationOccurred('success');
    }
}

// ===== NAV ACTIVE STATE =====
function updateNavActive(screen) {
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    const navMap = {
        'home': 0,
        'catalog': 1,
        'cart': 2,
        'orders': 3,
        'profile': 4
    };
    const index = navMap[screen];
    if (index !== undefined) {
        document.querySelectorAll('.nav-btn')[index]?.classList.add('active');
    }
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();
    
    if (tg.setHeaderColor) tg.setHeaderColor('#0a0a0f');
    if (tg.setBackgroundColor) tg.setBackgroundColor('#0a0a0f');
    
    tg.BackButton.onClick(() => {
        const activeScreen = document.querySelector('.screen.active');
        if (activeScreen.id === 'productScreen') showCatalog();
        else if (activeScreen.id === 'cartScreen') showHome();
        else if (activeScreen.id === 'checkoutScreen') showCart();
        else if (activeScreen.id === 'ordersScreen') showHome();
        else if (activeScreen.id === 'successScreen') showOrders();
        else if (activeScreen.id === 'profileScreen') showHome();
        else if (['depositTab', 'purchasesTab', 'paymentsTab'].some(id => activeScreen.id.includes(id))) showProfile();
    });
    
    const observer = new MutationObserver(() => {
        const activeScreen = document.querySelector('.screen.active');
        if (activeScreen && activeScreen.id !== 'homeScreen') {
            tg.BackButton.show();
        } else {
            tg.BackButton.hide();
        }
    });
    
    observer.observe(document.getElementById('app'), { 
        attributes: true, 
        subtree: true, 
        attributeFilter: ['class'] 
    });
});

// ===== UTILS =====
function formatPrice(price, currency) {
    return `${price} ${currency}`;
}

tg.onEvent('web_app_data', (data) => {
    console.log('Received data from bot:', data);
});
'''

with open('/mnt/agents/output/app.js', 'w', encoding='utf-8') as f:
    f.write(updated_app_js)

print("✅ app.js создан!")
print(f"Размер: {len(updated_app_js)} символов")
