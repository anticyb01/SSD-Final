from app import create_app


def test_home_returns_ok():
    app = create_app()
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_health_returns_healthy():
    app = create_app()
    client = app.test_client()
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "healthy"}

