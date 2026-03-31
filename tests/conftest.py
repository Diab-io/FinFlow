import os
import pytest
from dotenv import load_dotenv
load_dotenv()
from app.main import app
from app.core.database import Base, get_db
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URI = os.getenv('TEST_DATABASE_URL')
engine = create_engine(TEST_DATABASE_URI)
TestSession = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    def get_override_db():
        yield db
    
    app.dependency_overrides[get_db] = get_override_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def register_user(client):
    payload = {
        "username": "john.doe",
        "email": "test@example.com",
        "password": "example"
    }

    client.post('/api/auth/register', json=payload)
    return payload
