"""
Test configuration — SQLite in-memory, patching PG-specific types.
"""
import uuid as _uuid_mod
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Text, String, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import ARRAY, INET
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database.session import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _uuid_str(_ctx=None):
    return str(_uuid_mod.uuid4())


def _patch_pg_types():
    """Replace PG-only column types with SQLite-compatible equivalents."""
    for table in Base.metadata.tables.values():
        for col in table.columns:
            t = col.type
            if isinstance(t, ARRAY):
                col.type = Text()
            elif isinstance(t, INET):
                col.type = Text()
            elif isinstance(t, PG_UUID):
                col.type = String(36)
                if col.default is not None:
                    col.default.arg = _uuid_str
                    col.default.is_scalar = False
                    col.default.is_callable = True


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    _patch_pg_types()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Ensure list values stored to the ARRAY-patched Text column are JSON-encoded
# ---------------------------------------------------------------------------
from sqlalchemy.types import TypeDecorator
import json as _json


class _JsonList(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return _json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return _json.loads(value)
        return value


# Monkey-patch the Offer model's valid_days column type after table creation
from app.models.models import Offer as _Offer
_Offer.valid_days.property.columns[0].type = _JsonList()
