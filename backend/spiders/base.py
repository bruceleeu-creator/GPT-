import os
import time
import random
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

import requests

from app.config import REQUEST_DELAY, TIMEOUT
from spiders.utils import clean_price, detect_payment_method, normalize_product_type


class BaseSpider(ABC):
    def __init__(self, site_name: str, base_url: str = ""):
        self.site_name = site_name
        self.base_url = base_url
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
            logging.info("[%s] Using proxy: %s", self.site_name, proxy)
        return session

    def get_page(self, url: str, delay: Optional[tuple] = None) -> str:
        delay = delay or REQUEST_DELAY
        time.sleep(random.uniform(*delay))
        try:
            resp = self.session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return resp.text
        except Exception as e:
            logging.error("[%s] Failed to fetch %s: %s", self.site_name, url, e)
            return ""

    @abstractmethod
    def crawl(self) -> List[dict]:
        ...

    def parse_product(self, raw: dict) -> dict:
        title = raw.get("title", "")
        return {
            "title": title,
            "product_type": normalize_product_type(title),
            "price": clean_price(raw.get("price_str", "")),
            "payment_method": detect_payment_method(title),
            "source": self.site_name,
            "source_url": raw.get("url", ""),
            "merchant": raw.get("merchant", ""),
        }
