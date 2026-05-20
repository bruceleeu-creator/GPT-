import re
import os
import logging
from typing import List

from bs4 import BeautifulSoup

from spiders.base import BaseSpider
from spiders.utils import is_target_product

PRICE_PATTERNS = [
    r"¥\s*(\d+\.?\d*)",
    r"价格[：:]\s*(\d+\.?\d*)",
    r"(\d+\.?\d*)\s*元",
    r"(\d+\.?\d*)\s*/月",
]


class TelegramSpider(BaseSpider):
    def __init__(self, channel: str):
        super().__init__(f"TG:{channel}", "https://t.me")
        self.channel = channel

    def crawl(self) -> List[dict]:
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if not proxy:
            logging.warning("[Telegram] 未检测到代理配置，跳过爬取（设置 https_proxy 环境变量即可启用）")
            return []

        return self._scrape_channel(self.channel)

    def _scrape_channel(self, channel: str) -> List[dict]:
        url = f"https://t.me/s/{channel}"
        html = self.get_page(url, delay=(5, 10))
        if not html:
            return []

        if "tgme_channel_not_found" in html:
            logging.warning("[Telegram] Channel '%s' 不存在", channel)
            return []

        soup = BeautifulSoup(html, "lxml")
        messages = soup.find_all("div", class_="tgme_widget_message_wrap")
        items = []
        for msg in messages[:50]:
            try:
                text_el = msg.find("div", class_="tgme_widget_message_text")
                if not text_el:
                    continue
                text = text_el.get_text(strip=True)
                if not is_target_product(text):
                    continue

                price_str = self._extract_price(text)
                link_el = msg.find("a", class_="tgme_widget_message_date", href=True)
                msg_url = link_el["href"] if link_el else url

                items.append(self.parse_product({
                    "title": text[:80],
                    "price_str": price_str,
                    "url": msg_url,
                    "merchant": channel,
                }))
            except Exception as e:
                logging.warning("[Telegram] Parse message failed: %s", e)
                continue
        return items

    @staticmethod
    def _extract_price(text: str) -> str:
        for pattern in PRICE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""
