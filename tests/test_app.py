import json
import sys
from pathlib import Path

import pytest

# Include repository root so we can import mockapi
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mockapi import app as app_module
from mockapi import database


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.init_db()
    app_module.app.config.update({"TESTING": True})
    with app_module.app.test_client() as client:
        yield client


def test_register_and_get(client):
    data = {
        "path": "customer/123",
        "methods": ["GET"],
        "response_type": "json",
        "response_body": json.dumps({"id": 123, "name": "John Doe", "email": "john@doe.com"}),
        "status_code": 200,
    }
    resp = client.post("/register", json=data)
    assert resp.status_code == 201

    resp = client.get("/api/customer/123")
    assert resp.status_code == 200
    assert resp.get_json() == {"id": 123, "name": "John Doe", "email": "john@doe.com"}


def test_deregister(client):
    data = {
        "path": "customer/123",
        "methods": ["GET"],
        "response_type": "json",
        "response_body": json.dumps({"id": 123}),
        "status_code": 200,
    }
    resp = client.post("/register", json=data)
    assert resp.status_code == 201

    resp = client.post("/deregister", json={"path": "customer/123"})
    assert resp.status_code == 200

    resp = client.get("/api/customer/123")
    assert resp.status_code == 404


def test_method_not_allowed(client):
    data = {
        "path": "customer/123",
        "methods": ["GET"],
        "response_type": "json",
        "response_body": json.dumps({"id": 123}),
        "status_code": 200,
    }
    client.post("/register", json=data)

    resp = client.post("/api/customer/123")
    assert resp.status_code == 405


def test_html_responses(client):
    welcome = {
        "path": "welcome",
        "methods": ["GET"],
        "response_type": "html",
        "response_body": "<h1>Welcome</h1>",
        "status_code": 200,
    }
    error = {
        "path": "error",
        "methods": ["GET"],
        "response_type": "html",
        "response_body": "<h1>Internal Server Error</h1>",
        "status_code": 500,
    }

    client.post("/register", json=welcome)
    client.post("/register", json=error)

    resp = client.get("/api/welcome")
    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == "<h1>Welcome</h1>"

    resp = client.get("/api/error")
    assert resp.status_code == 500
    assert resp.get_data(as_text=True) == "<h1>Internal Server Error</h1>"


def test_list_endpoints(client):
    data = {
        "path": "customer/123",
        "methods": ["GET"],
        "response_type": "json",
        "response_body": json.dumps({"id": 123}),
        "status_code": 200,
    }
    client.post("/register", json=data)

    resp = client.get("/endpoints")
    assert resp.status_code == 200
    assert resp.get_json() == [
        {"path": "customer/123", "methods": ["GET"], "status_code": 200}
    ]
