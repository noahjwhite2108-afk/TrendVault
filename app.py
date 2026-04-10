"""
app.py — TrendVault e-commerce store
"""

import os
import json
import uuid
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, abort, flash
)
import database as db

try:
    with open("config.json") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    CONFIG = {"store":{"name":"TrendVault","tagline":"Today's Best Deals","domain":"localhost:5000","currency":"USD","admin_password":"change_me_before_launch","secret_key":"default_secret_key"},"payments":{"stripe_publishable_key":"pk_test_YOUR","stripe_secret_key":"sk_test_YOUR","stripe_webhook_secret":"whsec_YOUR"},"ai":{"provider":"gemini","api_key":"YOUR","model":"gemini-1.5-flash"},"supplier":{"platform":"aliexpress","affiliate_app_key":"","affiliate_app_secret":"","affiliate_tracking_id":""},"product_discovery":{"search_keywords":["trending gadgets","home organization","fitness accessories","phone accessories","kitchen tools"],"min_rating":4.5,"min_orders":500,"max_supplier_price_usd":30,"markup_multiplier":2.8,"shipping_buffer_usd":3.0,"products_per_keyword":5,"max_new_products_per_run":20,"exclude_categories":[]},"automation":{"product_sync_hours":24,"enabled":True}}

# Override config with environment variables if set (for Railway/cloud deployment)
if os.environ.get("GEMINI_API_KEY"):
    CONFIG["ai"]["api_key"] = os.environ["GEMINI_API_KEY"]
if os.environ.get("STRIPE_SECRET_KEY"):
    CONFIG["payments"]["stripe_secret_key"] = os.environ["STRIPE_SECRET_KEY"]
if os.environ.get("STRIPE_PUBLISHABLE_KEY"):
    CONFIG["payments"]["stripe_publishable_key"] = os.environ["STRIPE_PUBLISHABLE_KEY"]
if os.environ.get("ADMIN_PASSWORD"):
    CONFIG["store"]["admin_password"] = os.environ["ADMIN_PASSWORD"]

STORE = CONFIG["store"]
STRIPE_PUB = CONFIG["payments"]["stripe_publishable_key"]
STRIPE_SEC = CONFIG["payments"]["stripe_secret_key"]
STRIPE_WH  = CONFIG["payments"]["stripe_webhook_secret"]

app = Flask(__name__)
app.secret_key = STORE.get("secret_key", os.urandom(32))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    import stripe
    stripe.api_key = STRIPE_SEC
    STRIPE_OK = not STRIPE_SEC.startswith("sk_test_YOUR")
except ImportError:
    STRIPE_OK = False

db.init_db()

