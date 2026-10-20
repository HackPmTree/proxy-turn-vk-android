# -*- coding: utf-8 -*-
"""Интерфейс (клавиатуры и тексты) бота GLEBSBP.

Вкладки: Профили | Логи | Старт | Обход  (вкладка «Серверы» удалена).
Все упоминания прошлого автора убраны — только бренд GLEBSBP.
"""

from config import BRAND_NAME, CHANNEL_URL, BOT_USERNAME, SUPPORT_USERNAME, TARIFFS

WELCOME = (
    f"🏦 <b>{BRAND_NAME}</b> — бот продажи подписок через СБП\n\n"
    "Здесь можно купить подписку, управлять профилями, "
    "смотреть логи и пользоваться обходом блокировок.\n\n"
    f"📢 Наш канал: {CHANNEL_URL}"
)

HELP_TEXT = (
    "<b>Команды:</b>\n"
    "/start — главное меню\n"
    "/profile — твой профиль\n"
    "/buy — купить подписку\n"
    f"/channel — подписка на канал {CHANNEL_URL}\n"
    f"/support — поддержка @{SUPPORT_USERNAME}"
)


def main_keyboard():
    """Главное меню: только Профили, Логи, Старт, Обход (без Серверов)."""
    return [
        [
            {"text": "👤 Профили", "callback_data": "tab:profiles"},
            {"text": "📋 Логи", "callback_data": "tab:logs"},
        ],
        [
            {"text": "🚀 Старт", "callback_data": "tab:start"},
            {"text": "🛡 Обход", "callback_data": "tab:bypass"},
        ],
        [
            {"text": "💳 Купить подписку", "callback_data": "tab:buy"},
            {"text": "ℹ️ Помощь", "callback_data": "tab:help"},
        ],
    ]


def tariffs_keyboard():
    rows = [[{"text": name, "callback_data": f"buy:{name}"}] for name in TARIFFS]
    rows.append([{"text": "⬅️ Назад", "callback_data": "tab:start"}])
    return rows


def bypass_keyboard():
    return [
        [{"text": "🟢 Проверить обход", "callback_data": "bypass:check"}],
        [{"text": "🇷🇺 RU-прокси (напрямую)", "callback_data": "bypass:direct"}],
        [{"text": "⬅️ Назад", "callback_data": "tab:start"}],
    ]


def buy_confirm_keyboard(tariff):
    return [
        [{"text": "✅ Оплатить через СБП", "callback_data": f"pay:{tariff}"}],
        [{"text": "⬅️ Отмена", "callback_data": "tab:buy"}],
    ]


BACK_KB = [[{"text": "⬅️ Назад", "callback_data": "tab:start"}]]

FOOTER = f"\n\n<i>{BRAND_NAME} • @{BOT_USERNAME}</i>"
