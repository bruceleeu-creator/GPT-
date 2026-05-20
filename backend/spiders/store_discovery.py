import json
import logging
import re
import urllib.parse
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from app.config import DATA_DIR

STORES_FILE = DATA_DIR / "discovered_stores.json"

SEARCH_KEYWORDS = [
    "GPT代充 自动发卡",
    "ChatGPT账号 购买 自动发货",
    "AI代充值 发卡平台",
    "Claude Pro 代充 下单",
    "Gemini 代购 发卡",
    "ChatGPT Plus 代充 网站",
    "GPT账号 自动发货 发卡",
]

TG_SEARCH_KEYWORDS = [
    "t.me GPT代充 频道",
    "t.me ChatGPT充值 代充",
    "Telegram AI代充 频道",
    "t.me Claude 代充",
    "t.me GPT账号 发卡",
]

# 已知噪音域名（搜索结果中常见的非发卡站）
NOISE_DOMAINS = {
    "baidu.com", "baijiahao.baidu.com", "fanyi.baidu.com", "image.baidu.com",
    "github.com", "play.google.com", "openai.com", "cloud.tencent.com",
    "weidian.com", "doc200.com", "mdnice.com", "955code.com",
    "zhuanwaifu.com", "19nd.com", "talktop.cn", "puhuajia.com",
    "speed4card.com", "ggem666.com", "tiebabaidu.com", "zhihu.com",
    "baike.baidu.com", "jingyan.baidu.com", "wenku.baidu.com",
    "map.baidu.com", "mbd.baidu.com",
}

SEARCH_ENGINES = {
    "baidu": {
        "url": "https://www.baidu.com/s?wd={keyword}&rn=20",
        "result_selector": "a[href*='baidu.com/link']",
        "link_attr": "href",
    },
}


def load_discovered_stores() -> list[dict]:
    if STORES_FILE.exists():
        return json.loads(STORES_FILE.read_text(encoding="utf-8"))
    return []


def save_discovered_stores(stores: list[dict]):
    STORES_FILE.parent.mkdir(parents=True, exist_ok=True)
    STORES_FILE.write_text(
        json.dumps(stores, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def discover_telegram_channels(headers: dict) -> list[str]:
    """通过搜索引擎发现 Telegram 代充频道"""
    known = load_discovered_stores()
    known_domains = {s["domain"] for s in known}
    new_channels = []

    for keyword in TG_SEARCH_KEYWORDS:
        try:
            url = SEARCH_ENGINES["baidu"]["url"].format(keyword=urllib.parse.quote(keyword))
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue

            # 从搜索结果中提取 t.me/xxx 模式
            tme_links = re.findall(r't\.me/([a-zA-Z0-9_]+)', resp.text)
            for ch in tme_links:
                ch = ch.strip()
                # 排除常见非频道路径
                if ch in ("s", "joinchat", "share", "login", "guide", "about"):
                    continue
                # 额外过滤噪音
                if any(n in ch.lower() for n in ("bot", "spam", "block", "support", "help", "news", "error")):
                    continue
                domain = f"t.me/{ch}"
                if domain not in known_domains:
                    new_channels.append(domain)
                    known_domains.add(domain)
                    known.append({
                        "domain": domain,
                        "url": f"https://t.me/s/{ch}",
                        "enabled": True,
                        "type": "telegram",
                    })
                    logging.info("[StoreDiscovery] 发现 TG 频道: %s", domain)
        except Exception as e:
            logging.warning("[StoreDiscovery] TG搜索 '%s' 失败: %s", keyword, e)
            continue

    if new_channels:
        save_discovered_stores(known)
    return new_channels


def discover_new_stores() -> list[str]:
    """通过搜索引擎发现新发卡站和 Telegram 频道"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    known = load_discovered_stores()
    known_domains = {s["domain"] for s in known}
    new_domains = set()

    # 发现发卡站
    for keyword in SEARCH_KEYWORDS:
        try:
            url = SEARCH_ENGINES["baidu"]["url"].format(keyword=urllib.parse.quote(keyword))
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            all_links = soup.find_all("a", href=re.compile(r"baidu\.com/link\?"))
            for link in all_links[:30]:
                full_url = _resolve_baidu_link(link["href"], headers)
                if full_url:
                    domain = urllib.parse.urlparse(full_url).netloc
                    if domain and domain not in known_domains:
                        new_domains.add((domain, full_url))
        except Exception as e:
            logging.warning("[StoreDiscovery] 搜索关键词 '%s' 失败: %s", keyword, e)
            continue

    for domain, url in new_domains:
        if domain in NOISE_DOMAINS:
            continue
        known_domains.add(domain)
        known.append({"domain": domain, "url": url, "enabled": True})
        logging.info("[StoreDiscovery] 发现新站点: %s", domain)

    # 发现 Telegram 频道
    tg_channels = discover_telegram_channels(headers)

    save_discovered_stores(known)
    return [d for d, _ in new_domains] + tg_channels


def _resolve_baidu_link(baidu_url: str, headers: dict) -> Optional[str]:
    """解析百度跳转链接获取真实URL"""
    try:
        resp = requests.get(baidu_url, headers=headers, timeout=10, allow_redirects=True)
        return resp.url if resp.status_code == 200 else None
    except Exception:
        return None


def get_enabled_stores() -> list[dict]:
    stores = load_discovered_stores()
    return [s for s in stores if s.get("enabled", True)]


# 无硬编码预置 — 所有站点通过自动发现获取
