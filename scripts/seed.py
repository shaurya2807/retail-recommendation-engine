"""Seed the database with synthetic home improvement data."""
from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import settings          # noqa: E402
from app.repository.db import get_connection  # noqa: E402

# ── Catalog ──────────────────────────────────────────────────────────────────

PRODUCTS: list[dict] = [
    # Tools ── Hand Tools
    {"sku": "TOL-00001", "name": "20 oz Rip Hammer", "category": "Tools",
     "subcategory": "Hand Tools", "price": 18.97,
     "description": "Steel-head rip hammer with shock-absorbing fiberglass handle."},
    {"sku": "TOL-00002", "name": "6-Piece Screwdriver Set", "category": "Tools",
     "subcategory": "Hand Tools", "price": 14.97,
     "description": "Bi-material handle screwdrivers with precision-machined magnetic tips."},
    # Tools ── Power Tools
    {"sku": "TOL-00003", "name": "20V Cordless Drill/Driver", "category": "Tools",
     "subcategory": "Power Tools", "price": 89.00,
     "description": "Compact 20V lithium-ion drill with 2-speed transmission and LED light."},
    {"sku": "TOL-00004", "name": "7-1/4 in Circular Saw", "category": "Tools",
     "subcategory": "Power Tools", "price": 69.00,
     "description": "15-amp circular saw with laser guide and carbide-tipped 24-tooth blade."},
    {"sku": "TOL-00005", "name": "10-in Compound Miter Saw", "category": "Tools",
     "subcategory": "Power Tools", "price": 219.00,
     "description": "Dual-bevel compound miter saw with stainless bevel detents and LED shadow line."},
    {"sku": "TOL-00006", "name": "Random Orbit Sander 5-in", "category": "Tools",
     "subcategory": "Power Tools", "price": 49.00,
     "description": "5-in random orbit sander, 3.0A motor, dust-sealed power switch."},
    # Tools ── Measuring
    {"sku": "TOL-00007", "name": "25 ft Tape Measure", "category": "Tools",
     "subcategory": "Measuring", "price": 12.47,
     "description": "Impact-resistant tape measure with nylon-coated blade and magnetic hook."},
    {"sku": "TOL-00008", "name": "48-in Aluminum Level", "category": "Tools",
     "subcategory": "Measuring", "price": 24.98,
     "description": "Professional-grade aluminum level with three acrylic vials."},
    # Tools ── Safety
    {"sku": "TOL-00009", "name": "Hard Hat Type II Vented", "category": "Tools",
     "subcategory": "Safety", "price": 21.98,
     "description": "ANSI/ISEA Type II safety hard hat, vented, 6-point suspension."},
    {"sku": "TOL-00010", "name": "Leather Work Gloves M", "category": "Tools",
     "subcategory": "Safety", "price": 9.97,
     "description": "Full grain leather palm gloves with adjustable wrist strap."},

    # Lumber ── Dimensional
    {"sku": "LBR-00001", "name": "2x4x8 Kiln-Dried Stud", "category": "Lumber",
     "subcategory": "Dimensional", "price": 4.28,
     "description": "Kiln-dried Douglas fir framing stud, actual 1.5x3.5x96 in."},
    {"sku": "LBR-00002", "name": "2x6x8 Framing Lumber", "category": "Lumber",
     "subcategory": "Dimensional", "price": 7.15,
     "description": "Structural-grade 2x6 framing board, kiln-dried Douglas fir."},
    {"sku": "LBR-00003", "name": "2x10x12 Floor Joist", "category": "Lumber",
     "subcategory": "Dimensional", "price": 21.48,
     "description": "#2 Douglas fir floor/ceiling joist, 12-ft length."},
    {"sku": "LBR-00004", "name": "1x6x8 Cedar Fence Board", "category": "Lumber",
     "subcategory": "Dimensional", "price": 6.98,
     "description": "Select-grade western red cedar fence board, smooth face."},
    # Lumber ── Sheet Goods
    {"sku": "LBR-00005", "name": "3/4-in 4x8 Plywood Sheathing", "category": "Lumber",
     "subcategory": "Sheet Goods", "price": 42.97,
     "description": "23/32 CAT-PS1-09 plywood sheathing, T&G edges."},
    {"sku": "LBR-00006", "name": "7/16-in 4x8 OSB", "category": "Lumber",
     "subcategory": "Sheet Goods", "price": 14.87,
     "description": "Oriented strand board wall and roof sheathing panel."},
    {"sku": "LBR-00007", "name": "1/4-in 4x8 Lauan Plywood", "category": "Lumber",
     "subcategory": "Sheet Goods", "price": 19.97,
     "description": "Smooth lauan underlayment panel, sanded both sides."},
    {"sku": "LBR-00008", "name": "1/2-in 4x8 Drywall", "category": "Lumber",
     "subcategory": "Sheet Goods", "price": 13.48,
     "description": "Standard 1/2-in gypsum drywall panel for interior walls."},
    # Lumber ── Treated
    {"sku": "LBR-00009", "name": "4x4x8 Pressure-Treated Post", "category": "Lumber",
     "subcategory": "Treated", "price": 11.48,
     "description": "#2 Southern Yellow Pine ACQ ground-contact post."},
    {"sku": "LBR-00010", "name": "2x6x16 Pressure-Treated Deck Board", "category": "Lumber",
     "subcategory": "Treated", "price": 18.97,
     "description": "Ground-contact rated ACQ pressure-treated deck board."},

    # Plumbing ── Pipes & Fittings
    {"sku": "PLM-00001", "name": "1/2-in x 10-ft Schedule 40 PVC Pipe", "category": "Plumbing",
     "subcategory": "Pipes & Fittings", "price": 3.48,
     "description": "Schedule 40 white PVC pressure pipe, NSF-listed."},
    {"sku": "PLM-00002", "name": "1/2-in SharkBite 90° Elbow", "category": "Plumbing",
     "subcategory": "Pipes & Fittings", "price": 6.98,
     "description": "Push-to-connect elbow compatible with PEX, copper, and CPVC."},
    {"sku": "PLM-00003", "name": "3/4-in x 100-ft PEX-B Tubing Red", "category": "Plumbing",
     "subcategory": "Pipes & Fittings", "price": 39.97,
     "description": "Red PEX-B flexible tubing roll for hot water supply lines."},
    {"sku": "PLM-00004", "name": "P-Trap 1-1/2-in PVC", "category": "Plumbing",
     "subcategory": "Pipes & Fittings", "price": 4.97,
     "description": "Slip-joint PVC P-trap with 6-in adjustable extension arm."},
    {"sku": "PLM-00005", "name": "14-in Adjustable Pipe Wrench", "category": "Plumbing",
     "subcategory": "Pipes & Fittings", "price": 21.97,
     "description": "Drop-forged steel pipe wrench with aluminum jaw housing."},
    # Plumbing ── Valves
    {"sku": "PLM-00006", "name": "3/4-in Brass Full-Port Ball Valve", "category": "Plumbing",
     "subcategory": "Valves", "price": 11.97,
     "description": "Full-port brass ball valve with lockable lever handle."},
    # Plumbing ── Fixtures
    {"sku": "PLM-00007", "name": "Single-Handle Pull-Down Kitchen Faucet", "category": "Plumbing",
     "subcategory": "Fixtures", "price": 79.00,
     "description": "Pull-down sprayer kitchen faucet, brushed nickel finish."},
    {"sku": "PLM-00008", "name": "5-Setting Chrome Shower Head 2.5 GPM", "category": "Plumbing",
     "subcategory": "Fixtures", "price": 24.97,
     "description": "Fixed-mount shower head, 5 spray settings, 2.5 GPM."},
    {"sku": "PLM-00009", "name": "Wax Ring Toilet Seal Kit", "category": "Plumbing",
     "subcategory": "Fixtures", "price": 8.47,
     "description": "Standard wax ring with plastic horn and brass closet bolts."},
    # Plumbing ── Water Heaters
    {"sku": "PLM-00010", "name": "50-Gal Tall Electric Water Heater", "category": "Plumbing",
     "subcategory": "Water Heaters", "price": 549.00,
     "description": "50-gallon tall electric water heater, dual 4500W elements."},

    # Electrical ── Wiring
    {"sku": "ELC-00001", "name": "12-2 NM-B Romex Wire 250-ft", "category": "Electrical",
     "subcategory": "Wiring", "price": 74.00,
     "description": "12 AWG solid copper NM-B cable for 20A branch circuits."},
    {"sku": "ELC-00002", "name": "14-2 NM-B Romex Wire 100-ft", "category": "Electrical",
     "subcategory": "Wiring", "price": 27.98,
     "description": "14 AWG solid copper NM-B cable for 15A branch circuits."},
    {"sku": "ELC-00003", "name": "1/2-in EMT Conduit 10-ft", "category": "Electrical",
     "subcategory": "Wiring", "price": 5.48,
     "description": "1/2-in electrical metallic tubing, 10-ft length, galvanized."},
    # Electrical ── Outlets & Switches
    {"sku": "ELC-00004", "name": "20A GFCI Duplex Outlet White", "category": "Electrical",
     "subcategory": "Outlets & Switches", "price": 17.97,
     "description": "20A tamper-resistant GFCI receptacle with LED indicator, white."},
    {"sku": "ELC-00005", "name": "15A Single-Pole Toggle Switch", "category": "Electrical",
     "subcategory": "Outlets & Switches", "price": 2.98,
     "description": "Standard 15A/120V single-pole toggle light switch, white."},
    {"sku": "ELC-00006", "name": "150W LED Single-Pole Dimmer Switch", "category": "Electrical",
     "subcategory": "Outlets & Switches", "price": 14.97,
     "description": "Single-pole LED/CFL dimmer switch, 150W max, white."},
    {"sku": "ELC-00007", "name": "Outdoor GFCI Outlet In-Use Cover", "category": "Electrical",
     "subcategory": "Outlets & Switches", "price": 6.97,
     "description": "Weatherproof while-in-use cover for duplex receptacle, gray."},
    # Electrical ── Panels
    {"sku": "ELC-00008", "name": "20A Single-Pole Circuit Breaker", "category": "Electrical",
     "subcategory": "Panels", "price": 8.97,
     "description": "20A plug-in circuit breaker, QO-compatible."},
    {"sku": "ELC-00009", "name": "200A Main Breaker Panel 40-Space", "category": "Electrical",
     "subcategory": "Panels", "price": 189.00,
     "description": "200A 40-space 80-circuit indoor load center with main breaker."},
    # Electrical ── Lighting
    {"sku": "ELC-00010", "name": "A19 LED Bulb 60W Equiv 4-Pack", "category": "Electrical",
     "subcategory": "Lighting", "price": 11.97,
     "description": "800-lumen 2700K soft-white LED bulbs, 15,000-hr rated, 4-pack."},

    # Paint ── Interior
    {"sku": "PNT-00001", "name": "Interior Eggshell Paint 1-Gal White", "category": "Paint",
     "subcategory": "Interior", "price": 34.98,
     "description": "Zero-VOC interior eggshell latex, approx. 400 sq ft/gal."},
    {"sku": "PNT-00002", "name": "Interior Flat Paint 5-Gal Swiss Coffee", "category": "Paint",
     "subcategory": "Interior", "price": 139.00,
     "description": "5-gallon contractor-grade zero-VOC interior flat latex."},
    {"sku": "PNT-00003", "name": "Ultra-Matte Chalk Paint 1-Qt Linen", "category": "Paint",
     "subcategory": "Interior", "price": 22.98,
     "description": "Ultra-matte chalk-finish furniture and cabinet paint."},
    # Paint ── Exterior
    {"sku": "PNT-00004", "name": "Exterior Flat Paint 1-Gal Classic White", "category": "Paint",
     "subcategory": "Exterior", "price": 39.98,
     "description": "100% acrylic exterior flat paint, 10-year fade resistance."},
    {"sku": "PNT-00005", "name": "Fast-Dry Spray Paint Flat Black 12-oz", "category": "Paint",
     "subcategory": "Exterior", "price": 5.98,
     "description": "All-surface fast-dry spray paint, flat black, any-angle valve."},
    {"sku": "PNT-00006", "name": "Concrete & Masonry Waterproof Paint 1-Gal", "category": "Paint",
     "subcategory": "Exterior", "price": 36.98,
     "description": "Waterproofing masonry paint for below-grade and above-grade surfaces."},
    # Paint ── Primers
    {"sku": "PNT-00007", "name": "Interior/Exterior PVA Primer 1-Gal", "category": "Paint",
     "subcategory": "Primers", "price": 24.97,
     "description": "PVA drywall primer-sealer, ideal for bare and patched drywall."},
    {"sku": "PNT-00008", "name": "Stain-Blocking Oil Primer Spray 13-oz", "category": "Paint",
     "subcategory": "Primers", "price": 7.97,
     "description": "Oil-based stain-blocking spray primer for water stains and knots."},
    # Paint ── Stains & Finishes
    {"sku": "PNT-00009", "name": "Semi-Transparent Deck Stain 1-Gal Cedar", "category": "Paint",
     "subcategory": "Stains & Finishes", "price": 29.98,
     "description": "Oil-based semi-transparent deck stain, cedar tone."},
    {"sku": "PNT-00010", "name": "Oil-Based Polyurethane 1-Qt Satin", "category": "Paint",
     "subcategory": "Stains & Finishes", "price": 18.97,
     "description": "Satin oil-based polyurethane for floors and interior furniture."},
]

