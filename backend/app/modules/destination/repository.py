"""
DestinationRepository — data access only. No business rules, no caching
policy (that lives in app/infrastructure/cache), no HTTP concerns.
"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.db.models import City, Place, Province
from app.shared.place_kind import PlaceKind


class DestinationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # --- Province ---
    def get_or_create_province(self, name: str) -> Province:
        existing = self.db.execute(select(Province).where(Province.name == name)).scalar_one_or_none()
        if existing:
            return existing
        province = Province(name=name)
        self.db.add(province)
        self.db.flush()
        return province

    # --- City ---
    def search_cities_by_name(self, query: str, limit: int = 40) -> list[City]:
        pattern = f"%{query}%"
        stmt = (
            select(City)
            .join(Province)
            .options(joinedload(City.province))
            .where(
                or_(
                    City.name.ilike(pattern),
                    City.name_en.ilike(pattern),
                    Province.name.ilike(pattern),
                    Province.name_en.ilike(pattern),
                )
            )
            .order_by(City.name)
            .limit(limit)
        )
        return list(self.db.execute(stmt).unique().scalars().all())

    def get_city(self, city_id: str) -> City | None:
        stmt = select(City).options(joinedload(City.province)).where(City.id == city_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def list_featured_attractions(self, limit: int = 12) -> list[Place]:
        stmt = (
            select(Place)
            .options(joinedload(Place.city).joinedload(City.province))
            .where(Place.kind == PlaceKind.ATTRACTION.value)
            .where(Place.image.is_not(None))
            .where(Place.image != "")
            .order_by(Place.name)
        )
        places = list(self.db.execute(stmt).unique().scalars().all())
        picked: list[Place] = []
        seen_cities: set[str] = set()
        for place in places:
            if place.city_id in seen_cities:
                continue
            seen_cities.add(place.city_id)
            picked.append(place)
            if len(picked) >= limit:
                break
        if len(picked) < limit:
            for place in places:
                if place in picked:
                    continue
                picked.append(place)
                if len(picked) >= limit:
                    break
        return picked

    def get_city_by_source_id(self, source_provider_id: str) -> City | None:
        stmt = select(City).where(City.source_provider_id == source_provider_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert_city(self, city: City) -> City:
        self.db.add(city)
        self.db.flush()
        return city

    def list_all_cities(self) -> list[City]:
        stmt = select(City).options(joinedload(City.province)).order_by(City.name)
        return list(self.db.execute(stmt).unique().scalars().all())

    # --- Place ---
    def list_places_for_city(self, city_id: str, kind: str | None = None) -> list[Place]:
        stmt = select(Place).where(Place.city_id == city_id)
        if kind is not None:
            stmt = stmt.where(Place.kind == kind)
        return list(self.db.execute(stmt).scalars().all())

    def get_place(self, place_id: str) -> Place | None:
        stmt = (
            select(Place)
            .options(joinedload(Place.city).joinedload(City.province))
            .where(Place.id == place_id)
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_place_by_source_id(self, source_provider_id: str) -> Place | None:
        stmt = select(Place).where(Place.source_provider_id == source_provider_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert_place(self, place: Place) -> Place:
        self.db.add(place)
        self.db.flush()
        return place
