import sqlite3
import threading
from app.config import DB_PATH, DATA_DIR

_local = threading.local()
_lock = threading.Lock()

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    product_type TEXT NOT NULL,
    price REAL NOT NULL,
    payment_method TEXT NOT NULL DEFAULT '其他',
    source TEXT NOT NULL,
    source_url TEXT,
    merchant TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""

INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_product_type ON products(product_type);",
    "CREATE INDEX IF NOT EXISTS idx_source ON products(source);",
    "CREATE INDEX IF NOT EXISTS idx_updated_at ON products(updated_at);",
]


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    conn.execute(CREATE_TABLE_SQL)
    for idx in INDEXES_SQL:
        conn.execute(idx)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.commit()


def get_connection() -> sqlite3.Connection:
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(DB_PATH)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL;")
    return _local.conn


def get_write_lock() -> threading.Lock:
    return _lock
