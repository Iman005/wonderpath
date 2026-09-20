"""
SummaryService — assembles the read-only trip summary. This module is
intentionally read-only: it has no repository of its own and performs
no writes; it composes data already owned by the Trip module.
"""
from app.modules.summary.dtos import SummaryDayOut, SummaryPlaceOut, SummaryStayOut, TripSummaryOut
from app.modules.trip.service import TripService
from app.shared.place_kind import coerce_place_kind, is_per_person


def _traveler_count(trip) -> int:
    raw = getattr(trip, "traveler_count", 1)
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return 1


class SummaryService:
    def __init__(self, trip_service: TripService) -> None:
        self.trip_service = trip_service

    def get_trip_summary(self, trip_id: str, owner_device_id: str) -> TripSummaryOut:
        trip = self.trip_service.get_trip(trip_id, owner_device_id)
        return self.build_from_trip(trip)

    def build_from_trip(self, trip) -> TripSummaryOut:
        travelers = _traveler_count(trip)

        day_summaries: list[SummaryDayOut] = []
        trip_total = 0.0

        for day in trip.days:
            places: list[SummaryPlaceOut] = []
            day_total = 0.0
            for tp in day.trip_places:
                place = tp.place
                kind = coerce_place_kind(getattr(place, "kind", None))
                unit = tp.custom_entrance_fee if tp.custom_entrance_fee is not None else place.estimated_entrance_fee
                line = None if unit is None else unit * (travelers if is_per_person(kind) else 1)
                if line:
                    day_total += line
                city = getattr(place, "city", None)
                places.append(
                    SummaryPlaceOut(
                        place_id=place.id,
                        name=place.name,
                        category=place.category,
                        city_name=getattr(city, "name", None) or "",
                        estimated_entrance_fee=line,
                        note=tp.note,
                        order_index=tp.order_index,
                        kind=kind.value,
                    )
                )
            day_summaries.append(
                SummaryDayOut(
                    trip_day_id=day.id,
                    day_number=day.day_number,
                    date=day.date,
                    places=places,
                    estimated_day_total=day_total,
                )
            )
            trip_total += day_total

        stay_rows: list[SummaryStayOut] = []
        lodging_total = 0.0
        stays = trip.stays if isinstance(getattr(trip, "stays", None), (list, tuple)) else []
        for stay in stays:
            place = getattr(stay, "place", None)
            city = getattr(place, "city", None) if place is not None else None
            total = None if stay.nightly_rate is None else stay.nightly_rate * stay.nights
            if total:
                lodging_total += total
            stay_rows.append(
                SummaryStayOut(
                    stay_id=stay.id,
                    place_id=stay.place_id,
                    name=getattr(place, "name", None) or "",
                    city_name=getattr(city, "name", None) if city is not None else None,
                    check_in_day_number=stay.check_in_day_number,
                    nights=stay.nights,
                    nightly_rate=stay.nightly_rate,
                    total=total,
                )
            )

        return TripSummaryOut(
            trip_id=trip.id,
            trip_name=trip.name,
            traveler_count=travelers,
            days=day_summaries,
            stays=stay_rows,
            estimated_trip_total=trip_total + lodging_total,
            lodging_total=lodging_total,
        )
