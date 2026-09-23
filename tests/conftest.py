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


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="module")
def admin_token(db_session):
    admin = db_session.query(User).filter(User.email == "admin@circulareconomy.com").first()
    return create_access_token(data={"sub": admin.id, "role": admin.role})


@pytest.fixture(scope="module")
def seller_token(db_session):
    seller = db_session.query(User).filter(User.email == "seller@ecotextiles.com").first()
    return create_access_token(data={"sub": seller.id, "role": seller.role})


@pytest.fixture(scope="module")
def buyer_token(db_session):
    buyer = db_session.query(User).filter(User.email == "buyer@greenplast.com").first()
    return create_access_token(data={"sub": buyer.id, "role": buyer.role})
