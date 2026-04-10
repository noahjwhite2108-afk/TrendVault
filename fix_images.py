import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/trendvault.db")

IMAGE_MAP = [
    {"keywords": ["ring light", "led ring"], "images": ["https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=600&q=80", "https://images.unsplash.com/photo-1616763355548-1b606f439f86?w=600&q=80"]},
    {"keywords": ["car phone mount", "magnetic car", "dashboard"], "images": ["https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=600&q=80", "https://images.unsplash.com/photo-1609577716667-86ecb7f9f5e5?w=600&q=80"]},
    {"keywords": ["garlic press", "crusher", "mincer"], "images": ["https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&q=80", "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=600&q=80"]},
    {"keywords": ["resistance band", "workout elastic", "exercise band"], "images": ["https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&q=80", "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600&q=80"]},
    {"keywords": ["silicone food", "storage bag", "reusable bag"], "images": ["https://images.unsplash.com/photo-1583947581924-860bda6a26df?w=600&q=80", "https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=600&q=80"]},
    {"keywords": ["usb-c", "charging cable", "braided nylon"], "images": ["https://images.unsplash.com/photo-1601524909162-ae8725290836?w=600&q=80", "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80"]},
    {"keywords": ["posture corrector", "back brace", "support belt"], "images": ["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80", "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&q=80"]},
    {"keywords": ["bamboo drawer", "organizer", "divider"], "images": ["https://images.unsplash.com/photo-1558618047-f4e90a0b6875?w=600&q=80", "https://images.unsplash.com/photo-1556909114-44e3e70034e2?w=600&q=80"]},
    {"keywords": ["scalp massager", "shampoo brush", "electric massager"], "images": ["https://images.unsplash.com/photo-1576426863848-c21f53c60b19?w=600&q=80", "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&q=80"]},
    {"keywords": ["water bottle", "collapsible", "foldable flask"], "images": ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&q=80", "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=600&q=80"]},
    {"keywords": ["led strip", "rgb", "color changing"], "images": ["https://images.unsplash.com/photo-1555664424-778a1e5e1b48?w=600&q=80", "https://images.unsplash.com/photo-1583394293214-bd7e2db87afd?w=600&q=80"]},
    {"keywords": ["wireless earbuds", "bluetooth", "tws"], "images": ["https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=600&q=80", "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80"]},
]

CATEGORY_IMAGES = {
    "Photography": ["https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=600&q=80"],
    "Car Accessories": ["https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=600&q=80"],
    "Kitchen": ["https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&q=80"],
    "Fitness": ["https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&q=80"],
    "Tech": ["https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=600&q=80"],
    "Health": ["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80"],
    "Home": ["https://images.unsplash.com/photo-1555664424-778a1e5e1b48?w=600&q=80"],
    "Beauty": ["https://images.unsplash.com/photo-1576426863848-c21f53c60b19?w=600&q=80"],
    "Outdoor": ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&q=80"],
    "General": ["https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&q=80"],
}

DEFAULT_IMAGE = ["https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&q=80"]

def find_images(title, category):
    title_lower = title.lower()
    for entry in IMAGE_MAP:
        if any(kw in title_lower for kw in entry["keywords"]):
            return entry["images"]
    return CATEGORY_IMAGES.get(category, DEFAULT_IMAGE)

if not DB_PATH.exists():
    print("❌ Database not found. Run the app first, then try again.")
else:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, title, category, images FROM products").fetchall()
    print(f"Found {len(rows)} products.")
    patched = 0
    for row in rows:
        try:
            imgs = json.loads(row["images"] or "[]")
        except:
            imgs = []
        if imgs:
            print(f"  ✅ {row['title'][:50]}")
            continue
        new_imgs = find_images(row["title"], row["category"] or "General")
        conn.execute("UPDATE products SET images=? WHERE id=?", (json.dumps(new_imgs), row["id"]))
        patched += 1
        print(f"  🖼️  Patched: {row['title'][:50]}")
    conn.commit()
    conn.close()
    print(f"\n✅ Done — {patched} products patched.")
