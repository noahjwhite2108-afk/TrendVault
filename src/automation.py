"""
automation.py — TrendVault background automation
"""

import json
import logging
import random
import time
import re
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional

import database as db

logger = logging.getLogger(__name__)


def calculate_sale_price(supplier_price: float, config: Dict) -> float:
    disc = config["product_discovery"]
    markup = disc.get("markup_multiplier", 2.8)
    shipping = disc.get("shipping_buffer_usd", 3.0)
    raw = (supplier_price + shipping) * markup
    if config.get("pricing_strategy", {}).get("round_to_99", True):
        return round(raw) - 0.01 if raw >= 1 else raw
    return round(raw, 2)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/605.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
]

SAMPLE_PRODUCTS = [
    {"title": "Portable LED Ring Light 10\" with Flexible Phone Holder", "supplier_price": 8.99, "rating": 4.7, "orders": 12500, "category": "Photography"},
    {"title": "Magnetic Car Phone Mount Dashboard 360° Rotation", "supplier_price": 4.50, "rating": 4.6, "orders": 8900, "category": "Car Accessories"},
    {"title": "Stainless Steel Garlic Press Crusher Mincer Kitchen Tool", "supplier_price": 5.20, "rating": 4.8, "orders": 6700, "category": "Kitchen"},
    {"title": "Resistance Bands Set 5-Pack Exercise Workout Elastic", "supplier_price": 7.30, "rating": 4.7, "orders": 15000, "category": "Fitness"},
    {"title": "Reusable Silicone Food Storage Bags Set of 5", "supplier_price": 6.80, "rating": 4.5, "orders": 9200, "category": "Kitchen"},
    {"title": "USB-C Fast Charging Cable 3-Pack Braided Nylon 6ft", "supplier_price": 5.50, "rating": 4.6, "orders": 22000, "category": "Tech"},
    {"title": "Posture Corrector Back Brace Adjustable Support Belt", "supplier_price": 9.20, "rating": 4.5, "orders": 7800, "category": "Health"},
    {"title": "Bamboo Drawer Organizer Set Expandable Dividers", "supplier_price": 12.00, "rating": 4.7, "orders": 5400, "category": "Home"},
    {"title": "Electric Scalp Massager Waterproof Shampoo Brush", "supplier_price": 7.80, "rating": 4.6, "orders": 11200, "category": "Beauty"},
    {"title": "Collapsible Water Bottle BPA-Free Foldable Flask", "supplier_price": 6.40, "rating": 4.5, "orders": 9600, "category": "Outdoor"},
    {"title": "LED Strip Lights 32.8ft RGB Color Changing with Remote", "supplier_price": 11.00, "rating": 4.7, "orders": 18500, "category": "Home"},
    {"title": "Wireless Earbuds Bluetooth 5.3 Deep Bass TWS", "supplier_price": 14.50, "rating": 4.6, "orders": 32000, "category": "Tech"},
]


def scrape_aliexpress(keyword: str, limit: int, min_rating: float, min_orders: int) -> List[Dict]:
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Referer": "https://www.aliexpress.com/",
    })
    try:
        url = "https://www.aliexpress.com/glosearch/api/product"
        params = {"keywords": keyword, "sortType": "total_tranpro_desc", "page": 1,
                  "pageSize": min(limit * 3, 60), "locale": "en_US", "currency": "USD"}
        resp = session.get(url, params=params, timeout=12)
        data = resp.json()
        items = data.get("mods", {}).get("itemList", {}).get("content", [])
    except Exception as e:
        logger.debug(f"Scraper failed for '{keyword}': {e}")
        return _get_sample_products(keyword, limit)

    products = []
    for item in items:
        try:
            price_info = item.get("prices", {})
            supplier_price = float(price_info.get("salePrice", {}).get("minPrice", 0))
            if supplier_price <= 0 or supplier_price > 30:
                continue
            rating = float(item.get("evaluation", {}).get("starRating", 0))
            if rating < min_rating:
                continue
            orders_str = item.get("trade", {}).get("tradeDesc", "0")
            orders = _parse_orders(orders_str)
            if orders < min_orders:
                continue
            img = item.get("image", {}).get("imgUrl", "")
            if img and not img.startswith("http"):
                img = "https:" + img
            products.append({
                "id": hashlib.md5(str(item.get("productId", "")).encode()).hexdigest()[:12],
                "title": item.get("title", {}).get("displayTitle", "Product"),
                "supplier_price": supplier_price,
                "sale_price": 0,
                "original_price": float(price_info.get("originalPrice", {}).get("minPrice", supplier_price * 1.3)),
                "rating": rating,
                "orders": orders,
                "image_urls": [img] if img else [],
                "product_url": f"https://www.aliexpress.com/item/{item.get('productId','')}.html",
                "category": keyword.title()[:30],
            })
            if len(products) >= limit:
                break
        except Exception:
            continue
    return products if products else _get_sample_products(keyword, limit)


def _parse_orders(text: str) -> int:
    text = str(text).lower().replace(",", "").replace("+", "")
    if "k" in text:
        try:
            return int(float(re.sub(r"[^0-9.]", "", text.replace("k", ""))) * 1000)
        except Exception:
            return 0
    try:
        return int("".join(filter(str.isdigit, text.split()[0])))
    except Exception:
        return 0


