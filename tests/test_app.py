import os

os.environ.setdefault("IONOS_EMAIL", "mail@example.com")
os.environ.setdefault("IONOS_PASSWORD", "test-password")
os.environ.setdefault("API_KEY", "test-api-key")

from fastapi.testclient import TestClient

from ionos_gateway.app import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_mail_endpoint_requires_api_key() -> None:
    client = TestClient(app)
    response = client.get("/mail/recent")
    assert response.status_code == 401
