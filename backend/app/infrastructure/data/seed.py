"""
Idempotent seed of the Iran gazetteer + curated tourist places.

Called from app startup (development) and from scripts/seed_data.py.
Never overwrites provider-backed rows that already exist.
"""
from sqlalchemy.orm import Session

from app.infrastructure.data.iran_gazetteer import iter_cities
from app.infrastructure.data.iran_places import DINING_PLACES, LODGING_PLACES, TOURIST_PLACES, commons_image_url
from app.infrastructure.data.place_catalog import dump_place_catalog
from app.infrastructure.data.place_details import curated_description
from app.infrastructure.db.models import City, Place, Province
from app.shared.place_kind import PlaceKind


def _source_id(province_en: str, city_en: str) -> str:
    province_slug = province_en.lower().replace(" ", "-")
    city_slug = city_en.lower().replace(" ", "-")
    return f"ir:{province_slug}:{city_slug}"


def seed_iran_destinations(db: Session) -> tuple[int, int]:
    created_cities = 0
    created_places = 0
    cities_by_name: dict[str, City] = {}

    for province_fa, province_en, city_fa, city_en, lat, lng in iter_cities():
        province = db.query(Province).filter_by(name=province_fa).one_or_none()
        if not province:
            province = Province(name=province_fa, name_en=province_en)
            db.add(province)
            db.flush()
        elif not province.name_en:
            province.name_en = province_en

        source_id = _source_id(province_en, city_en)
        city = (
            db.query(City)
            .filter_by(name=city_fa, province_id=province.id)
            .one_or_none()
        )
        if not city:
            city = City(
                name=city_fa,
                name_en=city_en,
                province_id=province.id,
                latitude=lat,
                longitude=lng,
                source_provider_id=source_id,
            )
            db.add(city)
            db.flush()
            created_cities += 1
        else:
            if city.latitude is None:
                city.latitude = lat
            if city.longitude is None:
                city.longitude = lng
            if not city.name_en:
                city.name_en = city_en
            if not city.source_provider_id or city.source_provider_id == "seed":
                city.source_provider_id = source_id

        cities_by_name.setdefault(city_fa, city)

    created_places += _seed_place_group(db, cities_by_name, TOURIST_PLACES, PlaceKind.ATTRACTION)
    created_places += _seed_place_group(db, cities_by_name, LODGING_PLACES, PlaceKind.LODGING)
    created_places += _seed_place_group(db, cities_by_name, DINING_PLACES, PlaceKind.DINING)

    db.commit()
    return created_cities, created_places


def _seed_place_group(
    db: Session,
    cities_by_name: dict[str, City],
    items: list[dict],
    kind: PlaceKind,
) -> int:
    created = 0
    for item in items:
        city = cities_by_name.get(item["city"])
        if not city:
            continue
        exists = db.query(Place).filter_by(name=item["name"], city_id=city.id).one_or_none()
        image_url = commons_image_url(item.get("image"))
        description = curated_description(item["name"]) or item["description"]
        catalog_json = dump_place_catalog(item.get("catalog"))
        if exists:
            if exists.source_provider_id and exists.source_provider_id.startswith("seed:"):
                exists.description = description
                exists.category = item["category"]
                exists.estimated_entrance_fee = item["fee"]
                exists.opening_hours = item["hours"]
                exists.kind = kind.value
                exists.latitude = item["lat"]
                exists.longitude = item["lng"]
                if catalog_json:
                    exists.details_json = catalog_json
                if item.get("address"):
                    exists.address = item["address"]
                if image_url:
                    exists.image = image_url
            else:
                if not exists.kind:
                    exists.kind = kind.value
                if not exists.image and image_url:
                    exists.image = image_url
                if not exists.address and item.get("address"):
                    exists.address = item["address"]
            continue
        db.add(
            Place(
                name=item["name"],
                description=description,
                category=item["category"],
                city_id=city.id,
                latitude=item["lat"],
                longitude=item["lng"],
                estimated_entrance_fee=item["fee"],
                opening_hours=item["hours"],
                address=item.get("address"),
                image=image_url,
                kind=kind.value,
                details_json=catalog_json,
                source_provider_id=f"seed:{kind.value}:{item['name']}",
            )
        )
        created += 1
    return created
