from typing import Optional
from app.database import get_connection, get_write_lock
from app.config import TARGET_PRODUCTS


def upsert_product(data: dict) -> int:
    lock = get_write_lock()
    with lock:
        conn = get_connection()
        cursor = conn.execute(
            """SELECT id FROM products
               WHERE title = ? AND source = ? AND (source_url = ? OR (? IS NULL AND source_url IS NULL))""",
            (data["title"], data["source"], data.get("source_url"), data.get("source_url")),
        )
        existing = cursor.fetchone()
        if existing:
            conn.execute(
                """UPDATE products
                   SET price = ?, payment_method = ?, merchant = ?, updated_at = datetime('now', 'localtime')
                   WHERE id = ?""",
                (data["price"], data["payment_method"], data.get("merchant", ""), existing["id"]),
            )
            product_id = existing["id"]
        else:
            cursor = conn.execute(
                """INSERT INTO products (title, product_type, price, payment_method, source, source_url, merchant)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["title"],
                    data["product_type"],
                    data["price"],
                    data["payment_method"],
                    data["source"],
                    data.get("source_url"),
                    data.get("merchant", ""),
                ),
            )
            product_id = cursor.lastrowid
        conn.commit()
        return product_id


def get_products(
    product_type: Optional[str] = None,
    payment_method: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    conn = get_connection()
    conditions = []
    params = []

    if product_type and product_type != "全部":
        conditions.append("product_type = ?")
        params.append(product_type)
    if payment_method and payment_method != "全部":
        conditions.append("payment_method = ?")
        params.append(payment_method)
    if source and source != "全部":
        conditions.append("source = ?")
        params.append(source)
    if search:
        conditions.append("title LIKE ?")
        params.append(f"%{search}%")

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    sort_by = sort_by if sort_by in ("price", "created_at", "updated_at") else "updated_at"
    sort_order = "ASC" if sort_order.lower() == "asc" else "DESC"

    count_row = conn.execute(f"SELECT COUNT(*) as cnt FROM products {where}", params).fetchone()
    total = count_row["cnt"] if count_row else 0

    offset = (page - 1) * page_size
    rows = conn.execute(
        f"SELECT * FROM products {where} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?",
        params + [page_size, offset],
    ).fetchall()

    items = [dict(row) for row in rows]
    return items, total


def get_product_summary(product_type: Optional[str] = None) -> list[dict]:
    conn = get_connection()
    conditions = []
    params = []
    if product_type and product_type != "全部":
        conditions.append("p.product_type = ?")
        params.append(product_type)
    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    rows = conn.execute(
        f"""SELECT p.product_type,
                   MIN(p.price) as min_price,
                   MAX(p.price) as max_price,
                   ROUND(AVG(p.price), 2) as avg_price,
                   COUNT(*) as count,
                   GROUP_CONCAT(DISTINCT p.source) as sources_str
            FROM products p
            {where}
            GROUP BY p.product_type
            ORDER BY p.product_type""",
        params,
    ).fetchall()

    result = []
    for row in rows:
        d = dict(row)
        d["sources"] = d["sources_str"].split(",") if d["sources_str"] else []
        del d["sources_str"]
        result.append(d)
    return result


def get_sources() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT source as name,
                  COUNT(*) as product_count,
                  MAX(updated_at) as last_update
           FROM products
           GROUP BY source
           ORDER BY source"""
    ).fetchall()
    return [dict(row) for row in rows]


def clear_products():
    lock = get_write_lock()
    with lock:
        conn = get_connection()
        conn.execute("DELETE FROM products")
        conn.commit()