assert len(PRODUCTS) == 50, f"Expected 50 products, got {len(PRODUCTS)}"

USERNAMES: list[str] = [
    "mike_builds", "sarah_renovates", "tom_the_tiler", "jenny_diy",
    "carlos_contractor", "beth_paints", "raj_plumbing", "donna_decks",
    "frank_electric", "lena_lumber", "oscar_tools", "nina_nails",
    "dave_drywall", "amy_attic", "paul_plumber", "kim_kitchen",
    "steve_scaffold", "ruth_roof", "joe_joinery", "alice_allsorts",
]

assert len(USERNAMES) == 20, f"Expected 20 usernames, got {len(USERNAMES)}"

# Popularity weight per product (same order as PRODUCTS).
# Higher weight → more likely to be selected in interaction sampling.
PRODUCT_POPULARITY: list[int] = [
    # Tools: hammer, screwdrivers, drill, circ-saw, miter, sander, tape, level, hardhat, gloves
    2, 2, 5, 4, 3, 3, 3, 2, 1, 2,
    # Lumber: 2x4, 2x6, joist, cedar, plywood, OSB, lauan, drywall, PT-post, deck-board
    5, 3, 2, 2, 4, 4, 2, 4, 3, 2,
    # Plumbing: pvc-pipe, sharkbite, pex, p-trap, pipe-wrench, ball-valve, faucet, shower, wax-ring, water-heater
    3, 3, 2, 2, 2, 2, 4, 3, 2, 2,
    # Electrical: romex12, romex14, conduit, gfci, switch, dimmer, outdoor-cover, breaker, panel, bulbs
    4, 3, 2, 4, 3, 2, 2, 3, 2, 5,
    # Paint: eggshell, 5gal-flat, chalk, ext-flat, spray, masonry, primer, spray-primer, deck-stain, poly
    4, 3, 2, 3, 2, 2, 3, 2, 3, 2,
]

