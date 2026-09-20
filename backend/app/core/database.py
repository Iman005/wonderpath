"""
SQLAlchemy engine/session wiring. This is the only place that knows how to
talk to the database connection itself — everything else depends on the
`get_db` dependency, never on the engine directly.
"""
from collections.abc import Generator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False, "timeout": 30} if _is_sqlite else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)

if _is_sqlite:

    @event.listens_for(engine, "connect")
    def _sqlite_enable_wal(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_sqlite_dev_columns() -> None:
    """create_all will not ALTER existing SQLite tables — add new columns/tables."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "trips" not in table_names:
        return
    columns = {column["name"] for column in inspector.get_columns("trips")}
    if "budget_cap" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE trips ADD COLUMN budget_cap FLOAT"))
            if "budget_ceiling" in columns:
                conn.execute(text("UPDATE trips SET budget_cap = budget_ceiling WHERE budget_cap IS NULL"))
    if "trip_expenses" not in inspector.get_table_names():
        from app.infrastructure.db.models import TripExpense

        TripExpense.__table__.create(bind=engine)
        if "trip_side_expenses" in inspector.get_table_names():
            with engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        INSERT INTO trip_expenses (id, trip_id, label, amount, created_at)
                        SELECT id, trip_id, label, amount, created_at FROM trip_side_expenses
                        """
                    )
                )
    if "end_date" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE trips ADD COLUMN end_date DATETIME"))
    if "traveler_count" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE trips ADD COLUMN traveler_count INTEGER DEFAULT 1"))
            conn.execute(text("UPDATE trips SET traveler_count = 1 WHERE traveler_count IS NULL"))
    place_columns = {column["name"] for column in inspector.get_columns("places")}
    if "kind" not in place_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE places ADD COLUMN kind VARCHAR(20) DEFAULT 'attraction'"))
            conn.execute(text("UPDATE places SET kind = 'attraction' WHERE kind IS NULL"))
    if "details_json" not in place_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE places ADD COLUMN details_json TEXT"))
    if "users" not in inspector.get_table_names():
        from app.infrastructure.db.models import User

        User.__table__.create(bind=engine)
    if "trip_stays" not in inspector.get_table_names():
        from app.infrastructure.db.models import TripStay

        TripStay.__table__.create(bind=engine)
    else:
        stay_columns = {column["name"] for column in inspector.get_columns("trip_stays")}
        if "sort_index" not in stay_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE trip_stays ADD COLUMN sort_index INTEGER DEFAULT 0"))
                conn.execute(text("UPDATE trip_stays SET sort_index = 0 WHERE sort_index IS NULL"))
    if "users" in inspector.get_table_names():
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "password_hash" not in user_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
    if "trip_notes" not in inspector.get_table_names():
        from app.infrastructure.db.models import TripNote

        TripNote.__table__.create(bind=engine)
    if "packing_lists" not in inspector.get_table_names():
        from app.infrastructure.db.models import PackingList

        PackingList.__table__.create(bind=engine)
    if "packing_items" not in inspector.get_table_names():
        from app.infrastructure.db.models import PackingItem

        PackingItem.__table__.create(bind=engine)
    if "trip_places" in inspector.get_table_names():
        trip_place_columns = {column["name"] for column in inspector.get_columns("trip_places")}
        if "party_size" not in trip_place_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE trip_places ADD COLUMN party_size INTEGER DEFAULT 1"))
                conn.execute(text("UPDATE trip_places SET party_size = 1 WHERE party_size IS NULL"))
    if "trip_stays" in inspector.get_table_names():
        stay_columns = {column["name"] for column in inspector.get_columns("trip_stays")}
        if "guest_count" not in stay_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE trip_stays ADD COLUMN guest_count INTEGER DEFAULT 1"))
                conn.execute(text("UPDATE trip_stays SET guest_count = 1 WHERE guest_count IS NULL"))
    if "note_attachments" not in inspector.get_table_names():
        from app.infrastructure.db.models import NoteAttachment

        NoteAttachment.__table__.create(bind=engine)
    if "share_token" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE trips ADD COLUMN share_token VARCHAR(64)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_trips_share_token ON trips (share_token)"))
