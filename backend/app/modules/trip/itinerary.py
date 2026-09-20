"""Itinerary ordering shared by the map and destination distance origin."""


def stay_covers_day(stay, day_number: int) -> bool:
    check_in = getattr(stay, "check_in_day_number", None)
    nights = getattr(stay, "nights", 1) or 1
    if check_in is None:
        return False
    return check_in <= day_number < check_in + nights


def day_places_in_itinerary_order(trip, day) -> list:
    slots: list[tuple[int, object]] = []
    for tp in getattr(day, "trip_places", None) or []:
        place = getattr(tp, "place", None)
        if place is None:
            continue
        slots.append((getattr(tp, "order_index", 0) or 0, place))
    if getattr(trip, "stays", None):
        for stay in trip.stays:
            if not stay_covers_day(stay, day.day_number):
                continue
            place = getattr(stay, "place", None)
            if place is None:
                continue
            slots.append((getattr(stay, "sort_index", 0) or 0, place))
    slots.sort(key=lambda item: item[0])
    return [place for _, place in slots]


def last_place_before(trip, day_number: int):
    days = sorted(trip.days, key=lambda day: day.day_number)
    for day in reversed(days):
        if day.day_number >= day_number:
            continue
        places = day_places_in_itinerary_order(trip, day)
        if places:
            return places[-1]
    return None


def _coords(place) -> tuple[float, float] | None:
    lat = getattr(place, "latitude", None)
    lng = getattr(place, "longitude", None)
    if lat is None or lng is None:
        return None
    return float(lat), float(lng)


def search_origin_coords(trip, day_number: int | None) -> tuple[float, float] | None:
    """Origin for search distances: last selected stop, else trip origin.

    Same priority the day map uses: last place on the current day, otherwise
    the last place of previous days, otherwise the trip's home origin.
    """
    if day_number is not None:
        current = next((day for day in trip.days if day.day_number == day_number), None)
        if current is not None:
            here = day_places_in_itinerary_order(trip, current)
            if here:
                coords = _coords(here[-1])
                if coords is not None:
                    return coords
        previous = last_place_before(trip, day_number)
        if previous is not None:
            coords = _coords(previous)
            if coords is not None:
                return coords
    else:
        last = last_place_before(trip, 10**9)
        if last is not None:
            coords = _coords(last)
            if coords is not None:
                return coords
    if trip.origin_latitude is None or trip.origin_longitude is None:
        return None
    return trip.origin_latitude, trip.origin_longitude