# Activity weight per user — some users are more active buyers.
USER_ACTIVITY: list[int] = [
    5, 4, 3, 5, 2, 3, 4, 2, 3, 2,
    1, 2, 3, 4, 2, 1, 3, 2, 2, 1,
]

# ── Helpers ───────────────────────────────────────────────────────────────────


def _weighted_choice(items: list, weights: list) -> object:
    w = weights[:len(items)]
    if len(w) < len(items):
        w += [1] * (len(items) - len(w))
    return random.choices(items, weights=w, k=1)[0]


# ── Migration ─────────────────────────────────────────────────────────────────


def run_migrations(conn) -> None:
    sql = (Path(__file__).parent.parent / "migrations" / "001_init.sql").read_text()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("Migrations applied.")


# ── Seeders ───────────────────────────────────────────────────────────────────


def seed_products(cur) -> list[int]:
    ids: list[int] = []
    for p in PRODUCTS:
        cur.execute(
            """
            INSERT INTO products (sku, name, category, subcategory, price, description)
            VALUES (%(sku)s, %(name)s, %(category)s, %(subcategory)s, %(price)s, %(description)s)
            ON CONFLICT (sku) DO NOTHING
            RETURNING id
            """,
            p,
        )
        row = cur.fetchone()
        if row:
            ids.append(row["id"])
    return ids


