from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_returns_app_status() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "app_name": "KitchenCopilot API",
        "status": "ok",
        "environment": "development",
    }
