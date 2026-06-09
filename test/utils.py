from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from fastapi.testclient import TestClient
import pytest
from models import Todos, Users
import main
from routers.auth import bcrypt_context


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass= StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind = engine)


# Dependency overrides 
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'BiswajitTest', 'id': 1, 'user_role': 'admin'}


# The test client and actual test:
client = TestClient(main.app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title = "Learn To Code",
        description = "Need to practice everyday",
        priority = 4,
        complete = False,
        owner_id = 1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()



@pytest.fixture
def test_user():
    user = Users(
        username ="Biswajit",
        email ="biswajit@test.com",
        first_name = "Biswajit",
        last_name = "Biswas",
        hashed_password = bcrypt_context.hash("testpassword"),
        role = "admin",
        phone_number = "(111)-111-1111",

    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
