"""Public read-only share snapshot."""
from datetime import date, timedelta

DEVICE = {"X-Device-Id": "device-share"}
FUTURE_START_DATE = f"{date.today() + timedelta(days=1)}T00:00:00"


def test_share_link_is_public_and_read_only(client):
    created = client.post(
        "/trips",
        json={"name": "سفر اشتراک", "start_date": FUTURE_START_DATE},
        headers=DEVICE,
    )
    assert created.status_code == 201, created.text
    trip_id = created.json()["id"]

    enabled = client.post(f"/trips/{trip_id}/share", headers=DEVICE)
    assert enabled.status_code == 200, enabled.text
    token = enabled.json()["token"]
    assert token
    assert enabled.json()["path"] == f"/share/{token}"

    public = client.get(f"/share/{token}")
    assert public.status_code == 200, public.text
    body = public.json()
    assert body["trip_name"] == "سفر اشتراک"
    assert "summary" in body
    assert "budget" in body
    assert "notes" in body
    assert "weather" in body

    again = client.post(f"/trips/{trip_id}/share", headers=DEVICE)
    assert again.json()["token"] == token


def test_unknown_share_token_is_404(client):
    response = client.get("/share/not-a-real-token")
    assert response.status_code == 404
