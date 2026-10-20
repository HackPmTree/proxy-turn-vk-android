# -*- coding: utf-8 -*-
"""
GLEBSBP — бот продажи подписок через СБП.
Канал: https://t.me/glebsbp | Бот: @GLEBSBP_bot

Вкладки: Профили, Логи, Старт, Обход (вкладка «Серверы» удалена).
Все упоминания прошлого автора убраны.
"""

import datetime
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import bypass as bp
import ui
from config import (
    BOT_TOKEN,
    BRAND_NAME,
    CHANNEL_ID,
    CHANNEL_REQUIRED,
    CHANNEL_URL,
    SBP_PAY_URL_TEMPLATE,
    SUPPORT_USERNAME,
    TARIFFS,
)
from database import (
    activate_subscription,
    add_log,
    get_all_proxies,
    get_logs,
    get_subscription,
    init_db,
    upsert_user,
)

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


def kb(rows):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(**b) for b in row] for row in rows]
    )


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    if not CHANNEL_REQUIRED:
        return True
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


# ---------- /start ----------
@dp.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    u = message.from_user
    upsert_user(u.id, u.username, u.first_name)
    add_log(u.id, "start")
    if not await is_subscribed(bot, u.id):
        await message.answer(
            f"🔒 Для использования {BRAND_NAME} подпишись на канал:",
            reply_markup=kb([[{"text": "📢 Подписаться", "url": CHANNEL_URL}]]),
        )
        return
    await message.answer(ui.WELCOME + ui.FOOTER, reply_markup=kb(ui.main_keyboard()))


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(ui.HELP_TEXT)


@dp.message(Command("support"))
async def cmd_support(message: Message):
    await message.answer(f"🆘 Поддержка: @{SUPPORT_USERNAME}")


@dp.message(Command("channel"))
async def cmd_channel(message: Message):
    await message.answer(
        "📢 Наш канал:",
        reply_markup=kb([[{"text": "Открыть канал", "url": CHANNEL_URL}]]),
    )


@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    sub = get_subscription(message.from_user.id)
    if sub:
        exp = datetime.datetime.fromisoformat(sub["expires_at"])
        txt = f"✅ Подписка активна: <b>{sub['tariff']}</b>\nДействует до: {exp:%d.%m.%Y}"
    else:
        txt = "❌ Активной подписки нет."
    await message.answer(
        f"👤 <b>{message.from_user.first_name}</b> (id <code>{message.from_user.id}</code>)\n{txt}"
        + ui.FOOTER,
        reply_markup=kb(ui.BACK_KB),
    )


@dp.message(Command("buy"))
async def cmd_buy(message: Message):
    await message.answer("💳 Выбери тариф:", reply_markup=kb(ui.tariffs_keyboard()))


# ---------- Вкладки ----------
@dp.callback_query(F.data.startswith("tab:"))
async def cb_tab(call: CallbackQuery, bot: Bot):
    tab = call.data.split(":")[1]
    uid = call.from_user.id

    if tab == "start":
        await call.message.edit_text(ui.WELCOME + ui.FOOTER, reply_markup=kb(ui.main_keyboard()))
    elif tab == "help":
        await call.message.edit_text(ui.HELP_TEXT + ui.FOOTER, reply_markup=kb(ui.BACK_KB))
    elif tab == "profiles":
        sub = get_subscription(uid)
        if sub:
            exp = datetime.datetime.fromisoformat(sub["expires_at"])
            info = f"👤 Профиль: <b>{call.from_user.first_name}</b>\nПодписка: <b>{sub['tariff']}</b>\nДо: {exp:%d.%m.%Y %H:%M}"
        else:
            info = f"👤 Профиль: <b>{call.from_user.first_name}</b>\nПодписка не активна.\nНажми «Купить подписку»."
        add_log(uid, "profiles_open")
        await call.message.edit_text(info + ui.FOOTER, reply_markup=kb(ui.BACK_KB))
    elif tab == "logs":
        logs = get_logs(uid, limit=15)
        if logs:
            lines = []
            for l in logs:
                t = datetime.datetime.fromisoformat(l["created_at"]).strftime("%d.%m %H:%M")
                lines.append(f"• <code>{t}</code> — {l['action']} {l['details']}")
            text = "📋 <b>Логи действий</b>\n\n" + "\n".join(lines)
        else:
            text = "📋 Логов пока нет."
        await call.message.edit_text(text + ui.FOOTER, reply_markup=kb(ui.BACK_KB))
    elif tab == "bypass":
        await call.message.edit_text(
            "🛡 <b>Обход блокировок</b>\n\n"
            "Ресурсы, которые не пускают с VPN (Авито, WB, Ozon, Max, Яндекс),\n"
            "подключаются <b>напрямую</b> через российские айпишники без прокси.\n"
            "Остальные сайты идут через резидентные RU-прокси.",
            reply_markup=kb(ui.bypass_keyboard()),
        )
    elif tab == "buy":
        await call.message.edit_text("💳 Выбери тариф:", reply_markup=kb(ui.tariffs_keyboard()))
    await call.answer()


