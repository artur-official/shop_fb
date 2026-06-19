// ===== TELEGRAM WEB APP INIT =====
let tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Настройка цвета шапки Telegram
tg.setHeaderColor('#0a0a0f');
tg.setBackgroundColor('#0a0a0f');

// ===== DATA =====
const products = [
    {
        id: 1,
        title: 'Фарм-аккаунт Facebook USA',
        category: 'farm',
        country: 'usa',
        age: '3-6',
        price: 25,
        currency: 'USDT',
        badge: 'Популярный',
        description: 'Качественный фарм-аккаунт Facebook, зарегистрированный в США. Подходит для запуска рекламы и создания Business Manager.',
        specs: {
            'Страна': '🇺🇸 США',
            'Возраст': '3-6 месяцев',
            'Тип': 'Фарм-аккаунт',
            'Верификация': 'По email + телефон',
            'Cookies': 'Включены',
            '2FA': 'Отключен'
        }
    },
    {
        id: 2,
        title: 'Business Manager UK',
        category: 'bm',
        country: 'uk',
        age: '6+',
        price: 45,
        currency: 'USDT',
        badge: 'БМ',
        description: 'Готовый Business Manager с привязанным рекламным аккаунтом. Возраст 6+ месяцев, высокий траст.',
        specs: {
            'Страна': '🇬🇧 Великобритания',
            'Возраст': '6+ месяцев',
            'Тип': 'Business Manager',
            'Лимит': '$250/день',
            'Верификация': 'Полная',
            'Cookies': 'Включены'
        }
    },
    {
        id: 3,
        title: 'Аккаунт с запуском EU',
        category: 'launch',
        country: 'eu',
        age: '1-3',
        price: 35,
        currency: 'USDT',
        badge: 'Запуск',
        description: 'Аккаунт с историей запуска рекламы. Уже был использован для рекламных кампаний, высокий траст.',
        specs: {
            'Страна': '🇪🇺 Европа',
            'Возраст': '1-3 месяца',
            'Тип': 'С запуском',
            'История': 'Есть запуски',
            'Верификация': 'По email',
            'Cookies': 'Включены'
        }
    },
    {
        id: 4,
        title: 'Фарм-аккаунт Facebook UK',
        category: 'farm',
        country: 'uk',
        age: '6+',
        price: 30,
        currency: 'USDT',
        badge: 'VIP',
        description: 'Премиум фарм-аккаунт из Великобритании. Возраст 6+ месяцев, отличная репутация.',
        specs: {
            'Страна': '🇬🇧 Великобритания',
            'Возраст': '6+ месяцев',
            'Тип': 'Фарм-аккаунт',
            'Верификация': 'Полная',
            'Cookies': 'Включены',
            '2FA': 'Включен'
        }
    },
    {
        id: 5,
        title: 'Business Manager USA',
        category: 'bm',
        country: 'usa',
        age: '3-6',
        price: 55,
        currency: 'USDT',
        badge: 'БМ',
        description: 'Американский Business Manager с повышенным лимитом. Идеален для серьёзных рекламных кампаний.',
        specs: {
            'Страна': '🇺🇸 США',
            'Возраст': '3-6 месяцев',
            'Тип': 'Business Manager',
            'Лимит': '$500/день',
            'Верификация': 'Полная + БМ',
            'Cookies': 'Включены'
        }
    },
    {
        id: 6,
        title: 'Аккаунт с запуском USA',
        category: 'launch',
        country: 'usa',
        age: '3-6',
        price: 40,
        currency: 'USDT',
        badge: 'Запуск',
        description: 'Американский аккаунт с успешной историей запуска. Подходит для белых и серых вертикалей.',
        specs: {
            'Страна': '🇺🇸 США',
            'Возраст': '3-6 месяцев',
            'Тип': 'С запуском',
            'История': '5+ кампаний',
            'Верификация': 'Полная',
            'Cookies': 'Включены'
        }
    },
    {
        id: 7,
        title: 'Фарм-аккаунт Facebook EU',
        category: 'farm',
        country: 'eu',
        age: '1-3',
        price: 20,
        currency: 'USDT',
        badge: 'Новый',
        description: 'Европейский фарм-аккаунт начального уровня. Отличная цена для старта.',
        specs: {
            'Страна': '🇪🇺 Европа',
            'Возраст': '1-3 месяца',
            'Тип': 'Фарм-аккаунт',
            'Верификация': 'По email',
            'Cookies': 'Включены',
            '2FA': 'Отключен'
        }
    },
    {
        id: 8,
        title: 'Business Manager EU',
        category: 'bm',
        country: 'eu',
        age: '6+',
        price: 50,
        currency: 'USDT',
        badge: 'БМ',
        description: 'Европейский Business Manager с отличной репутацией. Готов к работе сразу после покупки.',
        specs: {
            'Страна': '🇪🇺 Европа',
            'Возраст': '6+ месяцев',
            'Тип': 'Business Manager',
            'Лимит': '$250/день',
            'Верификация': 'Полная',
            'Cookies': 'Включены'
        }
    }
];

