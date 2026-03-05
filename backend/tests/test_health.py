from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}