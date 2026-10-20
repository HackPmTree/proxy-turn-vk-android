# -*- coding: utf-8 -*-
"""
Конфигурация бота GLEBSBP.
Все упоминания прошлых авторов удалены. Бот для продажи подписок СБП.
"""

# Токен бота @GLEBSBP_bot — вставь свой токен от @BotFather
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

# Канал: https://t.me/glebsbp
CHANNEL_ID = "@glebsbp"          # публичный username канала
CHANNEL_URL = "https://t.me/glebsbp"
CHANNEL_REQUIRED = True          # требовать подписку на канал

# Название продукта / бренда (везде используется это, без имён авторов)
BRAND_NAME = "GLEBSBP"
BOT_USERNAME = "GLEBSBP_bot"

# Имя владельца бота (для команды /start и контактов) — укажи своё
OWNER_NAME = "Поддержка GLEBSBP"
SUPPORT_USERNAME = "glebsbp_help"   # юзернейм поддержки без @

# Webhook / запуск
WEBHOOK_URL = ""                  # пусто = long polling
PORT = 8080

# База данных
DB_PATH = "glebsbp.db"

# Подписки: тарифы (дни, цена в рублях)
TARIFFS = {
    "1 месяц":  {"days": 30,  "price": 299},
    "3 месяца": {"days": 90,  "price": 699},
    "6 месяцев": {"days": 180, "price": 1199},
    "1 год":    {"days": 365, "price": 1999},
}

# Оплата через СБП — ссылка на твой приём (например, виджет ЮKassa/СБП или сервер оплаты)
SBP_PAY_URL_TEMPLATE = "https://api.example-pay.ru/sbp?amount={amount}&comment={comment}"

# Прокси для обхода блокировок (список можно расширять)
DEFAULT_PROXIES_FILE = "proxies.json"
