from fastapi import APIRouter
from app.crud import upsert_product
from spiders.store_discovery import discover_new_stores, get_enabled_stores, load_discovered_stores
from spiders.store_scraper import GenericStoreSpider
from spiders.telegram import TelegramSpider

router = APIRouter(tags=["stores"])


def _create_spider(store: dict):
    if store.get("type") == "telegram":
        channel = store["domain"].replace("t.me/", "")
        return TelegramSpider(channel)
    return GenericStoreSpider(store["domain"], store["url"])


@router.get("/stores")
def list_stores():
    stores = load_discovered_stores()
    return [
        {
            "domain": s["domain"],
            "url": s["url"],
            "enabled": s.get("enabled", True),
            "type": s.get("type", "website"),
        }
        for s in stores
    ]


@router.post("/stores/discover")
def discover_stores():
    new_count = 0
    product_count = 0
    tg_count = 0

    new_domains = discover_new_stores()
    if new_domains:
        new_count = len(new_domains)

    stores = get_enabled_stores()
    for store in stores:
        try:
            spider = _create_spider(store)
            results = spider.crawl()
            for item in results:
                upsert_product(item)
            product_count += len(results)
            if store.get("type") == "telegram" and results:
                tg_count += 1
        except Exception:
            continue

    return {
        "status": "ok",
        "new_stores": new_count,
        "total_stores": len(stores),
        "telegram_channels": len([s for s in stores if s.get("type") == "telegram"]),
        "products_found": product_count,
    }


@router.post("/stores/scrape-all")
def scrape_all():
    product_count = 0
    stores = get_enabled_stores()
    for store in stores:
        try:
            spider = _create_spider(store)
            results = spider.crawl()
            for item in results:
                upsert_product(item)
            product_count += len(results)
        except Exception:
            continue

    return {
        "status": "ok",
        "stores_scraped": len(stores),
        "products_found": product_count,
    }
