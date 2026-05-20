from pydantic import BaseModel, Field
from typing import Optional


class ProductResponse(BaseModel):
    id: int
    title: str
    product_type: str
    price: float
    payment_method: str
    source: str
    source_url: Optional[str] = None
    merchant: str = ""
    created_at: str
    updated_at: str


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int


class ProductSummary(BaseModel):
    product_type: str
    min_price: float
    max_price: float
    avg_price: float
    count: int
    sources: list[str]


class SourceResponse(BaseModel):
    name: str
    product_count: int
    last_update: Optional[str] = None
