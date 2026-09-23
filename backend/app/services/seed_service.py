"""
AI Circular Economy Marketplace — Database Seeder
Populates initial demo accounts, categories, locations, materials, listings, and transactions.
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.dependencies import get_password_hash
from backend.app.models.location import Location
from backend.app.models.category import MaterialCategory
from backend.app.models.user import User
from backend.app.models.material import Material, MaterialImage
from backend.app.models.listing import Listing
from backend.app.models.buyer_requirement import BuyerRequirement
from backend.app.models.transaction import Transaction
from backend.app.models.sustainability import SustainabilityMetric

CITIES_DATA = [
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lon": 76.9558, "postal": "641001"},
    {"city": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "postal": "560001"},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707, "postal": "600001"},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "postal": "500001"},
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "postal": "400001"},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567, "postal": "411001"},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714, "postal": "380001"},
    {"city": "Delhi", "state": "Delhi", "lat": 28.7041, "lon": 77.1025, "postal": "110001"}
]

CATEGORIES_DATA = [
    {"name": "Aluminum", "desc": "Extruded profiles, alloy scrap, sheets and clean cans", "co2": 9.10, "landfill": 0.98},
    {"name": "Copper", "desc": "Clean stripped cable, millberry, pipe scrap and busbars", "co2": 4.50, "landfill": 0.99},
    {"name": "Steel", "desc": "Structural scrap, heavy melting steel (HMS 1&2), cuttings", "co2": 1.80, "landfill": 0.95},
    {"name": "Plastic", "desc": "Rigid HDPE, PET bottles, LDPE films, and PP regrind", "co2": 1.50, "landfill": 0.90},
    {"name": "Cardboard", "desc": "Corrugated boxes (OCC), double-wall kraft cartons", "co2": 1.00, "landfill": 0.95},
    {"name": "Paper", "desc": "De-inked office paper, sorted white ledger, newsprint", "co2": 1.10, "landfill": 0.92},
    {"name": "Glass", "desc": "Color-sorted cullet, container glass, float cullet", "co2": 0.35, "landfill": 0.99},
    {"name": "Textile", "desc": "Cotton garment cuttings, denim selvedge, blended yarn", "co2": 3.20, "landfill": 0.88},
    {"name": "E-waste", "desc": "Telecom PCB boards, server motherboards, electronic scrap", "co2": 5.80, "landfill": 0.96},
    {"name": "Other", "desc": "Industrial composites, rubber shreds, mixed recyclable lots", "co2": 0.80, "landfill": 0.85},
]


def seed_database(db: Session):
    # Check if already seeded
    if db.query(User).filter(User.email == "admin@circulareconomy.com").first():
        print("[Database] Already seeded. Skipping.")
        return

    print("[Database] Seeding initial circular marketplace dataset...")

    # 1. Locations
    locations = {}
    for c in CITIES_DATA:
        loc = Location(
            city=c["city"],
            state=c["state"],
            country="India",
            latitude=c["lat"],
            longitude=c["lon"],
            postal_code=c["postal"]
        )
        db.add(loc)
        db.flush()
        locations[c["city"]] = loc

    # 2. Material Categories
    categories = {}
    for cat_data in CATEGORIES_DATA:
        cat = MaterialCategory(
            name=cat_data["name"],
            description=cat_data["desc"],
            co2_factor_kg_per_kg=cat_data["co2"],
            landfill_diversion_factor=cat_data["landfill"]
        )
        db.add(cat)
        db.flush()
        categories[cat_data["name"]] = cat

    # 3. Users
    pwd_hash = get_password_hash("Admin@123")
    admin = User(
        name="System Administrator",
        email="admin@circulareconomy.com",
        password_hash=pwd_hash,
        role="admin",
        phone="+91 9876543210",
        organization="Circular Economy Authority",
        location_id=locations["Coimbatore"].id
    )
    db.add(admin)

    seller_pwd = get_password_hash("Seller@123")
    seller1 = User(
        name="Tamil Nadu Industrial Scrap Ltd",
        email="seller@ecotextiles.com",
        password_hash=seller_pwd,
        role="seller",
        phone="+91 9842100001",
        organization="Eco Materials Corp",
        location_id=locations["Coimbatore"].id
    )
    seller2 = User(
        name="Coimbatore Precision Alloys",
        email="seller2@coimbatoremetals.com",
        password_hash=seller_pwd,
        role="seller",
        phone="+91 9842100002",
        organization="Precision Metals Ltd",
        location_id=locations["Bengaluru"].id
    )
    db.add_all([seller1, seller2])

    buyer_pwd = get_password_hash("Buyer@123")
    buyer1 = User(
        name="GreenPlast Polymer Recyclers",
        email="buyer@greenplast.com",
        password_hash=buyer_pwd,
        role="buyer",
        phone="+91 9789000001",
        organization="GreenPlast Recyclers Hub",
        location_id=locations["Coimbatore"].id
    )
    buyer2 = User(
        name="Apex Smelting & Refining",
        email="buyer2@apexcopper.com",
        password_hash=buyer_pwd,
        role="buyer",
        phone="+91 9789000002",
        organization="Apex Copper Works",
        location_id=locations["Chennai"].id
    )
    buyer3 = User(
        name="Bharat Pulp & Paper Mills",
        email="buyer3@bharatpaper.com",
        password_hash=buyer_pwd,
        role="buyer",
        phone="+91 9789000003",
        organization="Bharat Paper Industries",
        location_id=locations["Bengaluru"].id
    )
    db.add_all([buyer1, buyer2, buyer3])
    db.flush()

    # 4. Materials & Listings
    SAMPLE_MATERIALS = [
        {
            "seller": seller1, "category": "Aluminum", "type": "Aluminum",
            "desc": "Extruded 6063 architectural aluminum scrap cuttings, clean and degreased.",
            "qty": 850.0, "quality": "High", "condition": "Clean", "purpose": "Recycling",
            "price": 185.0, "ask_price": 190.0, "img": "https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600"
        },
        {
            "seller": seller2, "category": "Copper", "type": "Copper",
            "desc": "Stripped bright shiny copper wire scrap (Millberry Grade 99.9% purity).",
            "qty": 420.0, "quality": "Industrial Grade", "condition": "Clean", "purpose": "Direct Reuse",
            "price": 680.0, "ask_price": 695.0, "img": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=600"
        },
        {
            "seller": seller1, "category": "Plastic", "type": "Plastic",
            "desc": "Baled post-consumer clear PET bottles, caps removed and pre-washed.",
            "qty": 1200.0, "quality": "High", "condition": "Sorted", "purpose": "Recycling",
            "price": 38.5, "ask_price": 40.0, "img": "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=600"
        },
        {
            "seller": seller2, "category": "Steel", "type": "Steel",
            "desc": "Industrial structural scrap beams and carbon steel plates, HMS-1 standard.",
            "qty": 3500.0, "quality": "High", "condition": "Sorted", "purpose": "Recycling",
            "price": 44.0, "ask_price": 45.5, "img": "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?w=600"
        },
        {
            "seller": seller1, "category": "Cardboard", "type": "Cardboard",
            "desc": "Compacted double-wall kraft corrugated cartons (OCC grade).",
            "qty": 2400.0, "quality": "Medium", "condition": "Baled", "purpose": "Recycling",
            "price": 14.5, "ask_price": 15.0, "img": "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=600"
        },
        {
            "seller": seller2, "category": "E-waste", "type": "E-waste",
            "desc": "Sorted telecommunication & server grade motherboards with gold-plated connectors.",
            "qty": 280.0, "quality": "High", "condition": "Sorted", "purpose": "Recycling",
            "price": 135.0, "ask_price": 140.0, "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600"
        },
        {
            "seller": seller1, "category": "Textile", "type": "Textile",
            "desc": "Combed virgin cotton spinning mill waste and yarn remnants.",
            "qty": 900.0, "quality": "High", "condition": "Clean", "purpose": "Upcycling",
            "price": 32.0, "ask_price": 34.0, "img": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600"
        },
        {
            "seller": seller2, "category": "Glass", "type": "Glass",
            "desc": "Clear container glass cullet, crushed to 20mm fraction.",
            "qty": 1800.0, "quality": "Medium", "condition": "Sorted", "purpose": "Recycling",
            "price": 8.5, "ask_price": 9.0, "img": "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=600"
        }
    ]

    for item in SAMPLE_MATERIALS:
        mat = Material(
            seller_id=item["seller"].id,
            category_id=categories[item["category"]].id,
            material_type=item["type"],
            description=item["desc"],
            quantity_kg=item["qty"],
            quality=item["quality"],
            condition=item["condition"],
            intended_purpose=item["purpose"],
            image_url=item["img"],
            predicted_price=item["price"],
            status="available"
        )
        db.add(mat)
        db.flush()

        listing = Listing(
            seller_id=item["seller"].id,
            material_id=mat.id,
            quantity_available=item["qty"],
            asking_price=item["ask_price"],
            status="active"
        )
        db.add(listing)

    # 5. Buyer Requirements
    REQUIREMENTS_DATA = [
        {"buyer": buyer1, "type": "Plastic", "min": 500, "max": 2500, "quality": "High", "purpose": "Recycling", "price": 42.0},
        {"buyer": buyer2, "type": "Copper", "min": 200, "max": 1000, "quality": "High", "purpose": "Direct Reuse", "price": 720.0},
        {"buyer": buyer2, "type": "Aluminum", "min": 400, "max": 2000, "quality": "Medium", "purpose": "Recycling", "price": 195.0},
        {"buyer": buyer3, "type": "Cardboard", "min": 1000, "max": 5000, "quality": "Medium", "purpose": "Recycling", "price": 16.0},
        {"buyer": buyer3, "type": "Paper", "min": 500, "max": 3000, "quality": "High", "purpose": "Recycling", "price": 14.0},
        {"buyer": buyer1, "type": "Textile", "min": 300, "max": 1500, "quality": "High", "purpose": "Upcycling", "price": 35.0},
        {"buyer": buyer2, "type": "Steel", "min": 1000, "max": 8000, "quality": "High", "purpose": "Recycling", "price": 48.0},
    ]

    for req_d in REQUIREMENTS_DATA:
        req = BuyerRequirement(
            buyer_id=req_d["buyer"].id,
            material_type=req_d["type"],
            min_quantity=req_d["min"],
            max_quantity=req_d["max"],
            quality=req_d["quality"],
            purpose=req_d["purpose"],
            max_price_per_kg=req_d["price"],
            location_id=req_d["buyer"].location_id,
            is_active=True
        )
        db.add(req)

    # 6. Completed Transactions
    TX_SAMPLES = [
        {"buyer": buyer2, "seller": seller1, "type": "Aluminum", "qty": 1200.0, "price": 182.0, "co2": 10920.0, "landfill": 1140.0, "days_ago": 12},
        {"buyer": buyer1, "seller": seller1, "type": "Plastic", "qty": 2500.0, "price": 37.0, "co2": 3750.0, "landfill": 2375.0, "days_ago": 25},
        {"buyer": buyer2, "seller": seller2, "type": "Copper", "qty": 600.0, "price": 675.0, "co2": 2700.0, "landfill": 570.0, "days_ago": 40},
        {"buyer": buyer3, "seller": seller1, "type": "Cardboard", "qty": 4500.0, "price": 14.0, "co2": 4500.0, "landfill": 4275.0, "days_ago": 55},
        {"buyer": buyer2, "seller": seller2, "type": "Steel", "qty": 5000.0, "price": 43.0, "co2": 9000.0, "landfill": 4750.0, "days_ago": 70},
    ]

    for tx_s in TX_SAMPLES:
        tx = Transaction(
            buyer_id=tx_s["buyer"].id,
            seller_id=tx_s["seller"].id,
            material_type=tx_s["type"],
            quantity_kg=tx_s["qty"],
            agreed_price=tx_s["price"],
            total_amount=round(tx_s["qty"] * tx_s["price"], 2),
            status="completed",
            co2_avoided_kg=tx_s["co2"],
            landfill_diverted_kg=tx_s["landfill"],
            created_at=datetime.utcnow() - timedelta(days=tx_s["days_ago"])
        )
        db.add(tx)

    db.commit()
    print("[Database] Successfully seeded admin, sellers, buyers, materials, requirements & transactions.")
