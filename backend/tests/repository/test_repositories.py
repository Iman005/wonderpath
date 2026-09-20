"""Repository tests — run against a real (in-memory SQLite) test database."""
from app.infrastructure.db.models import City, Place, Province, Trip, TripDay, TripPlace
from app.modules.destination.repository import DestinationRepository
from app.modules.trip.repository import TripRepository


def test_get_or_create_province_is_idempotent(db_session):
    repo = DestinationRepository(db_session)

    first = repo.get_or_create_province("فارس")
    second = repo.get_or_create_province("فارس")
    db_session.commit()

    assert first.id == second.id


def test_search_cities_by_name_matches_english_and_province(db_session):
    repo = DestinationRepository(db_session)
    province = repo.get_or_create_province("گیلان")
    province.name_en = "Gilan"
    repo.upsert_city(
        City(name="رشت", name_en="Rasht", province_id=province.id, source_provider_id="ir:gilan:rasht")
    )
    db_session.commit()

    assert repo.search_cities_by_name("Rasht")[0].name == "رشت"
    assert repo.search_cities_by_name("گیلان")[0].name == "رشت"
    repo = DestinationRepository(db_session)
    province = repo.get_or_create_province("فارس")
    repo.upsert_city(City(name="شیراز", province_id=province.id, source_provider_id="seed"))
    db_session.commit()

    results = repo.search_cities_by_name("شیراز")

    assert len(results) == 1
    assert results[0].name == "شیراز"


def test_list_places_for_city_returns_only_that_city(db_session):
    repo = DestinationRepository(db_session)
    province = repo.get_or_create_province("فارس")
    city_a = repo.upsert_city(City(name="شیراز", province_id=province.id))
    city_b = repo.upsert_city(City(name="اصفهان", province_id=province.id))
    repo.upsert_place(Place(name="تخت جمشید", city_id=city_a.id, latitude=1, longitude=1))
    repo.upsert_place(Place(name="نقش جهان", city_id=city_b.id, latitude=2, longitude=2))
    db_session.commit()

    places = repo.list_places_for_city(city_a.id)
    lodging = repo.list_places_for_city(city_a.id, kind="lodging")

    assert len(places) == 1
    assert places[0].name == "تخت جمشید"
    assert lodging == []


def test_trip_repository_cascades_days_and_places(db_session):
    trip_repo = TripRepository(db_session)
    dest_repo = DestinationRepository(db_session)

    province = dest_repo.get_or_create_province("فارس")
    city = dest_repo.upsert_city(City(name="شیراز", province_id=province.id))
    place = dest_repo.upsert_place(Place(name="ارم", city_id=city.id, latitude=1, longitude=1))
    db_session.commit()

    trip = trip_repo.create_trip(Trip(name="سفر شیراز", owner_device_id="device-1"))
    day = trip_repo.create_trip_day(TripDay(trip_id=trip.id, day_number=1))
    trip_repo.create_trip_place(TripPlace(trip_day_id=day.id, place_id=place.id, order_index=0))
    db_session.commit()

    fetched = trip_repo.get_trip(trip.id)

    assert len(fetched.days) == 1
    assert len(fetched.days[0].trip_places) == 1

    trip_repo.delete_trip(fetched)
    db_session.commit()

    assert trip_repo.get_trip(trip.id) is None
    assert trip_repo.get_trip_day(day.id) is None


def test_budget_repository_create_list_delete(db_session):
    from app.infrastructure.db.models import TripExpense
    from app.modules.budget.repository import BudgetRepository

    trip_repo = TripRepository(db_session)
    budget_repo = BudgetRepository(db_session)
    trip = trip_repo.create_trip(Trip(name="سفر یزد", owner_device_id="device-1"))
    db_session.commit()

    created = budget_repo.create_expense(TripExpense(trip_id=trip.id, label="غذا", amount=5_000_000))
    db_session.commit()

    items = budget_repo.list_expenses(trip.id)
    assert len(items) == 1
    assert items[0].label == "غذا"
    assert items[0].amount == 5_000_000

    fetched = budget_repo.get_expense(created.id)
    assert fetched is not None
    budget_repo.delete_expense(fetched)
    db_session.commit()

    assert budget_repo.list_expenses(trip.id) == []