def seed_users(cur) -> list[int]:
    ids: list[int] = []
    for username in USERNAMES:
        cur.execute(
            "INSERT INTO users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING RETURNING id",
            (username,),
        )
        row = cur.fetchone()
        if row:
            ids.append(row["id"])
    return ids


def seed_interactions(cur, user_ids: list[int], product_ids: list[int]) -> int:
    now = datetime.now(tz=timezone.utc)
    window_start = now - timedelta(days=180)

    # Ratings biased toward satisfied customers (3-5).
    rating_population = [1, 2, 3, 4, 5]
    rating_weights    = [3, 5, 20, 40, 32]

    total = 0
    for _ in range(500):
        user_id    = _weighted_choice(user_ids, USER_ACTIVITY)
        product_id = _weighted_choice(product_ids, PRODUCT_POPULARITY)

        # Random timestamp within the 180-day window.
        offset_s  = random.randint(0, 180 * 24 * 3600)
        event_ts  = now - timedelta(seconds=offset_s)

        itype = random.choices(
            ["view", "cart", "purchase"],
            weights=[0.60, 0.25, 0.15],
        )[0]

        if itype == "purchase":
            # Insert a prior view 1–7 days before the purchase.
            view_ts = event_ts - timedelta(
                days=random.randint(1, 7),
                hours=random.randint(0, 23),
            )
            if view_ts < window_start:
                view_ts = window_start

            cur.execute(
                "INSERT INTO interactions (user_id, product_id, interaction_type, rating, created_at)"
                " VALUES (%s, %s, 'view', NULL, %s)",
                (user_id, product_id, view_ts),
            )
            total += 1

            rating = random.choices(rating_population, weights=rating_weights)[0]
            cur.execute(
                "INSERT INTO interactions (user_id, product_id, interaction_type, rating, created_at)"
                " VALUES (%s, %s, 'purchase', %s, %s)",
                (user_id, product_id, rating, event_ts),
            )
        else:
            cur.execute(
                "INSERT INTO interactions (user_id, product_id, interaction_type, rating, created_at)"
                " VALUES (%s, %s, %s, NULL, %s)",
                (user_id, product_id, itype, event_ts),
            )
        total += 1

    return total


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    print(f"Connecting to {settings.db_name}@{settings.db_host}:{settings.db_port} …")
    conn = get_connection()
    try:
        run_migrations(conn)

        with conn.cursor() as cur:
            product_ids = seed_products(cur)
            conn.commit()

            if not product_ids:
                # Already seeded — fetch existing IDs for interaction generation.
                cur.execute("SELECT id FROM products ORDER BY id")
                product_ids = [r["id"] for r in cur.fetchall()]

            user_ids = seed_users(cur)
            conn.commit()

            if not user_ids:
                cur.execute("SELECT id FROM users ORDER BY id")
                user_ids = [r["id"] for r in cur.fetchall()]

            n_interactions = seed_interactions(cur, user_ids, product_ids)
            conn.commit()

        print("\nSeed summary")
        print(f"  {'products':<14} {len(product_ids):>4} inserted")
        print(f"  {'users':<14} {len(user_ids):>4} inserted")
        print(f"  {'interactions':<14} {n_interactions:>4} inserted"
              f"  (500 primary events + prior views for purchases)")

    except Exception as exc:
        conn.rollback()
        print(f"Seed failed: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
