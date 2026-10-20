# -*- coding: utf-8 -*-
"""
Модуль обхода блокировок (вкладка \"Обход\").

Логика:
 - Есть список российских прокси/айпи, которые НЕ пускают при подключении через VPN
   (авито, вб, озон, макс, яндекс и т.д.) — к ним подключаемся НАПРЯМУЮ, без прокси.
 - Остальные ресурсы обходятся через резидентные RU-прокси из proxies.json / БД.
"""

import json
import socket
import urllib.request
from config import DEFAULT_PROXIES_FILE

# Домены, которые блокируют VPN-трафик — идём к ним напрямую
DIRECT_ONLY_DOMAINS = [
    "avito.ru",
    "www.avito.ru",
    "wb.ru",
    "www.wb.ru",
    "wildberries.ru",
    "ozon.ru",
    "www.ozon.ru",
    "max.gov.ru",          # Госуслуги Max
    "max.ru",
    "yandex.ru",
    "www.yandex.ru",
    "ya.ru",
    "yandex.net",
    "sberbank.ru",
    "sber.ru",
    "vk.com",
    "gmail.com",           # пример ресурса с проверкой региона
]


def is_direct_only(target: str) -> bool:
    """Проверяет, нужно ли подключаться к цели напрямую (без прокси)."""
    target = target.lower().replace("https://", "").replace("http://", "")
    host = target.split("/")[0]
    return any(host == d or host.endswith("." + d) for d in DIRECT_ONLY_DOMAINS)


def load_proxies(path=DEFAULT_PROXIES_FILE):
    """Загружает список RU-прокси из файла вида [{host, port, login, password}, ...]."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def proxy_url(p: dict) -> str:
    login = p.get("login")
    pwd = p.get("password")
    proto = p.get("proxy_type", "http")
    auth = f"{login}:{pwd}@" if login and pwd else ""
    return f"{proto}://{auth}{p['host']}:{p['port']}"


def check_connectivity(target: str, timeout: float = 5.0) -> dict:
    """
    Пингует цель. Если домен из списка direct-only — проверяем прямое соединение.
    Иначе пробуем через прокси.
    """
    result = {"target": target, "mode": "direct" if is_direct_only(target) else "proxy", "ok": False}
    host = target.replace("https://", "").replace("http://", "").split("/")[0]
    port = 443
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        result["ok"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def fetch(target: str, proxies: list | None = None, timeout: float = 10.0) -> str:
    """Загружает страницу: напрямую для direct-only, иначе через первый рабочий прокси."""
    req = urllib.request.Request(target, headers={"User-Agent": "Mozilla/5.0"})
    if is_direct_only(target):
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "ignore")
    for p in (proxies or load_proxies()):
        try:
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({"http": proxy_url(p), "https": proxy_url(p)})
            )
            with opener.open(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception:
            continue
    raise RuntimeError("Не удалось подключиться ни напрямую, ни через прокси")
