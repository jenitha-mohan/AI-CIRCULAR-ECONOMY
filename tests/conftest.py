import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.services.seed_service import seed_database
from backend.app.dependencies import create_access_token
from backend.app.models.user import User

# Use an in-memory SQLite database with static pool for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def _registered_test_users(client):
    """
    Register seller and buyer test users via the public API.
    Admin cannot be registered publicly (role validator blocks it),
    so the admin fixture is handled separately via direct DB insertion.
    """
    non_admin = [
        {
            "name": "Test Seller",
            "email": "seller@ecotextiles.com",
            "password": "Seller@1234",
            "role": "seller",
            "phone": "+91 9000000011",
            "organization": "EcoTextiles",
            "city": "Coimbatore",
            "state": "Tamil Nadu",
        },
        {
            "name": "Test Buyer",
            "email": "buyer@greenplast.com",
            "password": "Buyer@1234",
            "role": "buyer",
            "phone": "+91 9000000012",
            "organization": "GreenPlast",
            "city": "Chennai",
            "state": "Tamil Nadu",
        },
    ]
    tokens = {}
    for u in non_admin:
        res = client.post("/api/auth/register", json=u)
        if res.status_code == 200:
            tokens[u["email"]] = res.json()["access_token"]
        elif res.status_code == 409:
            login_res = client.post("/api/auth/login", json={"email": u["email"], "password": u["password"]})
            if login_res.status_code == 200:
                tokens[u["email"]] = login_res.json()["access_token"]

    # Seed baseline Material, Listing, BuyerRequirement, and Transaction for tests
    from backend.app.models.material import Material
    from backend.app.models.listing import Listing
    from backend.app.models.buyer_requirement import BuyerRequirement
    from backend.app.models.transaction import Transaction
    from datetime import datetime

    db = TestingSessionLocal()
    try:
        seller = db.query(User).filter(User.email == "seller@ecotextiles.com").first()
        buyer = db.query(User).filter(User.email == "buyer@greenplast.com").first()
        if seller and buyer:
            existing_mat = db.query(Material).filter(Material.seller_id == seller.id).first()
            if not existing_mat:
                mat = Material(
                    seller_id=seller.id,
                    material_type="Aluminum",
                    description="Industrial Aluminum Offcuts",
                    quantity_kg=500.0,
                    quality="High",
                    condition="Clean",
                    intended_purpose="Recycling",
                    status="available"
                )
                db.add(mat)
                db.flush()

                listing = Listing(
                    seller_id=seller.id,
                    material_id=mat.id,
                    quantity_available=500.0,
                    asking_price=190.0,
                    status="active"
                )
                db.add(listing)
                db.flush()

                req = BuyerRequirement(
                    buyer_id=buyer.id,
                    material_type="Aluminum",
                    min_quantity=100.0,
                    max_quantity=1000.0,
                    quality="High",
                    purpose="Recycling",
                    max_price_per_kg=200.0,
                    is_active=True
                )
                db.add(req)
                db.flush()

                txn = Transaction(
                    buyer_id=buyer.id,
                    seller_id=seller.id,
                    listing_id=listing.id,
                    material_type="Aluminum",
                    quantity_kg=100.0,
                    agreed_price=185.0,
                    total_amount=18500.0,
                    status="CONFIRMED",
                    co2_avoided_kg=900.0,
                    landfill_diverted_kg=95.0,
                    created_at=datetime.utcnow()
                )
                db.add(txn)
                db.commit()
    finally:
        db.close()

    return tokens


@pytest.fixture(scope="session")
def _admin_user_token(setup_test_db):
    """
    Create an admin user directly in the test DB (bypasses public role restriction)
    and return a JWT with role=admin for role-authorization tests.
    """
    from backend.app.dependencies import get_password_hash, create_access_token
    from backend.app.models.user import User

    db = TestingSessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@circulareconomy.com").first()
        if existing:
            token = create_access_token(data={"sub": existing.id, "role": existing.role})
            return token
        admin = User(
            name="Test Admin",
            email="admin@circulareconomy.com",
            password_hash=get_password_hash("Admin@1234"),
            role="admin",
            phone="+91 9000000010",
            organization="CircularEconomy Admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return create_access_token(data={"sub": admin.id, "role": admin.role})
    finally:
        db.close()


@pytest.fixture(scope="module")
def admin_token(_admin_user_token):
    return _admin_user_token


@pytest.fixture(scope="module")
def seller_token(_registered_test_users):
    return _registered_test_users.get("seller@ecotextiles.com")


@pytest.fixture(scope="module")
def buyer_token(_registered_test_users):
    return _registered_test_users.get("buyer@greenplast.com")