# ---------- Покупка / СБП ----------
@dp.callback_query(F.data.startswith("buy:"))
async def cb_buy(call: CallbackQuery):
    tariff = call.data.split(":", 1)[1]
    t = TARIFFS[tariff]
    await call.message.edit_text(
        f"💳 Тариф: <b>{tariff}</b>\nЦена: <b>{t['price']} ₽</b> (СБП)\n\n"
        "Нажми «Оплатить через СБП» для получения ссылки оплаты.",
        reply_markup=kb(ui.buy_confirm_keyboard(tariff)),
    )
    await call.answer()


@dp.callback_query(F.data.startswith("pay:"))
async def cb_pay(call: CallbackQuery):
    tariff = call.data.split(":", 1)[1]
    t = TARIFFS[tariff]
    pay_url = SBP_PAY_URL_TEMPLATE.format(amount=t["price"], comment=f"{BRAND_NAME}_{call.from_user.id}_{tariff}")
    add_log(call.from_user.id, "payment_created", tariff)
    await call.message.edit_text(
        f"🏦 Оплата через <b>СБП</b>: <b>{t['price']} ₽</b> за {tariff}\n\n"
        "1️⃣ Открой ссылку и оплати по QR или номеру телефона\n"
        "2️⃣ После оплаты подписка активируется автоматически\n"
        "Если автоактивация недоступна — пришли чек в поддержку.",
        reply_markup=kb(
            [
                [{"text": "🔗 Оплатить СБП", "url": pay_url}],
                [{"text": "✅ Я оплатил", "callback_data": f"paid:{tariff}"}],
                [{"text": "⬅️ Отмена", "callback_data": "tab:buy"}],
            ]
        ),
    )
    await call.answer()


@dp.callback_query(F.data.startswith("paid:"))
async def cb_paid(call: CallbackQuery):
    """Ручная активация (по чеку). Для боевой схемы подключи вебхук от платёжного сервиса."""
    tariff = call.data.split(":", 1)[1]
    t = TARIFFS[tariff]
    expires = activate_subscription(call.from_user.id, tariff, t["days"], t["price"])
    add_log(call.from_user.id, "subscription_activated", tariff)
    await call.message.edit_text(
        f"🎉 Подписка <b>{tariff}</b> активирована до {expires:%d.%m.%Y}!\n"
        "Спасибо за покупку 💙",
        reply_markup=kb(ui.BACK_KB),
    )
    await call.answer()


# ---------- Обход ----------
@dp.callback_query(F.data.startswith("bypass:"))
async def cb_bypass(call: CallbackQuery):
    action = call.data.split(":")[1]
    if action == "check":
        targets = ["avito.ru", "wb.ru", "ozon.ru", "max.gov.ru", "yandex.ru"]
        lines = []
        for tg in targets:
            r = bp.check_connectivity("https://" + tg)
            mark = "🟢" if r["ok"] else "🔴"
            mode = "напрямую" if r["mode"] == "direct" else "через прокси"
            lines.append(f"{mark} <code>{tg}</code> — {mode}")
        await call.message.edit_text(
            "🛡 <b>Проверка обхода:</b>\n\n" + "\n".join(lines)
            + "\n\nDirect-only ресурсы всегда идут без VPN-прокси.",
            reply_markup=kb(ui.bypass_keyboard()),
        )
    elif action == "direct":
        proxies = get_all_proxies()
        lst = "\n".join(f"• <code>{p['host']}:{p['port']}</code> ({p.get('country','RU')})" for p in proxies[:10]) or "Список пуст — добавь прокси в proxies.json"
        await call.message.edit_text(
            "🇷🇺 <b>RU-айпишники (подключение напрямую):</b>\n"
            f"Авито, WB, Ozon, Max, Яндекс не пускают с VPN — к ним идёт прямое подключение.\n\n{lst}",
            reply_markup=kb(ui.bypass_keyboard()),
        )
    await call.answer()


async def main():
    init_db()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
