"""
API-level checks for the budget surface.

These exist because the budget module's failure modes are wiring bugs
(argument order between router and service, cap not surviving the round
trip) that unit tests with mocked repositories cannot see.
"""
from datetime import date, timedelta

from app.infrastructure.db.models import City, Place, Province

DEVICE = {"X-Device-Id": "device-a"}
OTHER_DEVICE = {"X-Device-Id": "device-b"}

# Trips reject start dates before today, so this must stay relative to "now".
FUTURE_START_DATE = f"{date.today() + timedelta(days=1)}T00:00:00"


def _seed_place(db_session, *, name="Museum", fee=None):
    city = City(name="Shiraz", province=Province(name="Fars"))
    place = Place(
        name=name,
        city=city,
        latitude=29.6,
        longitude=52.5,
        estimated_entrance_fee=fee,
    )
    db_session.add(place)
    db_session.commit()
    return place


def _create_trip(client, **overrides):
    payload = {"name": "Trip", "start_date": FUTURE_START_DATE}
    payload.update(overrides)
    response = client.post("/trips", json=payload, headers=DEVICE)
    assert response.status_code == 201, response.text
    return response.json()


def test_budget_cap_survives_create_and_budget_read(client):
    trip = _create_trip(client, budget_cap=7_000_000)
    assert trip["budget_cap"] == 7_000_000

    budget = client.get(f"/trips/{trip['id']}/budget", headers=DEVICE).json()
    assert budget["budget_cap"] == 7_000_000
    assert budget["grand_total"] == 0
    assert budget["is_over_budget"] is False


def test_budget_cap_update_is_reflected_in_budget(client):
    trip = _create_trip(client)

    updated = client.put(f"/trips/{trip['id']}", json={"budget_cap": 9_000_000}, headers=DEVICE)
    assert updated.status_code == 200
    assert updated.json()["budget_cap"] == 9_000_000

    budget = client.get(f"/trips/{trip['id']}/budget", headers=DEVICE).json()
    assert budget["budget_cap"] == 9_000_000


def test_expense_lifecycle_updates_totals(client):
    trip = _create_trip(client, budget_cap=3_000_000)
    trip_id = trip["id"]

    created = client.post(
        f"/trips/{trip_id}/budget/expenses",
        json={"label": "Hotel", "amount": 2_000_000},
        headers=DEVICE,
    )
    assert created.status_code == 201
    expense_id = created.json()["id"]

    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["expenses_total"] == 2_000_000
    assert budget["grand_total"] == 2_000_000
    assert [item["label"] for item in budget["expenses"]] == ["Hotel"]
    assert budget["is_over_budget"] is False

    client.post(
        f"/trips/{trip_id}/budget/expenses",
        json={"label": "Food", "amount": 1_500_000},
        headers=DEVICE,
    )
    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["is_over_budget"] is True
    assert budget["over_budget_amount"] == 500_000

    # Regression: the router used to pass expense_id where the service
    # expected the device id, so every delete failed with 403.
    deleted = client.delete(f"/trips/{trip_id}/budget/expenses/{expense_id}", headers=DEVICE)
    assert deleted.status_code == 204

    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert [item["label"] for item in budget["expenses"]] == ["Food"]
    assert budget["expenses_total"] == 1_500_000
    assert budget["is_over_budget"] is False


def test_expense_validation_and_ownership(client):
    trip = _create_trip(client)
    trip_id = trip["id"]

    assert client.post(
        f"/trips/{trip_id}/budget/expenses", json={"label": "x", "amount": 0}, headers=DEVICE
    ).status_code == 422
    assert client.post(
        f"/trips/{trip_id}/budget/expenses", json={"label": "   ", "amount": 100}, headers=DEVICE
    ).status_code == 422
    assert client.get(f"/trips/{trip_id}/budget", headers=OTHER_DEVICE).status_code == 403
    assert client.delete(
        f"/trips/{trip_id}/budget/expenses/missing", headers=DEVICE
    ).status_code == 404


def test_budget_exposes_per_place_rows_and_absorbs_a_custom_fee(client, db_session):
    """The budget page edits unknown entrance fees, so it needs days[].places[]."""
    place = _seed_place(db_session, name="Museum", fee=None)
    place_id = place.id
    trip_id = _create_trip(client, budget_cap=1_000_000)["id"]
    day = client.post(f"/trips/{trip_id}/days", json={"day_number": 1}, headers=DEVICE).json()
    client.post(
        f"/trip-days/{day['id']}/places", json={"place_id": place_id}, headers=DEVICE
    )

    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    rows = budget["days"][0]["places"]
    assert [(row["place_id"], row["name"], row["fee"]) for row in rows] == [(place_id, "Museum", None)]
    assert budget["places_with_unknown_fee"] == 1
    assert budget["estimated_total"] == 0

    updated = client.put(
        f"/trip-days/{day['id']}/places/{place_id}",
        json={"custom_entrance_fee": 250_000},
        headers=DEVICE,
    )
    assert updated.status_code == 200

    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["days"][0]["places"][0]["fee"] == 250_000
    assert budget["days"][0]["estimated_total"] == 250_000
    assert budget["estimated_total"] == 250_000
    assert budget["places_with_unknown_fee"] == 0

    # Clearing the fee returns the place to "unknown" rather than zero.
    client.put(
        f"/trip-days/{day['id']}/places/{place_id}",
        json={"custom_entrance_fee": None},
        headers=DEVICE,
    )
    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["days"][0]["places"][0]["fee"] is None
    assert budget["places_with_unknown_fee"] == 1


def test_clearing_the_cap_stops_over_budget_reporting(client):
    trip = _create_trip(client, budget_cap=1_000)
    trip_id = trip["id"]
    client.post(
        f"/trips/{trip_id}/budget/expenses", json={"label": "Food", "amount": 5_000}, headers=DEVICE
    )
    assert client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()["is_over_budget"] is True

    client.put(f"/trips/{trip_id}", json={"budget_cap": None}, headers=DEVICE)
    budget = client.get(f"/trips/{trip_id}/budget", headers=DEVICE).json()
    assert budget["budget_cap"] is None
    assert budget["is_over_budget"] is False
