"""
database.py — SQLite database setup and models for TrendVault
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/trendvault.db")


def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            slug        TEXT UNIQUE NOT NULL,
            description TEXT,
            short_desc  TEXT,
            price       REAL NOT NULL,
            compare_price REAL,
            images      TEXT DEFAULT '[]',
            category    TEXT DEFAULT 'General',
            tags        TEXT DEFAULT '[]',
            rating      REAL DEFAULT 0,
            orders_count INTEGER DEFAULT 0,
            supplier_url TEXT,
            sku         TEXT,
            stock       INTEGER DEFAULT 999,
            active      INTEGER DEFAULT 1,
            featured    INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS orders (
            id            TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            items         TEXT NOT NULL,
            subtotal      REAL NOT NULL,
            shipping      REAL DEFAULT 0,
            total         REAL NOT NULL,
            status        TEXT DEFAULT 'pending',
            payment_intent TEXT,
            created_at    TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id         TEXT PRIMARY KEY,
            cart       TEXT DEFAULT '{}',
            updated_at TEXT DEFAULT (datetime('now'))
        );
    """)

    conn.commit()
    conn.close()


def _slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:80]


def upsert_product(p: dict) -> bool:
    conn = get_db()
    c = conn.cursor()

    slug = _slugify(p.get("title", p["id"]))
    base_slug = slug
    i = 1
    while True:
        existing = c.execute("SELECT id FROM products WHERE slug=? AND id!=?", (slug, p["id"])).fetchone()
        if not existing:
            break
        slug = f"{base_slug}-{i}"
        i += 1

    ai = p.get("ai", {})
    ai_prod = ai.get("product", {})
    title = ai_prod.get("optimised_title", p["title"])
    description = ai_prod.get("html_description", p.get("title", ""))
    short_desc = ai_prod.get("short_description", "")
    tags = json.dumps(ai_prod.get("tags", []))
    category = ai_prod.get("product_type", p.get("category", "General"))
    images = json.dumps(p.get("image_urls", []))

    existing_row = c.execute("SELECT id FROM products WHERE id=?", (p["id"],)).fetchone()

    if existing_row:
        c.execute("""
            UPDATE products SET title=?, slug=?, description=?, short_desc=?,
            price=?, compare_price=?, images=?, category=?, tags=?,
            rating=?, orders_count=?, supplier_url=?, sku=?, active=1
            WHERE id=?
        """, (title, slug, description, short_desc, p["sale_price"],
              p.get("original_price", p["sale_price"] * 1.3),
              images, category, tags, p.get("rating", 0), p.get("orders", 0),
              p.get("product_url", ""), f"DS-{p['id']}", p["id"]))
        conn.commit()
        conn.close()
        return False
    else:
        c.execute("""
            INSERT INTO products
            (id, title, slug, description, short_desc, price, compare_price,
             images, category, tags, rating, orders_count, supplier_url, sku)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (p["id"], title, slug, description, short_desc, p["sale_price"],
              p.get("original_price", p["sale_price"] * 1.3),
              images, category, tags, p.get("rating", 0), p.get("orders", 0),
              p.get("product_url", ""), f"DS-{p['id']}"))
        conn.commit()
        conn.close()
        return True


def get_products(category=None, search=None, featured_only=False, limit=60, offset=0):
    conn = get_db()
    c = conn.cursor()
    query = "SELECT * FROM products WHERE active=1"
    params = []
    if category:
        query += " AND category=?"
        params.append(category)
    if search:
        query += " AND (title LIKE ? OR short_desc LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if featured_only:
        query += " AND featured=1"
    query += " ORDER BY featured DESC, created_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]
    rows = c.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_product_by_slug(slug: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM products WHERE slug=? AND active=1", (slug,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_product_by_id(pid: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_categories():
    conn = get_db()
    rows = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM products WHERE active=1 GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return [{"name": r["category"], "count": r["cnt"]} for r in rows]


def set_featured(product_id: str, featured: bool):
    conn = get_db()
    conn.execute("UPDATE products SET featured=? WHERE id=?", (1 if featured else 0, product_id))
    conn.commit()
    conn.close()


def _row_to_dict(row) -> dict:
    if not row:
        return {}
    d = dict(row)
    for key in ("images", "tags"):
        try:
            d[key] = json.loads(d.get(key, "[]"))
        except Exception:
            d[key] = []
    return d


def create_order(order_data: dict) -> str:
    import uuid
    order_id = str(uuid.uuid4())[:8].upper()
    conn = get_db()
    conn.execute("""
        INSERT INTO orders
        (id, customer_name, customer_email, customer_address, items,
         subtotal, shipping, total, status, payment_intent)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        order_id,
        order_data["customer_name"],
        order_data["customer_email"],
        order_data["customer_address"],
        json.dumps(order_data["items"]),
        order_data["subtotal"],
        order_data.get("shipping", 0),
        order_data["total"],
        order_data.get("status", "pending"),
        order_data.get("payment_intent", ""),
    ))
    conn.commit()
    conn.close()
    return order_id


def get_order(order_id: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["items"] = json.loads(d.get("items", "[]"))
    try:
        d["customer_address"] = json.loads(d.get("customer_address", "{}"))
    except Exception:
        d["customer_address"] = {}
    return d


def update_order_status(order_id: str, status: str):
    conn = get_db()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()


def get_all_orders(limit=100):
    conn = get_db()
    rows = conn.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    orders = []
    for row in rows:
        d = dict(row)
        try:
            d["items"] = json.loads(d.get("items", "[]"))
        except Exception:
            d["items"] = []
        orders.append(d)
    return orders


def get_stats():
    conn = get_db()
    c = conn.cursor()
    products = c.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0]
    orders = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    revenue = c.execute("SELECT SUM(total) FROM orders WHERE status='paid'").fetchone()[0] or 0
    pending = c.execute("SELECT COUNT(*) FROM orders WHERE status='pending'").fetchone()[0]
    conn.close()
    return {
        "products": products,
        "orders": orders,
        "revenue": round(revenue, 2),
        "pending_orders": pending,
    }
