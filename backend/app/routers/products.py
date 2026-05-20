import threading
from typing import Optional
from fastapi import APIRouter, Query, Request
from app.models import ProductResponse, ProductListResponse, ProductSummary
from app.crud import get_products, get_product_summary
from app.config import TARGET_PRODUCTS

router = APIRouter(tags=["products"])


@router.get("/products/types")
def list_product_types():
    return TARGET_PRODUCTS


@router.get("/products", response_model=ProductListResponse)
def list_products(
    product_type: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("updated_at", pattern="^(price|created_at|updated_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = get_products(
        product_type=product_type,
        payment_method=payment_method,
        source=source,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/products/summary", response_model=list[ProductSummary])
def products_summary(product_type: Optional[str] = Query(None)):
    return get_product_summary(product_type=product_type)


@router.post("/products/refresh")
def refresh_products(request: Request):
    scheduler = request.app.state.scheduler
    thread = threading.Thread(target=scheduler.run_all, daemon=True)
    thread.start()
    return {"status": "ok", "message": "数据刷新已开始，请在后台运行"}
