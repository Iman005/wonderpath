"""Demo hospitality catalog must stay priced so the MVP can be demoed without APIs."""
from app.infrastructure.data.demo_hospitality import DINING_PLACES, LODGING_PLACES


def test_every_hotel_has_a_nightly_rate_and_rooms():
    assert len(LODGING_PLACES) >= 20
    cities = {item["city"] for item in LODGING_PLACES}
    for required in ("تهران", "شیراز", "اصفهان", "یزد", "مشهد"):
        assert required in cities
    for item in LODGING_PLACES:
        assert item["fee"] and item["fee"] > 0
        catalog = item["catalog"]
        assert catalog["is_demo"] is True
        assert catalog["rooms"]
        assert all(room["price"] > 0 for room in catalog["rooms"])


def test_every_eatery_has_a_meal_price_and_menu():
    assert len(DINING_PLACES) >= 20
    categories = {item["category"] for item in DINING_PLACES}
    assert "رستوران" in categories
    assert "کافه" in categories
    for item in DINING_PLACES:
        assert item["fee"] and item["fee"] > 0
        catalog = item["catalog"]
        assert catalog["is_demo"] is True
        assert catalog["menu"]
        assert all(row["price"] > 0 for row in catalog["menu"])
