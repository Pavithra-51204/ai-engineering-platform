from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness_returns_alive() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_version_returns_application_metadata() -> None:
    response = client.get("/api/v1/version")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "AI Engineering Platform"
    assert data["version"] == "0.1.0"


def test_unknown_endpoint_returns_404() -> None:
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404


def test_health_response_includes_request_id() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.headers.get("x-request-id")
