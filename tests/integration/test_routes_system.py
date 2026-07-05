from src.lifecycle import monitor


def test_heartbeat_endpoint_returns_no_content(client):
    response = client.post("/heartbeat")
    assert response.status_code == 204


def test_heartbeat_endpoint_records_a_heartbeat(client, monkeypatch):
    monkeypatch.setattr(monitor, "last_heartbeat", None)
    client.post("/heartbeat")
    assert monitor.last_heartbeat is not None


def test_home_page_omits_keepalive_script_by_default(client, monkeypatch):
    monkeypatch.delenv("AUTO_SHUTDOWN_ON_CLOSE", raising=False)
    response = client.get("/")
    assert "/heartbeat" not in response.text


def test_home_page_includes_keepalive_script_when_enabled(client, monkeypatch):
    monkeypatch.setenv("AUTO_SHUTDOWN_ON_CLOSE", "true")
    response = client.get("/")
    assert "/heartbeat" in response.text
