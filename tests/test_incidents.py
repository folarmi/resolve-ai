import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app()

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_incident_successfully(client):
    response = client.post(
        "/api/incidents",
        json={
            "title": "Production API returning 502 errors",
            "description": "Users are receiving 502 errors.",
            "logs": "upstream connection refused",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Incident created successfully"
    assert data["incident"]["title"] == "Production API returning 502 errors"
    assert data["incident"]["description"] == "Users are receiving 502 errors."
    assert data["incident"]["logs"] == "upstream connection refused"
    assert data["incident"]["status"] == "Open"
    assert data["incident"]["id"]


def test_create_incident_without_title_returns_400(client):
    response = client.post(
        "/api/incidents",
        json={
            "description": "Database connection is failing.",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation failed"
    assert data["details"]["title"] == "Title is required"


def test_create_incident_without_description_returns_400(client):
    response = client.post(
        "/api/incidents",
        json={
            "title": "Database connection failure",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation failed"
    assert data["details"]["description"] == "Description is required"


def test_create_incident_without_json_returns_400(client):
    response = client.post(
        "/api/incidents",
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Request body must contain valid JSON"