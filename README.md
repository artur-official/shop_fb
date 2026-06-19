# FB Shop - Telegram Web App

## Структура проекта
```
fb-shop-complete/
├── bot/                    # Python backend
│   ├── config.py          # Configuration
│   ├── database.py        # SQLite database
│   ├── plisio_api.py      # Plisio payment integration
│   ├── api.py             # FastAPI server
│   ├── bot.py             # Telegram bot (aiogram)
│   ├── requirements.txt   # Python dependencies
│   ├── start_bot.bat      # Start bot
│   └── start_api.bat      # Start API server
├── webapp/                 # Frontend (HTML/CSS/JS)
│   ├── index.html
│   ├── css/
│   └── js/
└── nginx/
    └── conf/
        └── nginx.conf      # Nginx configuration
```

## Установка

### 1. Установи Python 3.11+
https://python.org/downloads

### 2. Установи зависимости
```bash
cd bot
pip install -r requirements.txt
```

### 3. Установи Nginx для Windows
1. Скачай с https://nginx.org/en/download.html
2. Распакуй в C:\nginx
3. Замени C:\nginx\conf\nginx.conf на наш файл

### 4. Настройка
- Открой bot/config.py
- Добавь свой Telegram ID в ADMIN_IDS

### 5. Запуск

**Окно 1 - API Server:**
```bash
cd bot
start_api.bat
```

**Окно 2 - Telegram Bot:**
```bash
cd bot
start_bot.bat
```

**Окно 3 - Nginx:**
```bash
cd C:\nginx
start nginx
```

## Доступ
- Web App: https://ingria-farm.com
- API: https://ingria-farm.com/api/
- Health: https://ingria-farm.com/health

## Настройка Cloudflare
1. SSL/TLS -> Flexible
2. Always Use HTTPS -> ON
3. DNS -> A-запись @ -> 135.181.74.25
