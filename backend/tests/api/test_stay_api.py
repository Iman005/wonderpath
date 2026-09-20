"""API-level checks for lodging stays."""
from datetime import date, timedelta

from app.infrastructure.db.models import City, Place, Province
from app.shared.place_kind import PlaceKind

DEVICE = {"X-Device-Id": "device-a"}
OTHER_DEVICE = {"X-Device-Id": "device-b"}
FUTURE_START_DATE = f"{date.today() + timedelta(days=1)}T00:00:00"


def _seed_place(db_session, *, name="Hotel", kind=PlaceKind.LODGING):
    city = City(name="Shiraz", province=Province(name="Fars"))
    place = Place(
        name=name,
        city=city,
        latitude=29.6,
        longitude=52.5,
        kind=kind.value,
        estimated_entrance_fee=None,
    )
    db_session.add(place)
    db_session.commit()
    return place


def _create_trip_with_days(client, day_count=3):
    trip = client.post(
        "/trips",
        json={"name": "Stay trip", "start_date": FUTURE_START_DATE, "traveler_count": 2},
        headers=DEVICE,
    )
    assert trip.status_code == 201, trip.text
    trip_id = trip.json()["id"]
    days = client.post(f"/trips/{trip_id}/days/bulk", json={"count": day_count}, headers=DEVICE)
    assert days.status_code == 201, days.text
    return trip.json(), days.json()


def test_stay_lifecycle_and_budget(client, db_session):
    hotel = _seed_place(db_session, name="هتل زندیه")
    trip, _days = _create_trip_with_days(client)
    trip_id = trip["id"]
    assert trip["traveler_count"] == 2

    created = client.post(
        f"/trips/{trip_id}/stays",
        json={"place_id": hotel.id, "check_in_day_number": 1, "nights": 2, "nightly_rate": 1_500_000},
        headers=DEVICE,
    )
    assert created.status_code == 201, created.text
    stay = created.json()
    assert stay["nights"] == 2
    assert stay["place_name"] == "هتل زندیه"

    fetched = client.get(f"/trips/{trip_id}", headers=DEVICE).json()
    assert len(fetched["stays"]) == 1

    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["lodging_total"] == 3_000_000
    assert budget["traveler_count"] == 2
    assert budget["grand_total"] == 3_000_000

    updated = client.put(
        f"/trips/{trip_id}/stays/{stay['id']}",
        json={"nightly_rate": 2_000_000, "nights": 2},
        headers=DEVICE,
    )
    assert updated.status_code == 200
    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["lodging_total"] == 4_000_000

    deleted = client.delete(f"/trips/{trip_id}/stays/{stay['id']}", headers=DEVICE)
    assert deleted.status_code == 204
    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["lodging_total"] == 0
    assert client.get(f"/trips/{trip_id}", headers=DEVICE).json()["stays"] == []


def test_stay_rejects_attraction_and_bad_check_in(client, db_session):
    attraction = _seed_place(db_session, name="حافظیه", kind=PlaceKind.ATTRACTION)
    hotel = _seed_place(db_session, name="هتل")
    trip, _days = _create_trip_with_days(client, day_count=2)
    trip_id = trip["id"]

    assert (
        client.post(
            f"/trips/{trip_id}/stays",
            json={"place_id": attraction.id, "check_in_day_number": 1, "nights": 1},
            headers=DEVICE,
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/trips/{trip_id}/stays",
            json={"place_id": hotel.id, "check_in_day_number": 9, "nights": 1},
            headers=DEVICE,
        ).status_code
        == 422
    )
    assert client.post(
        f"/trips/{trip_id}/stays",
        json={"place_id": hotel.id, "check_in_day_number": 1, "nights": 1},
        headers=OTHER_DEVICE,
    ).status_code == 403


def test_adding_lodging_as_day_stop_is_rejected(client, db_session):
    hotel = _seed_place(db_session)
    trip, days = _create_trip_with_days(client, day_count=1)
    response = client.post(
        f"/trip-days/{days[0]['id']}/places",
        json={"place_id": hotel.id},
        headers=DEVICE,
    )
    assert response.status_code == 422


def test_dining_fee_scales_with_party_size(client, db_session):
    restaurant = _seed_place(db_session, name="رستوران", kind=PlaceKind.DINING)
    restaurant.estimated_entrance_fee = 200_000
    db_session.commit()
    trip, days = _create_trip_with_days(client, day_count=1)
    trip_id = trip["id"]
    added = client.post(
        f"/trip-days/{days[0]['id']}/places",
        json={"place_id": restaurant.id, "party_size": 2},
        headers=DEVICE,
    )
    assert added.status_code == 201, added.text

    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["dining_total"] == 400_000
    assert budget["days"][0]["places"][0]["fee"] == 200_000
    assert budget["days"][0]["places"][0]["line_total"] == 400_000

    # Trip traveler_count is UI default only — does not rescale existing stops.
    client.put(f"/trips/{trip_id}", json={"traveler_count": 4}, headers=DEVICE)
    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["dining_total"] == 400_000
    assert budget["traveler_count"] == 4

    updated = client.put(
        f"/trip-days/{days[0]['id']}/places/{restaurant.id}",
        json={"custom_entrance_fee": 200_000, "party_size": 4},
        headers=DEVICE,
    )
    assert updated.status_code == 200, updated.text
    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["dining_total"] == 800_000
