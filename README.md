# GLEBSBP 🏦

Бот продажи подписок через **СБП**.
Бот: **@GLEBSBP_bot** • Канал: **https://t.me/glebsbp**

Все упоминания прошлого автора удалены, бренд везде — **GLEBSBP**.

## Вкладки меню
Только: **Профили • Логи • Старт • Обход** (вкладка «Серверы» убрана).

## Обход блокировок
В модуле `bypass.py` настроен список **direct-only** ресурсов — сайтов, которые
не пускают при подключении через VPN: **Авито, Wildberries, Ozon, Max, Яндекс**
(и Сбер, VK). К ним бот подключается **напрямую**, минуя прокси. Остальные
ресурсы идут через резидентные RU-прокси из `proxies.json`.

## Установка
```bash
pip install -r requirements.txt
```

1. Открой `config.py`:
   - `BOT_TOKEN` — токен от @BotFather для @GLEBSBP_bot
   - `TARIFFS` — свои тарифы и цены
   - `SBP_PAY_URL_TEMPLATE` — ссылка твоего приёма оплаты по СБП
   - `SUPPORT_USERNAME` — юзернейм поддержки
2. Прокси (по желанию) добавь в `proxies.json`:
```json
[{"host": "185.xx.xx.xx", "port": 8080, "login": "user", "password": "pass", "proxy_type": "http", "country": "RU"}]
```

## Запуск
```bash
python bot.py
```

## Название / аватарка / описание — задаются в @BotFather
Отправь BotFather'у команды для своего бота:
- `/setname` → **GLEBSBP | Подписки СБП**
- `/setdescription` → «Официальный бот продажи подписок через СБП. Канал: https://t.me/glebsbp»
- `/setabouttext` → «Подписки СБП • @GLEBSBP_bot • t.me/glebsbp»
- `/setuserpic` → загрузи новую аватарку с логотипом **GLEBSBP**
- `/setcommands` → start, profile, buy, help, channel, support