# Seed products — hardcoded here so no external file import needed on Railway
_SEED_PRODUCTS = [
    {"id":"seed001","title":"Portable LED Ring Light 10\" Selfie Light with Phone Holder","sale_price":24.99,"original_price":34.99,"rating":4.7,"orders":12500,"category":"Photography","image_urls":["https://images.unsplash.com/photo-1616400619175-5beda3a17896?w=600"],"ai":{"product":{"optimised_title":"Portable 10\" LED Ring Light","short_description":"Perfect lighting for photos, videos, and video calls.","html_description":"<p>Professional studio lighting in your pocket.</p>","tags":["ring light","photography"],"product_type":"Photography"}}},
    {"id":"seed002","title":"Resistance Bands Set 5-Pack for Home Workout","sale_price":19.99,"original_price":29.99,"rating":4.8,"orders":23400,"category":"Fitness","image_urls":["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600"],"ai":{"product":{"optimised_title":"Resistance Bands Set 5-Pack","short_description":"Build strength at home with these durable bands.","html_description":"<p>Versatile resistance bands for all fitness levels.</p>","tags":["fitness","workout","bands"],"product_type":"Fitness"}}},
    {"id":"seed003","title":"Wireless Earbuds Bluetooth 5.3 with Charging Case","sale_price":29.99,"original_price":49.99,"rating":4.6,"orders":45600,"category":"Electronics","image_urls":["https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600"],"ai":{"product":{"optimised_title":"Wireless Earbuds Bluetooth 5.3","short_description":"Crystal-clear audio with 30-hour battery life.","html_description":"<p>Premium wireless audio experience.</p>","tags":["earbuds","bluetooth","wireless"],"product_type":"Electronics"}}},
    {"id":"seed004","title":"Portable Phone Stand Adjustable Desk Holder","sale_price":12.99,"original_price":19.99,"rating":4.5,"orders":8900,"category":"Accessories","image_urls":["https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=600"],"ai":{"product":{"optimised_title":"Adjustable Phone Desk Stand","short_description":"Hands-free viewing at the perfect angle.","html_description":"<p>Works with all phones and tablets.</p>","tags":["phone stand","desk","accessories"],"product_type":"Accessories"}}},
    {"id":"seed005","title":"Smart Water Bottle with Temperature Display","sale_price":34.99,"original_price":44.99,"rating":4.7,"orders":6700,"category":"Kitchen","image_urls":["https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600"],"ai":{"product":{"optimised_title":"Smart Water Bottle with Temp Display","short_description":"Stay hydrated with smart temperature tracking.","html_description":"<p>LED temperature display keeps you on track.</p>","tags":["water bottle","smart","hydration"],"product_type":"Kitchen"}}},
    {"id":"seed006","title":"Laptop Stand Ergonomic Adjustable Aluminum","sale_price":39.99,"original_price":59.99,"rating":4.8,"orders":15300,"category":"Office","image_urls":["https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600"],"ai":{"product":{"optimised_title":"Ergonomic Aluminum Laptop Stand","short_description":"Reduce neck strain with perfect ergonomic height.","html_description":"<p>Premium aluminum build for any desk setup.</p>","tags":["laptop stand","ergonomic","office"],"product_type":"Office"}}},
    {"id":"seed007","title":"Foam Roller for Muscle Recovery Deep Tissue","sale_price":22.99,"original_price":34.99,"rating":4.6,"orders":11200,"category":"Fitness","image_urls":["https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600"],"ai":{"product":{"optimised_title":"Deep Tissue Foam Roller","short_description":"Speed up recovery and release muscle tension.","html_description":"<p>Professional-grade foam roller for serious athletes.</p>","tags":["foam roller","recovery","fitness"],"product_type":"Fitness"}}},
    {"id":"seed008","title":"Cable Management Box Organizer Desktop","sale_price":18.99,"original_price":27.99,"rating":4.5,"orders":7800,"category":"Office","image_urls":["https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600"],"ai":{"product":{"optimised_title":"Desktop Cable Management Box","short_description":"Hide messy cables and power strips instantly.","html_description":"<p>Clean up your desk in minutes.</p>","tags":["cable management","desk","organizer"],"product_type":"Office"}}},
    {"id":"seed009","title":"Silk Sleep Mask Blackout Eye Mask for Travel","sale_price":14.99,"original_price":22.99,"rating":4.7,"orders":19400,"category":"Wellness","image_urls":["https://images.unsplash.com/photo-1511295742362-92c96b1cf484?w=600"],"ai":{"product":{"optimised_title":"Silk Blackout Sleep Mask","short_description":"Block out light completely for deeper sleep.","html_description":"<p>Luxurious silk feel for restful nights.</p>","tags":["sleep mask","silk","wellness"],"product_type":"Wellness"}}},
    {"id":"seed010","title":"Stainless Steel Insulated Travel Mug 20oz","sale_price":27.99,"original_price":39.99,"rating":4.8,"orders":31200,"category":"Kitchen","image_urls":["https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600"],"ai":{"product":{"optimised_title":"Insulated Stainless Travel Mug 20oz","short_description":"Keeps drinks hot 12hrs, cold 24hrs.","html_description":"<p>Leak-proof lid, fits all cup holders.</p>","tags":["travel mug","insulated","coffee"],"product_type":"Kitchen"}}},
    {"id":"seed011","title":"Yoga Mat Non-Slip 6mm Extra Thick with Strap","sale_price":32.99,"original_price":49.99,"rating":4.7,"orders":14500,"category":"Fitness","image_urls":["https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600"],"ai":{"product":{"optimised_title":"Non-Slip Yoga Mat 6mm Extra Thick","short_description":"Premium grip surface for safe practice.","html_description":"<p>Eco-friendly TPE material, includes carry strap.</p>","tags":["yoga mat","fitness","non-slip"],"product_type":"Fitness"}}},
    {"id":"seed012","title":"Magnetic Phone Car Mount Universal Dashboard","sale_price":16.99,"original_price":24.99,"rating":4.6,"orders":28700,"category":"Accessories","image_urls":["https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600"],"ai":{"product":{"optimised_title":"Magnetic Phone Car Mount","short_description":"Hands-free navigation with strong magnetic hold.","html_description":"<p>Universal fit for all smartphones.</p>","tags":["car mount","magnetic","phone"],"product_type":"Accessories"}}},
]

