"""
Trip controller — HTTP layer only.

Split into two routers because the API contract exposes two resource
roots: /trips/... and /trip-days/.../places, matching the spec's API
contract section exactly.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.identity.dependencies import get_current_device_id
from app.modules.trip.dependencies import get_trip_service
from app.modules.trip.dtos import (
    DayItineraryReorder,
    TripCreate,
    TripDayCreate,
    TripDaysBulkCreate,
    TripDayOut,
    TripOut,
    TripPlaceCreate,
    TripPlaceOut,
    TripPlaceReorder,
    TripPlaceUpdate,
    TripUpdate,
)
from app.modules.trip.service import TripService

trips_router = APIRouter(prefix="/trips", tags=["Trip"])
trip_days_router = APIRouter(prefix="/trip-days", tags=["Trip"])


# --- Trip CRUD ---

@trips_router.post("", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    trip = service.create_trip(
        payload.name,
        device_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        origin_latitude=payload.origin_latitude,
        origin_longitude=payload.origin_longitude,
        origin_label=payload.origin_label,
        budget_cap=payload.budget_cap,
        traveler_count=payload.traveler_count,
    )
    db.commit()
    db.refresh(trip)
    return trip


@trips_router.get("/{trip_id}", response_model=TripOut)
def get_trip(
    trip_id: str,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
):
    return service.get_trip(trip_id, device_id)


@trips_router.put("/{trip_id}", response_model=TripOut)
def update_trip(
    trip_id: str,
    payload: TripUpdate,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    trip = service.update_trip(trip_id, device_id, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(trip)
    return trip


@trips_router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: str,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    service.delete_trip(trip_id, device_id)
    db.commit()


# --- Trip Days ---

@trips_router.post("/{trip_id}/days", response_model=TripDayOut, status_code=status.HTTP_201_CREATED)
def add_trip_day(
    trip_id: str,
    payload: TripDayCreate,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    day = service.add_day(trip_id, device_id, payload.day_number, payload.date)
    db.commit()
    db.refresh(day)
    return day


@trips_router.post("/{trip_id}/days/bulk", response_model=list[TripDayOut], status_code=status.HTTP_201_CREATED)
def add_trip_days_bulk(
    trip_id: str,
    payload: TripDaysBulkCreate,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    days = service.add_days_bulk(trip_id, device_id, payload.count)
    db.commit()
    for day in days:
        db.refresh(day)
    return days


@trips_router.delete("/{trip_id}/days/last", status_code=status.HTTP_204_NO_CONTENT)
def remove_last_trip_day(
    trip_id: str,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    service.remove_last_day(trip_id, device_id)
    db.commit()


@trips_router.delete("/{trip_id}/days/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_trip_day(
    trip_id: str,
    day_id: str,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    service.remove_day(trip_id, device_id, day_id)
    db.commit()


# --- Trip Day Places ---

@trip_days_router.post("/{trip_day_id}/places", response_model=TripPlaceOut, status_code=status.HTTP_201_CREATED)
def add_place_to_day(
    trip_day_id: str,
    payload: TripPlaceCreate,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    trip_place = service.add_place_to_day(
        trip_day_id,
        device_id,
        payload.place_id,
        payload.note,
        payload.custom_entrance_fee,
        allow_duplicate=payload.allow_duplicate,
        party_size=payload.party_size,
    )
    db.commit()
    db.refresh(trip_place)
    # Eagerly resolve place so TripPlaceOut can expose name/kind.
    _ = trip_place.place
    return trip_place


@trip_days_router.put("/{trip_day_id}/places/reorder", response_model=list[TripPlaceOut])
def reorder_places(
    trip_day_id: str,
    payload: TripPlaceReorder,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    result = service.reorder_places(trip_day_id, device_id, payload.ordered_trip_place_ids)
    db.commit()
    return result


@trip_days_router.put("/{trip_day_id}/itinerary", status_code=status.HTTP_204_NO_CONTENT)
def reorder_day_itinerary(
    trip_day_id: str,
    payload: DayItineraryReorder,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    service.reorder_day_itinerary(
        trip_day_id,
        device_id,
        [(item.kind, item.id) for item in payload.items],
    )
    db.commit()


@trip_days_router.put("/{trip_day_id}/places/{place_id}", response_model=TripPlaceOut)
def update_place_on_day(
    trip_day_id: str,
    place_id: str,
    payload: TripPlaceUpdate,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    trip_place = service.update_place_fee(
        trip_day_id,
        place_id,
        device_id,
        payload.custom_entrance_fee,
        party_size=payload.party_size,
    )
    db.commit()
    db.refresh(trip_place)
    return trip_place


@trip_days_router.delete("/{trip_day_id}/places/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_place_from_day(
    trip_day_id: str,
    place_id: str,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    service.remove_place(trip_day_id, place_id, device_id)
    db.commit()


@trip_days_router.delete("/{trip_day_id}/stops/{trip_place_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_trip_place_from_day(
    trip_day_id: str,
    trip_place_id: str,
    device_id: str = Depends(get_current_device_id),
    service: TripService = Depends(get_trip_service),
    db: Session = Depends(get_db),
):
    service.remove_trip_place(trip_day_id, trip_place_id, device_id)
    db.commit()
