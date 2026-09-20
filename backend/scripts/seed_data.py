"""
Seed script — populates the local database with Iranian provinces, cities,
and curated tourist places so the app is demoable without a live Neshan
API key.

Run with:
    python -m scripts.seed_data
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, SessionLocal, engine
from app.infrastructure.data.seed import seed_iran_destinations


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        created_cities, created_places = seed_iran_destinations(db)
        print(f"Seed complete: {created_cities} cities, {created_places} places added.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
