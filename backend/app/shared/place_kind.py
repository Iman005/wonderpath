"""
PlaceKind — the discriminator that decides how a cached Place behaves in
the itinerary and in the budget.

`Place.estimated_entrance_fee` is a generic *reference cost* whose meaning
depends on this kind:

    ATTRACTION -> entrance ticket, per person
    DINING     -> typical cost of one meal, per person
    LODGING    -> nightly rate for the room/unit, for the whole group

Attraction and dining costs are therefore multiplied by the stop's
`TripPlace.party_size` (not trip traveler_count); lodging is not.
Budget code must go through `is_per_person` rather than testing the kind
inline, so adding a fourth kind later stays a one-line change.
"""
from enum import StrEnum


class PlaceKind(StrEnum):
    ATTRACTION = "attraction"
    LODGING = "lodging"
    DINING = "dining"


DEFAULT_PLACE_KIND = PlaceKind.ATTRACTION


def coerce_place_kind(value: object) -> PlaceKind:
    """Rows cached before `kind` existed read back as NULL — treat as attraction."""
    if isinstance(value, PlaceKind):
        return value
    try:
        return PlaceKind(str(value))
    except ValueError:
        return DEFAULT_PLACE_KIND


def is_per_person(kind: object) -> bool:
    return coerce_place_kind(kind) is not PlaceKind.LODGING
