"""Shared pytest fixtures: an isolated in-memory SQLite DB per test."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.infrastructure.db import models  # noqa: F401  ensure models register on Base.metadata


def _memory_engine():
    # StaticPool keeps every session on the same in-memory connection, so the
    # schema created here is still there when the app's request sessions run.
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture()
def db_session():
    engine = _memory_engine()
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """TestClient wired to the in-memory DB, with the seeding startup hook off."""
    from app.main import app

    app.dependency_overrides[get_db] = lambda: db_session
    startup_hooks = list(app.router.on_startup)
    app.router.on_startup.clear()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.router.on_startup.extend(startup_hooks)
        app.dependency_overrides.clear()
