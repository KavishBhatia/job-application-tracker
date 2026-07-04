import pytest
from fastapi.testclient import TestClient

from src import db
from src.app import app


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.init_db()
    return db_path


@pytest.fixture
def client(temp_db):
    with TestClient(app) as c:
        yield c
