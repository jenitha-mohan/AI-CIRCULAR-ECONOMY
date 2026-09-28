import logging
from sqlalchemy.orm import Session
from backend.app.models.location import Location
from backend.app.models.category import MaterialCategory

logger = logging.getLogger(__name__)

def seed_database(db: Session):
    """
    Seeds the database with essential taxonomies: Locations and Categories.
    Strictly skips User creation (No Demo Accounts permitted by design constraints).
    """
    # 1. Locations
    locations_data = [
        {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
        {"city": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
        {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707}
    ]
    
    locations = {}
    for loc_d in locations_data:
        loc = db.query(Location).filter_by(city=loc_d["city"]).first()
        if not loc:
            loc = Location(city=loc_d["city"], state=loc_d["state"], country="India", 
                           latitude=loc_d["lat"], longitude=loc_d["lng"])
            db.add(loc)
            db.flush()
        locations[loc.city] = loc

    # 2. Categories
    CATEGORIES = ["Plastic", "Metal", "Paper", "Glass", "E-waste", "Textile", "Rubber", "Wood"]
    categories = {}
    for c_name in CATEGORIES:
        cat = db.query(MaterialCategory).filter_by(name=c_name).first()
        if not cat:
            cat = MaterialCategory(
                name=c_name, 
                description=f"Recyclable {c_name} materials and scraps."
            )
            db.add(cat)
            db.flush()
        categories[c_name] = cat
        
    db.commit()
    logger.info("[Database] Successfully seeded Locations and Categories. Demo accounts skipped.")
