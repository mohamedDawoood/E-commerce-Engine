import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db.session import get_db
from app.main import app, Base
from app.api.deps import get_current_user , user_dependency , admin_user
from app.models.user import User
from app.models.product import Product
from app.models.order import Order

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback() 
    connection.close()

from app.core.security import get_password_hash 

@pytest.fixture
def client(db, test_user): 
    def override_get_db():
        yield db


    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[user_dependency] = lambda: test_user
    app.dependency_overrides[admin_user] = lambda: test_user

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):

    hashed_pwd = get_password_hash("testpassword123") 
    user = User(
        username="testuser", 
        email="testuser@example.com",
        role="admin",
        hashed_password=hashed_pwd, 
        phone_number="1234567890",
        first_name="Test",
        last_name="User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@pytest.fixture
def test_product(db, test_user):
    product = Product(
        name="Test Product",
        description="A product for testing",
        price=9.99,
        stock=100,
        image_url="http://example.com/image.jpg",
        owner_id=test_user.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@pytest.fixture
def test_order(db, test_user, test_product):
    order = Order(
        user_id=test_user.id,
        product_id=test_product.id,
        quantity=2,
        total_price=19.98
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order