def _auto_seed():
    try:
        for p in _SEED_PRODUCTS:
            db.upsert_product(p)
        print(f"[TrendVault] Seeded {len(_SEED_PRODUCTS)} products with images", flush=True)
        logger.info(f"Seeded {len(_SEED_PRODUCTS)} products with images")
    except Exception as e:
        print(f"[TrendVault] Seed failed: {e}", flush=True)
        logger.warning(f"Auto-seed failed: {e}")

_auto_seed()


@app.context_processor
def inject_globals():
    cart = session.get("cart", {})
    cart_count = sum(item["qty"] for item in cart.values()) if cart else 0
    return {
        "store": STORE,
        "cart_count": cart_count,
        "categories": db.get_categories(),
        "stripe_pub": STRIPE_PUB,
        "stripe_enabled": STRIPE_OK,
        "now": datetime.utcnow(),
    }


@app.route("/debug-db")
def debug_db():
    import sqlite3
    stats = db.get_stats()
    products = db.get_products(limit=5)
    rows = []
    for p in products:
        rows.append(f"{p['id']} | {p['title'][:40]} | images: {p['images']}")
    return "<pre>Stats: " + str(stats) + "\n\nProducts:\n" + "\n".join(rows) + "</pre>"

@app.route("/")
def index():
    featured = db.get_products(featured_only=True, limit=8)
    if len(featured) < 4:
        featured = db.get_products(limit=8)
    recent = db.get_products(limit=12)
    categories = db.get_categories()[:6]
    return render_template("index.html", featured=featured, recent=recent, categories=categories)


@app.route("/shop")
def shop():
    category = request.args.get("category", "")
    search = request.args.get("q", "")
    page = int(request.args.get("page", 1))
    per_page = 24
    offset = (page - 1) * per_page
    products = db.get_products(category=category or None, search=search or None, limit=per_page + 1, offset=offset)
    has_next = len(products) > per_page
    products = products[:per_page]
    return render_template("shop.html", products=products, category=category, search=search, page=page, has_next=has_next)


@app.route("/product/<slug>")
def product(slug):
    p = db.get_product_by_slug(slug)
    if not p:
        abort(404)
    related = [r for r in db.get_products(category=p["category"], limit=5) if r["id"] != p["id"]][:4]
    return render_template("product.html", product=p, related=related)


def _get_cart():
    return session.get("cart", {})

def _save_cart(cart):
    session["cart"] = cart
    session.modified = True


@app.route("/api/cart/add", methods=["POST"])
def cart_add():
    data = request.get_json(force=True)
    pid = data.get("product_id")
    qty = int(data.get("qty", 1))
    product = db.get_product_by_id(pid)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    cart = _get_cart()
    if pid in cart:
        cart[pid]["qty"] += qty
    else:
        cart[pid] = {"id": pid, "title": product["title"], "price": product["price"],
                     "image": product["images"][0] if product["images"] else "", "slug": product["slug"], "qty": qty}
    _save_cart(cart)
    total_items = sum(i["qty"] for i in cart.values())
    return jsonify({"success": True, "cart_count": total_items})


@app.route("/api/cart/update", methods=["POST"])
def cart_update():
    data = request.get_json(force=True)
    pid = data.get("product_id")
    qty = int(data.get("qty", 0))
    cart = _get_cart()
    if pid in cart:
        if qty <= 0:
            del cart[pid]
        else:
            cart[pid]["qty"] = qty
    _save_cart(cart)
    return jsonify({"success": True, "cart": _cart_summary(cart)})


@app.route("/api/cart/remove", methods=["POST"])
def cart_remove():
    data = request.get_json(force=True)
    pid = data.get("product_id")
    cart = _get_cart()
    cart.pop(pid, None)
    _save_cart(cart)
    return jsonify({"success": True, "cart": _cart_summary(cart)})


@app.route("/cart")
def cart():
    cart = _get_cart()
    summary = _cart_summary(cart)
    return render_template("cart.html", cart=cart, summary=summary)


def _cart_summary(cart):
    subtotal = sum(i["price"] * i["qty"] for i in cart.values())
    shipping = 0 if subtotal >= 50 else 4.99
    total = round(subtotal + shipping, 2)
    return {"subtotal": round(subtotal, 2), "shipping": shipping, "total": total}