def _get_sample_products(keyword: str, limit: int) -> List[Dict]:
    products = []
    for i, s in enumerate(SAMPLE_PRODUCTS[:limit]):
        products.append({
            "id": hashlib.md5(f"{s['title']}{i}".encode()).hexdigest()[:12],
            "title": s["title"],
            "supplier_price": s["supplier_price"],
            "sale_price": 0,
            "original_price": round(s["supplier_price"] * 1.35, 2),
            "rating": s["rating"],
            "orders": s["orders"],
            "image_urls": [],
            "product_url": "https://www.aliexpress.com",
            "category": s.get("category", keyword.title()),
        })
    return products


def _ai_enrich(product: Dict, config: Dict) -> Dict:
    api_key = config.get("ai", {}).get("api_key", "YOUR_GEMINI_API_KEY")
    if api_key == "YOUR_GEMINI_API_KEY":
        return _template_enrich(product)
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(config["ai"].get("model", "gemini-1.5-flash"))
        prompt = f"""You are an expert e-commerce copywriter.
Product: {product['title']}
Sale price: ${product['sale_price']}
Category: {product['category']}
Rating: {product['rating']}/5 ({product['orders']}+ sold)
Generate a product listing as JSON with keys: optimised_title, short_description, html_description, meta_description, tags (list), product_type.
Respond ONLY with the JSON."""
        response = model.generate_content(prompt)
        text = re.sub(r"```json\s*|```\s*", "", response.text.strip())
        ai_data = json.loads(text)
        product["ai_title"] = ai_data.get("optimised_title", product["title"])
        product["ai_short_desc"] = ai_data.get("short_description", "")
        product["ai_description"] = ai_data.get("html_description", "")
        product["ai_meta"] = ai_data.get("meta_description", "")
        product["ai_tags"] = ai_data.get("tags", [])
        product["ai_type"] = ai_data.get("product_type", product["category"])
        return product
    except Exception as e:
        logger.debug(f"AI enrichment failed: {e}")
        return _template_enrich(product)


def _template_enrich(product: Dict) -> Dict:
    title = product["title"]
    price = product["sale_price"]
    product["ai_title"] = title[:70]
    product["ai_short_desc"] = f"Highly rated by {product['orders']}+ buyers — only ${price}!"
    product["ai_description"] = f"""
<h3>About This Product</h3>
<p>{title} — trusted by thousands of happy customers worldwide.</p>
<h3>Key Features</h3>
<ul>
  <li>⭐ Rated {product['rating']}/5 stars by {product['orders']}+ verified buyers</li>
  <li>✅ Premium quality at an unbeatable price of ${price}</li>
  <li>🚚 Fast worldwide shipping available</li>
  <li>🔒 30-day satisfaction guarantee</li>
  <li>📦 Ready to ship — order today!</li>
</ul>
<p><strong>Limited stock available — order now and save!</strong></p>
"""
    product["ai_meta"] = f"{title[:100]} — just ${price}. Fast shipping & top quality."
    product["ai_tags"] = [w for w in product["category"].lower().split() if len(w) > 3][:5]
    product["ai_type"] = product["category"]
    return product


def run_product_sync(config: Dict) -> Dict:
    logger.info("Starting product sync...")
    disc = config["product_discovery"]
    keywords = disc.get("search_keywords", [])
    per_kw = disc.get("products_per_keyword", 5)
    max_new = disc.get("max_new_products_per_run", 20)
    min_rating = disc.get("min_rating", 4.5)
    min_orders = disc.get("min_orders", 500)

    existing_conn = db.get_db()
    existing_ids = {r[0] for r in existing_conn.execute("SELECT id FROM products").fetchall()}
    existing_conn.close()

    random.shuffle(keywords)
    new_products = []

    for keyword in keywords:
        if len(new_products) >= max_new:
            break
        logger.info(f"  Searching '{keyword}'...")
        results = scrape_aliexpress(keyword, per_kw, min_rating, min_orders)
        for raw in results:
            if raw["id"] in existing_ids:
                continue
            raw["sale_price"] = calculate_sale_price(raw["supplier_price"], config)
            enriched = _ai_enrich(raw, config)
            new_products.append(enriched)
            existing_ids.add(raw["id"])
        time.sleep(random.uniform(1.0, 2.5))

    added = 0
    for product in new_products:
        db_product = {
            "id": product["id"],
            "title": product.get("ai_title", product["title"]),
            "sale_price": product["sale_price"],
            "original_price": product["original_price"],
            "rating": product["rating"],
            "orders": product["orders"],
            "image_urls": product.get("image_urls", []),
            "product_url": product.get("product_url", ""),
            "category": product.get("ai_type", product.get("category", "General")),
            "ai": {
                "product": {
                    "optimised_title": product.get("ai_title", product["title"]),
                    "short_description": product.get("ai_short_desc", ""),
                    "html_description": product.get("ai_description", ""),
                    "meta_description": product.get("ai_meta", ""),
                    "tags": product.get("ai_tags", []),
                    "product_type": product.get("ai_type", product.get("category", "General")),
                }
            },
        }
        is_new = db.upsert_product(db_product)
        if is_new:
            added += 1

    logger.info(f"Sync complete — {added} new products added")
    return {"added": added, "total_processed": len(new_products)}


def start_background_scheduler(config: Dict):
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        hours = config.get("automation", {}).get("product_sync_hours", 24)
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=lambda: run_product_sync(config), trigger="interval", hours=hours, id="product_sync")
        scheduler.start()
        logger.info(f"Background scheduler started (sync every {hours}h)")
        return scheduler
    except ImportError:
        logger.warning("APScheduler not installed — background sync disabled")
        return None
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        return None
