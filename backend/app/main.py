from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import products, sources, stores
from spiders.scheduler import SpiderScheduler
from spiders.xianyu import XianyuSpider
from spiders.telegram import TelegramSpider
from spiders.store_scraper import GenericStoreSpider
from spiders.store_discovery import get_enabled_stores


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    scheduler = SpiderScheduler()
    scheduler.register(XianyuSpider())

    # 从发现列表加载已知站点（全自动发现，无硬编码）
    for store in get_enabled_stores():
        if store.get("type") == "telegram":
            channel = store["domain"].replace("t.me/", "")
            scheduler.register(TelegramSpider(channel))
        else:
            scheduler.register(GenericStoreSpider(store["domain"], store["url"]))

    scheduler.start()

    app.state.scheduler = scheduler
    yield
    scheduler.stop()


app = FastAPI(title="AI Price Comparison", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api")
app.include_router(sources.router, prefix="/api")
app.include_router(stores.router, prefix="/api")