@app.route("/checkout", methods=["GET"])
def checkout():
    cart = _get_cart()
    if not cart:
        return redirect(url_for("shop"))
    summary = _cart_summary(cart)
    return render_template("checkout.html", cart=cart, summary=summary)


@app.route("/checkout/create-payment-intent", methods=["POST"])
def create_payment_intent():
    if not STRIPE_OK:
        return jsonify({"error": "Stripe not configured"}), 400
    cart = _get_cart()
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400
    summary = _cart_summary(cart)
    amount_cents = int(summary["total"] * 100)
    intent = stripe.PaymentIntent.create(amount=amount_cents, currency="usd", metadata={"store": "trendvault"})
    return jsonify({"clientSecret": intent.client_secret})


@app.route("/checkout/confirm", methods=["POST"])
def checkout_confirm():
    data = request.get_json(force=True)
    cart = _get_cart()
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400
    summary = _cart_summary(cart)
    address = {"line1": data.get("address_line1",""), "city": data.get("city",""),
               "state": data.get("state",""), "zip": data.get("zip",""), "country": data.get("country","US")}
    order_id = db.create_order({
        "customer_name": data.get("name",""),
        "customer_email": data.get("email",""),
        "customer_address": json.dumps(address),
        "items": [{"id": v["id"], "title": v["title"], "price": v["price"], "qty": v["qty"]} for v in cart.values()],
        "subtotal": summary["subtotal"], "shipping": summary["shipping"], "total": summary["total"],
        "status": "paid", "payment_intent": data.get("payment_intent_id",""),
    })
    session.pop("cart", None)
    return jsonify({"success": True, "order_id": order_id})


@app.route("/checkout/demo-confirm", methods=["POST"])
def checkout_demo_confirm():
    data = request.get_json(force=True)
    cart = _get_cart()
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400
    summary = _cart_summary(cart)
    address = {"line1": data.get("address_line1",""), "city": data.get("city",""), "zip": data.get("zip","")}
    order_id = db.create_order({
        "customer_name": data.get("name","Demo Customer"),
        "customer_email": data.get("email","demo@example.com"),
        "customer_address": json.dumps(address),
        "items": [{"id": v["id"], "title": v["title"], "price": v["price"], "qty": v["qty"]} for v in cart.values()],
        "subtotal": summary["subtotal"], "shipping": summary["shipping"], "total": summary["total"],
        "status": "demo", "payment_intent": "DEMO",
    })
    session.pop("cart", None)
    return jsonify({"success": True, "order_id": order_id})


@app.route("/order/<order_id>")
def order_success(order_id):
    order = db.get_order(order_id)
    if not order:
        abort(404)
    return render_template("order_success.html", order=order)


@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature","")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WH)
    except Exception:
        return "", 400
    return "", 200


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        pw = request.form.get("password","")
        if pw == STORE["admin_password"]:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect password", "error")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    stats = db.get_stats()
    recent_orders = db.get_all_orders(10)
    products = db.get_products(limit=20)
    return render_template("admin/dashboard.html", stats=stats, recent_orders=recent_orders, products=products)


@app.route("/admin/products")
@admin_required
def admin_products():
    search = request.args.get("q","")
    products = db.get_products(search=search or None, limit=100)
    return render_template("admin/products.html", products=products, search=search)


@app.route("/admin/products/toggle-featured", methods=["POST"])
@admin_required
def toggle_featured():
    data = request.get_json(force=True)
    pid = data["product_id"]
    product = db.get_product_by_id(pid)
    if product:
        db.set_featured(pid, not product["featured"])
    return jsonify({"success": True})


@app.route("/admin/orders")
@admin_required
def admin_orders():
    orders = db.get_all_orders(100)
    return render_template("admin/orders.html", orders=orders)


@app.route("/admin/sync", methods=["POST"])
@admin_required
def admin_sync():
    from src.automation import run_product_sync
    try:
        result = run_product_sync(CONFIG)
        return jsonify({"success": True, "added": result.get("added", 0)})
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG","false").lower() == "true"
    if CONFIG.get("automation",{}).get("enabled", True):
        from src.automation import start_background_scheduler
        start_background_scheduler(CONFIG)
    logger.info(f"TrendVault starting on http://localhost:{port}")
    logger.info(f"Admin panel: http://localhost:{port}/admin")
    app.run(host="0.0.0.0", port=port, debug=debug)
