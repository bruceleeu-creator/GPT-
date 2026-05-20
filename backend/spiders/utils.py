import re
from app.config import TARGET_PRODUCTS, PAYMENT_METHODS


def clean_price(price_str: str) -> float:
    if not price_str:
        return 9999.99
    cleaned = re.sub(r'[^\d.]', "", price_str)
    if not cleaned:
        return 9999.99
    try:
        return float(cleaned)
    except ValueError:
        return 9999.99


def detect_payment_method(description: str) -> str:
    if not description:
        return "其他"
    lower_desc = description.lower()
    for method, keywords in PAYMENT_METHODS.items():
        for keyword in keywords:
            if keyword in lower_desc:
                return method
    return "其他"


def is_target_product(title: str) -> bool:
    if not title:
        return False
    for product in TARGET_PRODUCTS:
        if product.lower() in title.lower():
            return True
    return False


def normalize_product_type(title: str) -> str:
    if not title:
        return "其他"
    lower_title = title.lower()
    for product in TARGET_PRODUCTS:
        if product.lower() in lower_title:
            return product
    return "其他"
