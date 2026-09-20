"""
OpenStreetMap / Overpass fallback for IPlaceDataProvider.

Used when Neshan is unconfigured or returns nothing, so every gazetteer
city can still surface nearby POIs — sightseeing, lodging, or places to
eat, depending on the requested PlaceKind. City search is served from the
local Iran gazetteer (no network).

OSM has good Persian-named coverage of Iranian hotels and restaurants but
carries no prices, so every result comes back with a null reference cost
for the traveler to fill in.
"""
import logging

import httpx

from app.infrastructure.data.iran_gazetteer import iter_cities
from app.modules.destination.interfaces import IPlaceDataProvider, ProviderCity, ProviderPlace
from app.shared.exceptions import ExternalProviderError
from app.shared.place_kind import DEFAULT_PLACE_KIND, PlaceKind

logger = logging.getLogger("wanderpath.providers.osm_place")

_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
_TIMEOUT_SECONDS = 14.0
_SEARCH_RADIUS_METERS = 12_000
_MAX_PLACES = 24
_USER_AGENT = "WanderPath/1.0 (domestic trip planner)"

# Overpass filter clauses per kind. Each entry is a tag key plus the values
# worth surfacing; the query is assembled with the search radius per clause.
_FILTERS_BY_KIND: dict[PlaceKind, tuple[tuple[str, str], ...]] = {
    PlaceKind.ATTRACTION: (
        ("tourism", "attraction|museum|gallery|viewpoint|theme_park|zoo|artwork"),
        ("historic", "monument|castle|ruins|palace|archaeological_site|mosque|tomb"),
    ),
    PlaceKind.LODGING: (
        ("tourism", "hotel|guest_house|hostel|motel|apartment|chalet"),
    ),
    PlaceKind.DINING: (
        ("amenity", "restaurant|cafe|fast_food|food_court|ice_cream"),
    ),
}

_CATEGORY_BY_TAG = {
    "museum": "موزه",
    "attraction": "جاذبه",
    "gallery": "گالری",
    "viewpoint": "چشم‌انداز",
    "theme_park": "تفریحی",
    "zoo": "باغ‌وحش",
    "artwork": "هنری",
    "monument": "یادمان",
    "castle": "تاریخی",
    "ruins": "باستانی",
    "palace": "تاریخی",
    "archaeological_site": "باستانی",
    "mosque": "مذهبی",
    "tomb": "تاریخی",
    "place_of_worship": "مذهبی",
    "hotel": "هتل",
    "guest_house": "اقامتگاه",
    "hostel": "هاستل",
    "motel": "مُتل",
    "apartment": "آپارتمان",
    "chalet": "ویلا",
    "restaurant": "رستوران",
    "cafe": "کافه",
    "fast_food": "فست‌فود",
    "food_court": "فودکورت",
    "ice_cream": "بستنی و آبمیوه",
}

_FALLBACK_CATEGORY_BY_KIND = {
    PlaceKind.LODGING: "اقامتگاه",
    PlaceKind.DINING: "رستوران",
}


class OsmPlaceDataProvider(IPlaceDataProvider):
    def search_cities(self, query: str) -> list[ProviderCity]:
        needle = (query or "").strip().casefold()
        if not needle:
            return []
        matches: list[ProviderCity] = []
        for province_fa, province_en, city_fa, city_en, lat, lng in iter_cities():
            haystacks = (city_fa, city_en, province_fa, province_en)
            if not any(needle in value.casefold() for value in haystacks):
                continue
            matches.append(
                ProviderCity(
                    source_id=f"ir:{province_en.lower().replace(' ', '-')}:{city_en.lower().replace(' ', '-')}",
                    name=city_fa,
                    name_en=city_en,
                    province_name=province_fa,
                    latitude=lat,
                    longitude=lng,
                )
            )
            if len(matches) >= 40:
                break
        return matches

    def search_places(
        self,
        city_source_id: str,
        query: str | None = None,
        city_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        kind: PlaceKind = DEFAULT_PLACE_KIND,
    ) -> list[ProviderPlace]:
        lat, lng = latitude, longitude
        if lat is None or lng is None:
            lat, lng = self._coords_for_source(city_source_id, city_name)
        if lat is None or lng is None:
            raise ExternalProviderError("City coordinates are required for OSM place search.")

        clauses = "".join(
            f'nwr["{key}"~"{values}"](around:{_SEARCH_RADIUS_METERS},{lat},{lng});'
            for key, values in _FILTERS_BY_KIND.get(kind, _FILTERS_BY_KIND[PlaceKind.ATTRACTION])
        )
        ql = f"[out:json][timeout:12];({clauses});out center {_MAX_PLACES};"
        try:
            with httpx.Client(timeout=_TIMEOUT_SECONDS, headers={"User-Agent": _USER_AGENT}) as client:
                response = client.post(_OVERPASS_URL, data={"data": ql})
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ExternalProviderError(f"OpenStreetMap place search unavailable: {exc}") from exc

        elements = payload.get("elements") or []
        places: list[ProviderPlace] = []
        seen_names: set[str] = set()
        needle = (query or "").strip()
        for element in elements:
            tags = element.get("tags") or {}
            name = tags.get("name:fa") or tags.get("name")
            if not name or name in seen_names:
                continue
            if needle and needle not in name:
                continue
            center = element.get("center") or element
            elat = center.get("lat")
            elng = center.get("lon")
            if elat is None or elng is None:
                continue
            seen_names.add(name)
            places.append(
                ProviderPlace(
                    source_id=f"osm:{element.get('type', 'node')}/{element.get('id')}",
                    name=name,
                    description=tags.get("description:fa") or tags.get("description"),
                    category=self._category(tags, kind),
                    latitude=float(elat),
                    longitude=float(elng),
                    image=None,
                    estimated_entrance_fee=None,
                    opening_hours=tags.get("opening_hours"),
                    kind=kind,
                )
            )
            if len(places) >= _MAX_PLACES:
                break
        return places

    def get_place_details(self, place_source_id: str) -> ProviderPlace | None:
        return None

    @staticmethod
    def _category(tags: dict, kind: PlaceKind = DEFAULT_PLACE_KIND) -> str | None:
        for key in ("tourism", "historic", "amenity"):
            value = tags.get(key)
            if value in _CATEGORY_BY_TAG:
                return _CATEGORY_BY_TAG[value]
        fallback = _FALLBACK_CATEGORY_BY_KIND.get(kind)
        if fallback:
            return fallback
        if tags.get("tourism"):
            return "جاذبه"
        if tags.get("historic"):
            return "تاریخی"
        return None

    @staticmethod
    def _coords_for_source(source_id: str, city_name: str | None) -> tuple[float | None, float | None]:
        for _province_fa, province_en, city_fa, city_en, lat, lng in iter_cities():
            slug = f"ir:{province_en.lower().replace(' ', '-')}:{city_en.lower().replace(' ', '-')}"
            if source_id == slug or (city_name and city_name == city_fa):
                return lat, lng
        return None, None
