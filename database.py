# -*- coding: utf-8 -*-
"""Хранилище данных (SQLite) для бота GLEBSBP."""

import sqlite3
import datetime
from config import DB_PATH


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            subscribed_channel INTEGER DEFAULT 0,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tariff TEXT,
            paid_amount INTEGER,
            activated_at TEXT,
            expires_at TEXT
        );
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            details TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT,
            port INTEGER,
            login TEXT,
            password TEXT,
            proxy_type TEXT DEFAULT 'http',
            country TEXT DEFAULT 'RU',
            enabled INTEGER DEFAULT 1
        );
        """)


def upsert_user(user_id, username, first_name):
    now = datetime.datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute(
            "INSERT INTO users(user_id, username, first_name, created_at) VALUES(?,?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET username=?, first_name=?",
            (user_id, username, first_name, now, username, first_name),
        )


def add_log(user_id, action, details=""):
    now = datetime.datetime.utcnow().isoformat()
    with _conn() as c:
        c.execute(
            "INSERT INTO logs(user_id, action, details, created_at) VALUES(?,?,?,?)",
            (user_id, action, details, now),
        )


def get_logs(user_id, limit=20):
    with _conn() as c:
        rows = c.execute(
            "SELECT action, details, created_at FROM logs WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def activate_subscription(user_id, tariff, days, price):
    now = datetime.datetime.utcnow()
    # продлеваем от текущей активной подписки, если есть
    with _conn() as c:
        last = c.execute(
            "SELECT expires_at FROM subscriptions WHERE user_id=? AND expires_at>? ORDER BY expires_at DESC LIMIT 1",
            (user_id, now.isoformat()),
        ).fetchone()
        base = datetime.datetime.fromisoformat(last["expires_at"]) if last else now
        expires = base + datetime.timedelta(days=days)
        c.execute(
            "INSERT INTO subscriptions(user_id, tariff, paid_amount, activated_at, expires_at) VALUES(?,?,?,?,?)",
            (user_id, tariff, price, now.isoformat(), expires.isoformat()),
        )
    return expires


def get_subscription(user_id):
    now = datetime.datetime.utcnow().isoformat()
    with _conn() as c:
        row = c.execute(
            "SELECT tariff, expires_at FROM subscriptions WHERE user_id=? AND expires_at>? ORDER BY expires_at DESC LIMIT 1",
            (user_id, now),
        ).fetchone()
    return dict(row) if row else None


def get_all_proxies():
    with _conn() as c:
        rows = c.execute("SELECT * FROM proxies WHERE enabled=1").fetchall()
    return [dict(r) for r in rows]
