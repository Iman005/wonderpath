"""API checks for adding/removing trip days."""
from datetime import date, timedelta

DEVICE = {"X-Device-Id": "device-a"}
OTHER_DEVICE = {"X-Device-Id": "device-b"}

# Trips reject start dates before today, so this must stay relative to "now".
FUTURE_START_DATE = f"{date.today() + timedelta(days=1)}T00:00:00"


def _create_trip(client):
    response = client.post(
        "/trips", json={"name": "Trip", "start_date": FUTURE_START_DATE}, headers=DEVICE
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _day_numbers(client, trip_id):
    trip = client.get(f"/trips/{trip_id}", headers=DEVICE).json()
    return sorted(day["day_number"] for day in trip["days"])


def test_remove_last_day_drops_the_highest_numbered_day(client):
    trip_id = _create_trip(client)
    client.post(f"/trips/{trip_id}/days/bulk", json={"count": 3}, headers=DEVICE)
    assert _day_numbers(client, trip_id) == [1, 2, 3]

    response = client.delete(f"/trips/{trip_id}/days/last", headers=DEVICE)
    assert response.status_code == 204
    assert _day_numbers(client, trip_id) == [1, 2]

    # Numbering stays contiguous, so adding a day reuses the freed number.
    client.post(f"/trips/{trip_id}/days/bulk", json={"count": 1}, headers=DEVICE)
    assert _day_numbers(client, trip_id) == [1, 2, 3]


def test_remove_middle_day_shifts_later_plans_forward(client, db_session):
    from app.infrastructure.db.models import City, Place, Province

    city = City(name="Shiraz", province=Province(name="Fars"))
    first = Place(name="جای روز ۲", city=city, latitude=29.6, longitude=52.5)
    second = Place(name="جای روز ۳", city=city, latitude=29.7, longitude=52.6)
    db_session.add_all([first, second])
    db_session.commit()

    trip_id = _create_trip(client)
    days = client.post(f"/trips/{trip_id}/days/bulk", json={"count": 3}, headers=DEVICE).json()
    day1, day2, day3 = sorted(days, key=lambda day: day["day_number"])

    assert (
        client.post(
            f"/trip-days/{day2['id']}/places",
            json={"place_id": first.id},
            headers=DEVICE,
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/trip-days/{day3['id']}/places",
            json={"place_id": second.id},
            headers=DEVICE,
        ).status_code
        == 201
    )

    response = client.delete(f"/trips/{trip_id}/days/{day2['id']}", headers=DEVICE)
    assert response.status_code == 204, response.text

    trip = client.get(f"/trips/{trip_id}", headers=DEVICE).json()
    remaining = sorted(trip["days"], key=lambda day: day["day_number"])
    assert [day["day_number"] for day in remaining] == [1, 2]
    assert remaining[0]["id"] == day1["id"]
    assert remaining[1]["id"] == day3["id"]
    assert [place["place_id"] for place in remaining[1]["trip_places"]] == [second.id]
    assert remaining[0]["trip_places"] == []


def test_remove_day_rejects_the_only_remaining_day(client):
    trip_id = _create_trip(client)
    days = client.post(f"/trips/{trip_id}/days/bulk", json={"count": 1}, headers=DEVICE).json()
    response = client.delete(f"/trips/{trip_id}/days/{days[0]['id']}", headers=DEVICE)
    assert response.status_code == 422
    assert _day_numbers(client, trip_id) == [1]


def test_remove_last_day_rejects_empty_trips_and_other_devices(client):
    trip_id = _create_trip(client)
    assert client.delete(f"/trips/{trip_id}/days/last", headers=DEVICE).status_code == 422

    client.post(f"/trips/{trip_id}/days/bulk", json={"count": 1}, headers=DEVICE)
    assert client.delete(f"/trips/{trip_id}/days/last", headers=OTHER_DEVICE).status_code == 403
    assert _day_numbers(client, trip_id) == [1]
