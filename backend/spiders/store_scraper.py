import logging
import re
import urllib.parse
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from spiders.base import BaseSpider
from spiders.utils import is_target_product, clean_price, detect_payment_method, normalize_product_type
from app.config import TIMEOUT


PRICE_PATTERNS = re.compile(
    r"(?:¥|Â¥|￥|价格|价|仅[售卖]?)\s*(\d+\.?\d*)",
    re.IGNORECASE,
)

PRODUCT_KEYWORDS = [
    "GPT", "ChatGPT", "Claude", "Gemini", "Grok",
    "AI", "Plus", "Pro", "会员", "账号", "代充", "代购",
    "成品号", "共享", "独享", "卡密", "订阅",
]


def is_store_page(soup: BeautifulSoup) -> bool:
    """判断页面是否可能包含商品列表"""
    text = soup.get_text()
    price_hints = len(PRICE_PATTERNS.findall(text))
    product_hints = sum(1 for kw in PRODUCT_KEYWORDS if kw.lower() in text.lower())
    return price_hints >= 1 and product_hints >= 1


def extract_prices(text: str) -> List[float]:
    """从文本中提取所有价格"""
    return [
        float(m) for m in PRICE_PATTERNS.findall(text)
        if 0.1 < float(m) < 99999
    ]


def find_product_cards(soup: BeautifulSoup) -> List[dict]:
    """通过多种策略寻找页面中的商品卡片"""
    found = []

    # 策略1: article 元素（常见于 landing page 式发卡站）
    for article in soup.find_all("article"):
        text = article.get_text(strip=True)
        prices = extract_prices(text)
        if not prices:
            continue
        title_el = article.find(["h3", "h4", "h2", "strong"])
        title = title_el.get_text(strip=True) if title_el else text[:120]
        found.append({"title": title, "price": prices[0], "el": article})

    if found:
        return found

    # 策略2: 查找含 price 类的容器 + 附近标题
    for price_el in soup.select("[class*=price], [class*=Price]"):
        text = price_el.get_text(strip=True)
        prices = extract_prices(text)
        if not prices:
            continue
        card = price_el.find_parent(["div", "li", "article"])
        if not card:
            continue
        title_el = card.find(["h3", "h4", "h2", "strong", "a"])
        if not title_el:
            title_el = card.find(["div", "p"], class_=re.compile(r"name|title|tt|nm", re.I))
        title = title_el.get_text(strip=True)[:120] if title_el else card.get_text(strip=True)[:120]
        found.append({"title": title, "price": prices[0], "el": card})

    if found:
        return found

    # 策略3: 常见的发卡站商品容器
    for selector in [
        "div.goods-item", "div.product-item", "div.commodity",
        "tr.goods-tr", "li.goods-li", "div.prod-item",
        "div.card-item", "div[class*='goods']", "div[class*='product']",
        "div[class*='commodity']", "div[class*='card']",
    ]:
        cards = soup.select(selector)
        if len(cards) >= 2:
            for card in cards:
                text = card.get_text(strip=True)
                prices = extract_prices(text)
                if prices:
                    title_el = card.find(["a", "h3", "h4", "div", "span"],
                                         class_=re.compile(r"name|title|tt|nm", re.I))
                    if not title_el:
                        title_el = card.find("a")
                    title = (title_el.get_text(strip=True)[:120] if title_el
                             else text[:120])
                    found.append({"title": title, "price": prices[0], "el": card})
            if found:
                return found

    # 策略4: 查找表格行
    rows = soup.select("table tr")
    if len(rows) >= 3:
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                text = row.get_text(strip=True)
                prices = extract_prices(text)
                if prices:
                    title_cell = cells[0].get_text(strip=True)[:120]
                    found.append({"title": title_cell, "price": prices[0], "el": row})
        if found:
            return found

    # 策略5: 搜索所有含价格的目标商品文本（兜底）
    for tag in ["div", "li", "section", "article"]:
        for el in soup.find_all(tag):
            text = el.get_text(strip=True)
            prices = extract_prices(text)
            if prices and is_target_product(text):
                title = text[:120]
                if title not in {f["title"] for f in found}:
                    found.append({"title": title, "price": prices[0], "el": el})
        if len(found) >= 3:
            return found

    return found


class GenericStoreSpider(BaseSpider):
    """通用发卡站爬虫，自动适配不同站点结构"""

    def __init__(self, domain: str, url: str, name: Optional[str] = None):
        super().__init__(name or domain, url)

    def crawl(self) -> List[dict]:
        try:
            html = self.get_page(self.base_url)
            if not html:
                return []

            soup = BeautifulSoup(html, "lxml")

            if not is_store_page(soup):
                logging.info("[%s] 页面不包含商品信息，跳过", self.site_name)
                return []

            cards = find_product_cards(soup)
            results = []
            seen = set()

            for card in cards[:30]:
                title = card["title"]
                if not title or title in seen:
                    continue
                seen.add(title)

                if not is_target_product(title):
                    continue

                price = card["price"]
                result = self.parse_product({
                    "title": title,
                    "price_str": str(price),
                    "url": self.base_url,
                    "merchant": self.site_name,
                })
                result["price"] = price
                results.append(result)

            logging.info("[%s] 提取到 %d 个商品", self.site_name, len(results))
            return results

        except Exception as e:
            logging.error("[%s] 爬取失败: %s", self.site_name, e)
            return []
