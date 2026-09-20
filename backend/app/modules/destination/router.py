"""Destination controller — HTTP layer only, no business logic here."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.destination.dependencies import get_destination_service
from app.modules.destination.dtos import CityOut, FeaturedPlaceOut, PlaceDetailOut, PlaceOut
from app.modules.destination.service import DestinationService
from app.modules.identity.dependencies import get_current_device_id
from app.shared.place_kind import DEFAULT_PLACE_KIND, PlaceKind

router = APIRouter(tags=["Destination"])


@router.get("/cities", response_model=list[CityOut])
def search_cities(
    q: str = Query(default="", description="City name search term (Persian or English)"),
    trip_id: str | None = Query(default=None, description="Optional trip id for origin-relative distances"),
    day_number: int | None = Query(default=None, description="Optional trip day; distances use last stop before this day"),
    service: DestinationService = Depends(get_destination_service),
    owner_device_id: str = Depends(get_current_device_id),
    db: Session = Depends(get_db),
):
    cities = service.search_cities(
        q, trip_id=trip_id, owner_device_id=owner_device_id, day_number=day_number
    )
    db.commit()
    return cities


@router.get("/cities/{city_id}", response_model=CityOut)
def get_city(
    city_id: str,
    service: DestinationService = Depends(get_destination_service),
):
    return service.get_city_out(city_id)


@router.get("/places/featured", response_model=list[FeaturedPlaceOut])
def list_featured_places(
    service: DestinationService = Depends(get_destination_service),
):
    return service.list_featured_places()


@router.get("/cities/{city_id}/places", response_model=list[PlaceOut])
def list_places_for_city(
    city_id: str,
    trip_id: str | None = Query(default=None, description="Optional trip id for origin-relative driving metrics"),
    kind: PlaceKind = Query(default=DEFAULT_PLACE_KIND, description="attraction, lodging, or dining"),
    day_number: int | None = Query(default=None, description="Optional trip day; distances use last stop before this day"),
    service: DestinationService = Depends(get_destination_service),
    owner_device_id: str = Depends(get_current_device_id),
    db: Session = Depends(get_db),
):
    places = service.list_places_for_city(
        city_id,
        trip_id=trip_id,
        owner_device_id=owner_device_id,
        kind=kind,
        day_number=day_number,
    )
    db.commit()
    return places


@router.get("/places/{place_id}", response_model=PlaceDetailOut)
def get_place_details(
    place_id: str,
    service: DestinationService = Depends(get_destination_service),
    db: Session = Depends(get_db),
):
    details = service.get_place_details(place_id)
    db.commit()
    return details