// ===== STATE =====
let cart = JSON.parse(localStorage.getItem('fb_cart')) || [];
let orders = JSON.parse(localStorage.getItem('fb_orders')) || [];
let currentCategory = 'all';
let currentProduct = null;

// ===== NAVIGATION =====
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');

    // Update nav
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    if (screenId === 'homeScreen') document.querySelectorAll('.nav-btn')[0].classList.add('active');
    if (screenId === 'catalogScreen') document.querySelectorAll('.nav-btn')[1].classList.add('active');
    if (screenId === 'cartScreen') document.querySelectorAll('.nav-btn')[2].classList.add('active');
    if (screenId === 'ordersScreen') document.querySelectorAll('.nav-btn')[3].classList.add('active');

    window.scrollTo(0, 0);
}

function showHome() {
    showScreen('homeScreen');
}

function showCatalog() {
    showScreen('catalogScreen');
    renderProducts();
}

function showCart() {
    showScreen('cartScreen');
    renderCart();
}

function showOrders() {
    showScreen('ordersScreen');
    renderOrders();
}

function showProduct(productId) {
    currentProduct = products.find(p => p.id === productId);
    if (!currentProduct) return;

    const detail = document.getElementById('productDetail');
    detail.innerHTML = `
        <div class="product-detail-header">
            <div class="product-detail-title">${currentProduct.title}</div>
            <div class="product-detail-desc">${currentProduct.description}</div>
        </div>
        <div class="product-detail-specs">
            ${Object.entries(currentProduct.specs).map(([key, value]) => `
                <div class="spec-row">
                    <span class="spec-label">${key}</span>
                    <span class="spec-value">${value}</span>
                </div>
            `).join('')}
        </div>
        <div class="product-detail-price">${currentProduct.price} ${currentProduct.currency}</div>
        <button class="btn btn-primary btn-large" onclick="addToCart(${currentProduct.id})">
            <span class="btn-icon">🛒</span>
            Добавить в корзину
        </button>
    `;

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

// ===== RENDER PRODUCTS =====
function renderProducts() {
    const grid = document.getElementById('productsGrid');
    const countryFilter = document.getElementById('countryFilter').value;
    const ageFilter = document.getElementById('ageFilter').value;

    let filtered = products;

    if (currentCategory !== 'all') {
        filtered = filtered.filter(p => p.category === currentCategory);
    }

    if (countryFilter !== 'all') {
        filtered = filtered.filter(p => p.country === countryFilter);
    }

    if (ageFilter !== 'all') {
        filtered = filtered.filter(p => p.age === ageFilter);
    }

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="cart-empty">
                <div class="cart-empty-icon">🔍</div>
                <p>Ничего не найдено</p>
                <p style="font-size: 13px; margin-top: 8px;">Попробуйте изменить фильтры</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = filtered.map(product => `
        <div class="product-card" onclick="showProduct(${product.id})">
            <div class="product-header">
                <div class="product-title">${product.title}</div>
                <div class="product-badge">${product.badge}</div>
            </div>
            <div class="product-tags">
                <span class="product-tag">${product.specs['Страна']}</span>
                <span class="product-tag">${product.specs['Возраст']}</span>
                <span class="product-tag">${product.specs['Тип']}</span>
            </div>
            <div class="product-footer">
                <div class="product-price">${product.price} <span>${product.currency}</span></div>
                <button class="btn-add" onclick="event.stopPropagation(); addToCart(${product.id})">В корзину</button>
            </div>
        </div>
    `).join('');
}

// ===== CART =====
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    if (cart.find(item => item.id === productId)) {
        tg.showAlert('Этот товар уже в корзине!');
        return;
    }

    cart.push(product);
    saveCart();
    updateCartBadge();

    tg.showAlert(`${product.title} добавлен в корзину!`);

    // Haptic feedback
    if (tg.HapticFeedback) {
        tg.HapticFeedback.impactOccurred('light');
    }
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
            <div class="cart-empty">
                <div class="cart-empty-icon">🛒</div>
                <p>Корзина пуста</p>
                <p style="font-size: 13px; margin-top: 8px;">Добавьте аккаунты из каталога</p>
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
                    <div class="cart-item-price">${item.price} ${item.currency}</div>
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
function processPayment() {
    const total = cart.reduce((sum, item) => sum + item.price, 0);

    // Показываем кнопку оплаты через CryptoBot (или другой способ)
    // В реальном приложении здесь будет запрос к backend

    tg.showConfirm(`Оплатить ${total} USDT через CryptoBot?`, (confirmed) => {
        if (confirmed) {
            // Отправляем данные в бот для создания счёта
            const orderData = {
                action: 'create_invoice',
                items: cart.map(item => ({ id: item.id, title: item.title, price: item.price })),
                total: total,
                user_id: tg.initDataUnsafe?.user?.id || 'test_user'
            };

            // Отправляем данные боту через WebAppData
            tg.sendData(JSON.stringify(orderData));

            // Для демонстрации — показываем успех
            showSuccess();
        }
    });
}

function showSuccess() {
    // Создаём заказ
    const order = {
        id: 'ORD-' + Date.now(),
        date: new Date().toLocaleString('ru-RU'),
        items: [...cart],
        total: cart.reduce((sum, item) => sum + item.price, 0),
        status: 'completed',
        accounts: cart.map(item => ({
            title: item.title,
            login: 'fb_user_' + Math.random().toString(36).substring(7) + '@gmail.com',
            password: 'Pass' + Math.random().toString(36).substring(2, 10) + '!',
            cookies: 'cookies_' + Math.random().toString(36).substring(7) + '.json',
            twoFA: Math.floor(100000 + Math.random() * 900000).toString()
        }))
    };

    orders.unshift(order);
    localStorage.setItem('fb_orders', JSON.stringify(orders));

    // Очищаем корзину
    cart = [];
    saveCart();
    updateCartBadge();

    showScreen('successScreen');

    if (tg.HapticFeedback) {
        tg.HapticFeedback.notificationOccurred('success');
    }
}

// ===== ORDERS =====
function renderOrders() {
    const list = document.getElementById('ordersList');

    if (orders.length === 0) {
        list.innerHTML = `
            <div class="order-empty">
                <div class="cart-empty-icon">📋</div>
                <p>У вас пока нет заказов</p>
                <p style="font-size: 13px; margin-top: 8px;">Купите первый аккаунт!</p>
                <button class="btn btn-primary" style="margin-top: 20px;" onclick="showCatalog()">В каталог</button>
            </div>
        `;
        return;
    }

    list.innerHTML = orders.map(order => `
        <div class="order-card">
            <div class="order-header">
                <span class="order-id">${order.id}</span>
                <span class="order-status ${order.status}">${order.status === 'completed' ? '✅ Выполнен' : '⏳ Ожидание'}</span>
            </div>
            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item">${item.title} — ${item.price} USDT</div>
                `).join('')}
            </div>
            <div class="order-total">Итого: ${order.total} USDT</div>
            ${order.status === 'completed' && order.accounts ? `
                <div class="order-accounts">
                    <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;">Данные аккаунтов:</div>
                    ${order.accounts.map((acc, idx) => `
                        <div class="account-data">
                            <div class="account-data-label">Аккаунт ${idx + 1}: ${acc.title}</div>
                            <div>Login: ${acc.login}</div>
                            <div>Password: ${acc.password}</div>
                            <div>2FA: ${acc.twoFA}</div>
                            <div>Cookies: ${acc.cookies}</div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();

    // Устанавливаем темную тему для Telegram
    if (tg.setHeaderColor) tg.setHeaderColor('#0a0a0f');
    if (tg.setBackgroundColor) tg.setBackgroundColor('#0a0a0f');

    // Показываем кнопку "Назад" в Telegram
    tg.BackButton.onClick(() => {
        const activeScreen = document.querySelector('.screen.active');
        if (activeScreen.id === 'productScreen') showCatalog();
        else if (activeScreen.id === 'cartScreen') showHome();
        else if (activeScreen.id === 'checkoutScreen') showCart();
        else if (activeScreen.id === 'ordersScreen') showHome();
        else if (activeScreen.id === 'successScreen') showOrders();
    });

    // Показываем/скрываем кнопку назад в зависимости от экрана
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

// Обработка данных от бота (если бот отправляет данные)
tg.onEvent('web_app_data', (data) => {
    console.log('Received data from bot:', data);
});
