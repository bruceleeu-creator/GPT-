import logging
import threading
import time
import schedule

from app.crud import upsert_product
from spiders.base import BaseSpider
from spiders.store_discovery import discover_new_stores, get_enabled_stores
from spiders.store_scraper import GenericStoreSpider
from spiders.telegram import TelegramSpider
from app.config import SCHEDULE_TIME


def _create_spider(store: dict) -> BaseSpider:
    if store.get("type") == "telegram":
        channel = store["domain"].replace("t.me/", "")
        return TelegramSpider(channel)
    return GenericStoreSpider(store["domain"], store["url"])


class SpiderScheduler:
    def __init__(self):
        self.spiders: list[BaseSpider] = []
        self._running = False
        self._crawling = threading.Event()

    def register(self, spider: BaseSpider):
        self.spiders.append(spider)

    def run_all(self):
        if self._crawling.is_set():
            logging.warning("Crawl already in progress, skipping")
            return
        self._crawling.set()
        logging.info("=== Scheduled crawl started ===")

        # 第一步：自动发现新站点和 TG 频道
        try:
            discover_new_stores()
            stores = get_enabled_stores()
            existing = {s.site_name for s in self.spiders}
            for store in stores:
                spider = _create_spider(store)
                if spider.site_name not in existing:
                    self.spiders.append(spider)
                    existing.add(spider.site_name)
            logging.info("[Discovery] 当前共 %d 个爬虫实例", len(self.spiders))
        except Exception as e:
            logging.error("[Discovery] 自动发现失败: %s", e)

        # 第二步：运行所有爬虫
        try:
            for spider in self.spiders:
                try:
                    results = spider.crawl()
                    count = 0
                    for item in results:
                        upsert_product(item)
                        count += 1
                    logging.info("[%s] Crawled %d products", spider.site_name, count)
                except Exception as e:
                    logging.error("[%s] Crawl failed: %s", spider.site_name, e)
        finally:
            self._crawling.clear()
        logging.info("=== Scheduled crawl finished ===")

    def start(self):
        schedule.every().day.at(SCHEDULE_TIME).do(self.run_all)

        def _loop():
            while self._running:
                schedule.run_pending()
                time.sleep(30)

        self._running = True
        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        logging.info("Scheduler started, next run at %s daily", SCHEDULE_TIME)

    def stop(self):
        self._running = False
