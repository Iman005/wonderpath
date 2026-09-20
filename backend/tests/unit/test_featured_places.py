from unittest.mock import MagicMock

from app.infrastructure.db.models import City, Place, Province
from app.modules.destination.repository import DestinationRepository
from app.modules.destination.service import DestinationService
from app.shared.place_kind import PlaceKind


def test_featured_places_prefer_one_per_city(db_session):
    province = Province(name="فارس")
    shiraz = City(name="شیراز", province=province, latitude=29.6, longitude=52.5)
    isfahan = City(name="اصفهان", province=province, latitude=32.6, longitude=51.6)
    db_session.add_all(
        [
            Place(
                name="حافظیه",
                city=shiraz,
                latitude=29.6,
                longitude=52.5,
                image="https://example.com/hafez.jpg",
                kind=PlaceKind.ATTRACTION.value,
            ),
            Place(
                name="سعدیه",
                city=shiraz,
                latitude=29.62,
                longitude=52.58,
                image="https://example.com/saadi.jpg",
                kind=PlaceKind.ATTRACTION.value,
            ),
            Place(
                name="نقش جهان",
                city=isfahan,
                latitude=32.65,
                longitude=51.67,
                image="https://example.com/naqsh.jpg",
                kind=PlaceKind.ATTRACTION.value,
            ),
        ]
    )
    db_session.commit()

    service = DestinationService(DestinationRepository(db_session), cache_sync=MagicMock())
    featured = service.list_featured_places(limit=2)
    names = {item.name for item in featured}
    cities = {item.city_name for item in featured}
    assert len(featured) == 2
    assert "نقش جهان" in names
    assert cities == {"شیراز", "اصفهان"}
