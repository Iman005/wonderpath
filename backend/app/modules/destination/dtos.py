"""Pydantic DTOs for the Destination module's API surface."""
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.infrastructure.data.place_catalog import parse_place_catalog
from app.infrastructure.data.place_details import extra_image_urls, visit_tip
from app.infrastructure.data.place_history import historical_era, notable_events, place_identity
from app.infrastructure.db.models import Place
from app.shared.place_kind import DEFAULT_PLACE_KIND, coerce_place_kind
from app.shared.text import shorten_description


class ProvinceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    name_en: str | None = None


class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    name_en: str | None = None
    province_id: str
    latitude: float | None = None
    longitude: float | None = None
    province_name: str | None = None
    distance_from_origin_km: float | None = None
    duration_from_origin_minutes: float | None = None
    distance_is_driving: bool = False

    @model_validator(mode="wrap")
    @classmethod
    def _attach_province_name(cls, value, handler):
        if hasattr(value, "id") and hasattr(value, "province_id"):
            province = getattr(value, "province", None)
            return handler(
                {
                    "id": value.id,
                    "name": value.name,
                    "name_en": value.name_en,
                    "province_id": value.province_id,
                    "latitude": value.latitude,
                    "longitude": value.longitude,
                    "province_name": getattr(province, "name", None) if province is not None else None,
                    "distance_from_origin_km": getattr(value, "distance_from_origin_km", None),
                    "duration_from_origin_minutes": getattr(value, "duration_from_origin_minutes", None),
                    "distance_is_driving": bool(getattr(value, "distance_is_driving", False)),
                }
            )
        if isinstance(value, dict):
            value = {
                **value,
                "distance_from_origin_km": value.get("distance_from_origin_km"),
                "duration_from_origin_minutes": value.get("duration_from_origin_minutes"),
                "distance_is_driving": bool(value.get("distance_is_driving", False)),
            }
        return handler(value)


def to_city_out(
    city,
    *,
    distance_from_origin_km: float | None = None,
    duration_from_origin_minutes: float | None = None,
    distance_is_driving: bool = False,
) -> CityOut:
    province = getattr(city, "province", None)
    return CityOut(
        id=city.id,
        name=city.name,
        name_en=city.name_en,
        province_id=city.province_id,
        latitude=city.latitude,
        longitude=city.longitude,
        province_name=getattr(province, "name", None) if province is not None else None,
        distance_from_origin_km=distance_from_origin_km,
        duration_from_origin_minutes=duration_from_origin_minutes,
        distance_is_driving=distance_is_driving,
    )


class CatalogRoomOut(BaseModel):
    name: str
    price: float


class CatalogMenuItemOut(BaseModel):
    section: str
    name: str
    price: float


class PlaceCatalogOut(BaseModel):
    is_demo: bool = False
    stars: int | None = None
    amenities: list[str] = []
    rooms: list[CatalogRoomOut] = []
    menu: list[CatalogMenuItemOut] = []


class PlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    category: str | None = None
    city_id: str
    latitude: float
    longitude: float
    image: str | None = None
    address: str | None = None
    estimated_entrance_fee: float | None = None
    opening_hours: str | None = None
    extra_images: list[str] = []
    visit_tip: str | None = None
    kind: str = DEFAULT_PLACE_KIND.value
    catalog: PlaceCatalogOut | None = None
    distance_from_origin_km: float | None = None
    duration_from_origin_minutes: float | None = None
    distance_is_driving: bool = False

    @field_validator("description")
    @classmethod
    def _short_description(cls, value: str | None) -> str | None:
        return shorten_description(value)


class FeaturedPlaceOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    category: str | None = None
    image: str | None = None
    city_id: str
    city_name: str
    province_name: str | None = None


class PlaceDetailOut(BaseModel):
    """Full place payload for the detail modal — description is not truncated."""

    id: str
    name: str
    description: str | None = None
    category: str | None = None
    city_id: str
    latitude: float
    longitude: float
    image: str | None = None
    address: str | None = None
    estimated_entrance_fee: float | None = None
    opening_hours: str | None = None
    extra_images: list[str] = []
    visit_tip: str | None = None
    historical_era: str | None = None
    identity: str | None = None
    notable_events: list[str] = []
    city_name: str | None = None
    province_name: str | None = None
    kind: str = DEFAULT_PLACE_KIND.value
    catalog: PlaceCatalogOut | None = None


def _gallery_for(place: Place) -> list[str]:
    return extra_image_urls(place.name, place.image)


def _catalog_for(place: Place) -> PlaceCatalogOut | None:
    raw = parse_place_catalog(getattr(place, "details_json", None))
    if not raw:
        return None
    return PlaceCatalogOut.model_validate(raw)


def to_place_out(
    place: Place,
    *,
    distance_from_origin_km: float | None = None,
    duration_from_origin_minutes: float | None = None,
    distance_is_driving: bool = False,
) -> PlaceOut:
    return PlaceOut(
        id=place.id,
        name=place.name,
        description=place.description,
        category=place.category,
        city_id=place.city_id,
        latitude=place.latitude,
        longitude=place.longitude,
        image=place.image,
        address=place.address,
        estimated_entrance_fee=place.estimated_entrance_fee,
        opening_hours=place.opening_hours,
        extra_images=_gallery_for(place),
        visit_tip=visit_tip(place.name),
        kind=coerce_place_kind(place.kind).value,
        catalog=_catalog_for(place),
        distance_from_origin_km=distance_from_origin_km,
        duration_from_origin_minutes=duration_from_origin_minutes,
        distance_is_driving=distance_is_driving,
    )


def to_place_detail_out(
    place: Place,
    *,
    description: str | None = None,
    extra_images: list[str] | None = None,
) -> PlaceDetailOut:
    city = getattr(place, "city", None)
    province = getattr(city, "province", None) if city is not None else None
    gallery = extra_images if extra_images is not None else _gallery_for(place)
    return PlaceDetailOut(
        id=place.id,
        name=place.name,
        description=description if description is not None else place.description,
        category=place.category,
        city_id=place.city_id,
        latitude=place.latitude,
        longitude=place.longitude,
        image=place.image,
        address=place.address,
        estimated_entrance_fee=place.estimated_entrance_fee,
        opening_hours=place.opening_hours,
        extra_images=gallery,
        visit_tip=visit_tip(place.name),
        historical_era=historical_era(place.name),
        identity=place_identity(place.name),
        notable_events=notable_events(place.name),
        city_name=getattr(city, "name", None) if city is not None else None,
        province_name=getattr(province, "name", None) if province is not None else None,
        kind=coerce_place_kind(place.kind).value,
        catalog=_catalog_for(place),
    )
