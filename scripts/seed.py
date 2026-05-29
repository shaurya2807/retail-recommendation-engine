"""Seed the database with synthetic products, users, and interactions."""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import settings  # noqa: E402 — path fix must come first
from app.repository.db import get_connection  # noqa: E402

CATEGORIES: dict[str, list[str]] = {
    "Electronics": ["Phones", "Laptops", "Audio", "Accessories"],
    "Clothing":    ["Men", "Women", "Kids", "Footwear"],
    "Home & Kitchen": ["Cookware", "Storage", "Decor", "Appliances"],
    "Books":       ["Fiction", "Non-Fiction", "Science", "Technology"],
    "Sports":      ["Fitness", "Outdoor", "Team Sports", "Water Sports"],
}

ADJECTIVES = ["Premium", "Ultra", "Classic", "Pro", "Lite", "Max", "Mini", "Smart"]

NOUNS: dict[str, list[str]] = {
    "Electronics":    ["Phone", "Laptop", "Tablet", "Speaker", "Headphones", "Charger"],
    "Clothing":       ["Shirt", "Jacket", "Pants", "Dress", "Sneakers", "Hat"],
    "Home & Kitchen": ["Pan", "Knife", "Container", "Mug", "Lamp", "Pillow"],
    "Books":          ["Guide", "Handbook", "Encyclopedia", "Novel", "Manual"],
    "Sports":         ["Weights", "Mat", "Bottle", "Bag", "Gloves", "Tracker"],
}


def _sku(category: str, n: int) -> str:
    return f"{category[:3].upper()}-{n:05d}"


def seed_products(cur, n: int = 50) -> list[int]:
    ids: list[int] = []
    for i in range(1, n + 1):
        cat = random.choice(list(CATEGORIES))
        sub = random.choice(CATEGORIES[cat])
        name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS[cat])}"
        price = round(random.uniform(5.99, 499.99), 2)
        desc = f"A quality {name.lower()} for {sub.lower()} enthusiasts."
        cur.execute(
            """
            INSERT INTO products (sku, name, category, subcategory, price, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (sku) DO NOTHING
            RETURNING id
            """,
            (_sku(cat, i), name, cat, sub, price, desc),
        )
        row = cur.fetchone()
        if row:
            ids.append(row["id"])
    print(f"  products : {len(ids)} inserted")
    return ids


def seed_users(cur, n: int = 20) -> list[int]:
    ids: list[int] = []
    for i in range(1, n + 1):
        cur.execute(
            "INSERT INTO users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING RETURNING id",
            (f"user_{i:03d}",),
        )
        row = cur.fetchone()
        if row:
            ids.append(row["id"])
    print(f"  users    : {len(ids)} inserted")
    return ids


def seed_interactions(cur, user_ids: list[int], product_ids: list[int], n: int = 200) -> None:
    types = ["view", "cart", "purchase"]
    weights = [0.60, 0.25, 0.15]
    for _ in range(n):
        itype = random.choices(types, weights=weights)[0]
        rating = random.randint(1, 5) if itype == "purchase" else None
        cur.execute(
            """
            INSERT INTO interactions (user_id, product_id, interaction_type, rating)
            VALUES (%s, %s, %s, %s)
            """,
            (random.choice(user_ids), random.choice(product_ids), itype, rating),
        )
    print(f"  interactions: {n} inserted")


def main() -> None:
    print("Connecting to", settings.db_name, "on", settings.db_host)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            product_ids = seed_products(cur)
            user_ids = seed_users(cur)
            if product_ids and user_ids:
                seed_interactions(cur, user_ids, product_ids)
        conn.commit()
        print("Seed complete.")
    except Exception as exc:
        conn.rollback()
        print(f"Seed failed: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
