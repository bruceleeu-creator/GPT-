import logging
import urllib.parse
from typing import List

from bs4 import BeautifulSoup

from spiders.base import BaseSpider
from spiders.utils import is_target_product

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


class XianyuSpider(BaseSpider):
    SEARCH_URL = "https://www.goofish.com/search"

    def __init__(self):
        super().__init__("闲鱼", "https://www.goofish.com")

    def crawl(self) -> List[dict]:
        keywords = ["GPT代充", "ChatGPT账号", "Claude代充", "Gemini", "Grok", "GPT账号"]
        all_items = []

        # 尝试方式1: Playwright 浏览器自动化
        if HAS_PLAYWRIGHT:
            try:
                items = self._crawl_via_playwright(keywords)
                if items:
                    return items
            except Exception as e:
                logging.warning("[闲鱼] Playwright 方式失败: %s", e)

        # 尝试方式2: 直接 HTTP 请求
        logging.info("[闲鱼] 尝试 HTTP 方式爬取")
        for keyword in keywords:
            try:
                items = self._search_keyword_http(keyword)
                all_items.extend(items)
            except Exception as e:
                logging.warning("[闲鱼] HTTP 关键词 '%s' 失败: %s", keyword, e)

        if not all_items:
            logging.warning("[闲鱼] 所有爬取方式均失败（闲鱼反爬严格，需要登录环境）")
            logging.warning("[闲鱼] 如需闲鱼数据，可配置真实 Cookie 或使用其他渠道替代")
        return all_items

    def _crawl_via_playwright(self, keywords: List[str]) -> List[dict]:
        """通过 Playwright 浏览器自动化爬取（需要登录环境）"""
        all_items = []
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = browser.new_context(
                locale="zh-CN",
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
            )
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            for keyword in keywords:
                try:
                    page = context.new_page()
                    url = f"{self.SEARCH_URL}?q={urllib.parse.quote(keyword)}"
                    page.goto(url, timeout=20000, wait_until="domcontentloaded")
                    page.wait_for_timeout(3000)

                    if "登录" in page.inner_text("body")[:200]:
                        page.close()
                        continue

                    cards = page.query_selector_all('[class*="item"], a[href*="item.goofish"]')
                    for card in cards[:20]:
                        try:
                            title = card.inner_text().strip()
                            if not title or not is_target_product(title):
                                continue
                            link = card.get_attribute("href") or ""
                            full_url = urllib.parse.urljoin(self.base_url, link) if link else ""
                            all_items.append(self.parse_product({
                                "title": title,
                                "price_str": "",
                                "url": full_url,
                                "merchant": "",
                            }))
                        except Exception:
                            continue
                    page.close()
                except Exception as e:
                    logging.warning("[闲鱼] Playwright 关键词 '%s' 失败: %s", keyword, e)

            browser.close()
        return all_items

    def _search_keyword_http(self, keyword: str) -> List[dict]:
        """HTTP 方式爬取（用于降级兜底）"""
        params = {"q": keyword, "source": "search"}
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        html = self.get_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        cards = soup.find_all("div", class_="item") or soup.find_all("a", href=lambda h: h and "item.goofish" in h)
        items = []
        for card in cards[:20]:
            try:
                title = card.get_text(strip=True)
                if not title or not is_target_product(title):
                    continue
                link = card.get("href") if isinstance(card, dict) else ""
                full_url = urllib.parse.urljoin(self.base_url, link) if link else ""
                items.append(self.parse_product({
                    "title": title,
                    "price_str": "",
                    "url": full_url,
                    "merchant": "",
                }))
            except Exception:
                continue
        return items
