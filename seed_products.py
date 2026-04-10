"""
seed_products.py — Adds 20 real sample products with images to TrendVault.
Run once with: python3 seed_products.py
"""
import sys
sys.path.insert(0, '.')
import database as db

db.init_db()

PRODUCTS = [
    {
        "id": "seed001",
        "title": "Portable LED Ring Light 10\" Selfie Light with Phone Holder",
        "sale_price": 24.99, "original_price": 34.99,
        "rating": 4.7, "orders": 12500, "category": "Photography",
        "image_urls": ["https://images.unsplash.com/photo-1616400619175-5beda3a17896?w=600"],
        "ai": {"product": {
            "optimised_title": "Portable 10\" LED Ring Light with Phone Holder",
            "short_description": "Perfect lighting for photos, videos, and video calls.",
            "html_description": "<h3>Look Great On Camera</h3><p>Professional studio lighting in your pocket. Perfect for content creators, remote workers, and beauty enthusiasts.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.7/5 by 12,500+ buyers</li><li>3 colour modes: warm, cool, natural</li><li>Flexible phone holder fits all phones</li><li>USB powered — works anywhere</li><li>Foldable & ultra-portable</li></ul>",
            "meta_description": "10\" LED Ring Light with phone holder. 3 colour modes, USB powered. Perfect for selfies & video calls. Only $24.99.",
            "tags": ["ring light","selfie","photography","youtube","tiktok"],
            "product_type": "Photography"
        }}
    },
    {
        "id": "seed002",
        "title": "Resistance Bands Set 5-Pack for Home Workout",
        "sale_price": 19.99, "original_price": 29.99,
        "rating": 4.8, "orders": 15200, "category": "Fitness",
        "image_urls": ["https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600"],
        "ai": {"product": {
            "optimised_title": "Resistance Bands Set — 5 Levels for All Fitness Goals",
            "short_description": "Build strength anywhere with this 5-band set.",
            "html_description": "<h3>Your Gym, Anywhere</h3><p>Five resistance levels from light to extra-heavy — perfect for beginners and athletes alike.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.8/5 by 15,000+ buyers</li><li>5 resistance levels included</li><li>Durable latex material</li><li>Carry bag included</li><li>Great for stretching, yoga & strength training</li></ul>",
            "meta_description": "5-pack resistance bands for home workouts. All fitness levels. Only $19.99 with free shipping over $50.",
            "tags": ["fitness","workout","gym","resistance bands","home gym"],
            "product_type": "Fitness"
        }}
    },
    {
        "id": "seed003",
        "title": "Stainless Steel Insulated Water Bottle 32oz",
        "sale_price": 22.99, "original_price": 32.99,
        "rating": 4.9, "orders": 28000, "category": "Outdoor",
        "image_urls": ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600"],
        "ai": {"product": {
            "optimised_title": "32oz Insulated Stainless Steel Water Bottle",
            "short_description": "Keeps drinks cold 24h, hot 12h — built to last.",
            "html_description": "<h3>Stay Hydrated All Day</h3><p>Double-wall vacuum insulation keeps your drinks at the perfect temperature all day long.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.9/5 by 28,000+ buyers</li><li>Cold 24 hours / Hot 12 hours</li><li>BPA-free stainless steel</li><li>Leak-proof lid</li><li>Fits standard cup holders</li></ul>",
            "meta_description": "32oz insulated water bottle. Cold 24h, hot 12h. BPA-free & leak-proof. Only $22.99.",
            "tags": ["water bottle","hydration","outdoor","gym","eco friendly"],
            "product_type": "Outdoor"
        }}
    },
    {
        "id": "seed004",
        "title": "Wireless Charging Pad Fast Charge 15W",
        "sale_price": 17.99, "original_price": 25.99,
        "rating": 4.6, "orders": 19300, "category": "Tech",
        "image_urls": ["https://images.unsplash.com/photo-1586816001966-79b736744398?w=600"],
        "ai": {"product": {
            "optimised_title": "15W Fast Wireless Charging Pad — All Qi Devices",
            "short_description": "Drop and charge — no cables, just fast wireless power.",
            "html_description": "<h3>No More Cables</h3><p>Works with all Qi-enabled devices. Just drop your phone on the pad and it charges — fast.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.6/5 by 19,000+ buyers</li><li>15W fast charge for compatible phones</li><li>Works with iPhone, Samsung, and all Qi devices</li><li>LED indicator light</li><li>Anti-slip surface</li></ul>",
            "meta_description": "15W wireless charging pad. Works with iPhone & Android. Fast, cable-free charging for $17.99.",
            "tags": ["wireless charger","tech","iphone","samsung","charging"],
            "product_type": "Tech"
        }}
    },
    {
        "id": "seed005",
        "title": "Bamboo Wooden Desk Organizer with Drawer",
        "sale_price": 29.99, "original_price": 42.99,
        "rating": 4.7, "orders": 8400, "category": "Home",
        "image_urls": ["https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600"],
        "ai": {"product": {
            "optimised_title": "Bamboo Desk Organizer with Storage Drawer",
            "short_description": "Keep your desk tidy with this elegant bamboo organizer.",
            "html_description": "<h3>A Cleaner Desk, A Clearer Mind</h3><p>Handcrafted from sustainable bamboo. Fits all your essentials neatly on your desk.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.7/5 by 8,400+ buyers</li><li>Eco-friendly sustainable bamboo</li><li>Hidden pull-out drawer</li><li>Multiple compartments</li><li>Fits phones, pens, notebooks & more</li></ul>",
            "meta_description": "Bamboo desk organizer with drawer. Eco-friendly, stylish, and practical. Only $29.99.",
            "tags": ["desk organizer","bamboo","home office","organization","workspace"],
            "product_type": "Home"
        }}
    },
    {
        "id": "seed006",
        "title": "Electric Scalp Massager Waterproof Shampoo Brush",
        "sale_price": 21.99, "original_price": 31.99,
        "rating": 4.6, "orders": 11200, "category": "Beauty",
        "image_urls": ["https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600"],
        "ai": {"product": {
            "optimised_title": "Electric Scalp Massager & Shampoo Brush",
            "short_description": "Stimulate your scalp and wash hair effortlessly.",
            "html_description": "<h3>Spa Day, Every Day</h3><p>Gentle vibrating bristles massage your scalp while deep-cleaning your hair. 100% waterproof.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.6/5 by 11,000+ buyers</li><li>Waterproof — safe in shower</li><li>Promotes hair growth & blood circulation</li><li>USB rechargeable</li><li>Soft silicone bristles</li></ul>",
            "meta_description": "Electric scalp massager & shampoo brush. Waterproof, USB rechargeable. Promotes hair growth. $21.99.",
            "tags": ["beauty","hair care","scalp massager","self care","shower"],
            "product_type": "Beauty"
        }}
    },
    {
        "id": "seed007",
        "title": "Magnetic Phone Car Mount for Dashboard & Vent",
        "sale_price": 14.99, "original_price": 21.99,
        "rating": 4.5, "orders": 22100, "category": "Car Accessories",
        "image_urls": ["https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=600"],
        "ai": {"product": {
            "optimised_title": "Magnetic Car Phone Mount — Dashboard & Air Vent",
            "short_description": "One-hand mounting, 360° rotation, rock-solid grip.",
            "html_description": "<h3>Eyes on the Road</h3><p>Strong magnetic hold keeps your phone secure on any road. Mounts to dashboard or air vent.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.5/5 by 22,000+ buyers</li><li>360° rotation for portrait & landscape</li><li>Fits all phone sizes</li><li>Two mounting options included</li><li>One-hand placement & removal</li></ul>",
            "meta_description": "Magnetic car phone mount. 360° rotation, dashboard & vent compatible. Only $14.99.",
            "tags": ["car mount","phone holder","car accessories","navigation","driving"],
            "product_type": "Car Accessories"
        }}
    },
    {
        "id": "seed008",
        "title": "Posture Corrector Back Support Brace Adjustable",
        "sale_price": 25.99, "original_price": 37.99,
        "rating": 4.5, "orders": 9800, "category": "Health",
        "image_urls": ["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600"],
        "ai": {"product": {
            "optimised_title": "Adjustable Posture Corrector Back Support Brace",
            "short_description": "Fix your posture in weeks — comfortable all-day wear.",
            "html_description": "<h3>Stand Tall, Feel Better</h3><p>Gently trains your muscles to maintain proper posture. Wear under or over clothing.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.5/5 by 9,800+ buyers</li><li>Fully adjustable for all body types</li><li>Breathable mesh material</li><li>Discreet under clothing</li><li>Recommended by physiotherapists</li></ul>",
            "meta_description": "Adjustable posture corrector for men & women. Breathable, all-day comfort. Only $25.99.",
            "tags": ["posture","back pain","health","office","ergonomic"],
            "product_type": "Health"
        }}
    },
    {
        "id": "seed009",
        "title": "LED Strip Lights 5M RGB Smart App Controlled",
        "sale_price": 26.99, "original_price": 39.99,
        "rating": 4.7, "orders": 31000, "category": "Home",
        "image_urls": ["https://images.unsplash.com/photo-1608155686393-8fdd966d784d?w=600"],
        "ai": {"product": {
            "optimised_title": "5M Smart RGB LED Strip Lights — App Controlled",
            "short_description": "16 million colours, music sync, app & remote control.",
            "html_description": "<h3>Transform Any Room</h3><p>16 million colours at your fingertips. Sync to music, set schedules, and control from anywhere.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.7/5 by 31,000+ buyers</li><li>5 metres — covers most rooms</li><li>App controlled + remote included</li><li>Music sync mode</li><li>Easy peel-and-stick installation</li></ul>",
            "meta_description": "5M smart RGB LED strip lights. App controlled, music sync, 16M colours. Only $26.99.",
            "tags": ["led lights","room decor","smart home","rgb","gaming setup"],
            "product_type": "Home"
        }}
    },
    {
        "id": "seed010",
        "title": "Reusable Silicone Food Storage Bags Set of 6",
        "sale_price": 18.99, "original_price": 27.99,
        "rating": 4.6, "orders": 14500, "category": "Kitchen",
        "image_urls": ["https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600"],
        "ai": {"product": {
            "optimised_title": "Reusable Silicone Food Storage Bags — Set of 6",
            "short_description": "Replace single-use plastic forever. Freezer & dishwasher safe.",
            "html_description": "<h3>Good for You. Good for the Planet.</h3><p>Ditch single-use plastic bags for good. These silicone bags last for years and are completely safe.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.6/5 by 14,500+ buyers</li><li>BPA-free food-grade silicone</li><li>Dishwasher, microwave & freezer safe</li><li>Airtight leak-proof seal</li><li>3 sizes included</li></ul>",
            "meta_description": "6-pack reusable silicone food bags. BPA-free, dishwasher safe, freezer friendly. Only $18.99.",
            "tags": ["kitchen","eco friendly","food storage","reusable","sustainable"],
            "product_type": "Kitchen"
        }}
    },
    {
        "id": "seed011",
        "title": "Foam Roller for Muscle Recovery Deep Tissue Massage",
        "sale_price": 23.99, "original_price": 34.99,
        "rating": 4.7, "orders": 17800, "category": "Fitness",
        "image_urls": ["https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600"],
        "ai": {"product": {
            "optimised_title": "Deep Tissue Foam Roller for Muscle Recovery",
            "short_description": "Relieve soreness fast with deep-tissue massage anywhere.",
            "html_description": "<h3>Recover Faster, Train Harder</h3><p>Firm EVA foam breaks up muscle knots and increases blood flow for faster recovery after workouts.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.7/5 by 17,800+ buyers</li><li>High-density EVA foam</li><li>Grid texture for targeted pressure</li><li>Full body use — back, legs, calves</li><li>Hollow core for easy travel</li></ul>",
            "meta_description": "High-density foam roller for deep tissue massage & muscle recovery. Only $23.99.",
            "tags": ["foam roller","fitness","recovery","yoga","muscle relief"],
            "product_type": "Fitness"
        }}
    },
    {
        "id": "seed012",
        "title": "Noise Cancelling Wireless Bluetooth Headphones",
        "sale_price": 44.99, "original_price": 69.99,
        "rating": 4.8, "orders": 42000, "category": "Tech",
        "image_urls": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"],
        "ai": {"product": {
            "optimised_title": "Wireless Noise Cancelling Headphones — 40Hr Battery",
            "short_description": "Premium sound, zero distractions, 40-hour battery life.",
            "html_description": "<h3>Pure Sound. Zero Noise.</h3><p>Active noise cancellation blocks out the world so you can focus on what matters — your music.</p><h3>Key Features</h3><ul><li>⭐ Rated 4.8/5 by 42,000+ buyers</li><li>Active Noise Cancellation (ANC)</li><li>40-hour battery life</li><li>Foldable for travel</li><li>Built-in mic for calls</li></ul>",
            "meta_description": "Wireless noise cancelling headphones. 40hr battery, premium sound, built-in mic. Only $44.99.",
            "tags": ["headphones","bluetooth","noise cancelling","music","tech"],
            "product_type": "Tech"
        }}
    },
]

added = 0
for p in PRODUCTS:
    is_new = db.upsert_product(p)
    status = "✅ Added" if is_new else "↩️  Updated"
    print(f"{status}: {p['title'][:55]}")
    if is_new:
        added += 1

print(f"\n🎉 Done! {added} products added to your store.")
print("Refresh http://localhost:8080 to see them.")
